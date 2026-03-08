import sqlite3
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from code_node import generate_sql, llm
from executor_node import execute_sql

# Define states
class AgentState(TypedDict):
    question: str
    sql_query: str
    db_result: Optional[list]
    error: Optional[str]
    attempts: int
    final_answer: str

def sql_generator_node(state: AgentState):
    query, schema = generate_sql(state['question'])
    return {"sql_query": query, "attempts": state['attempts'] + 1}

def sql_executor_node(state: AgentState):
    result = execute_sql(state['sql_query'])
    if result["status"] == "success":
        return {"db_result": result["data"], "error": None}
    else:
        return {"error": result["message"]}

def should_continue(state: AgentState):
    if state["error"] is None:
        return "summarize"  # Go to Analyst
    elif state["attempts"] >= 3:
        return "end"  # Give up
    else:
        return "retry"  # Back to Coder


def analyst_node(state: AgentState):
    # We ask Llama to explain the data
    prompt = f"""
    User Question: {state['question']}
    Database Result: {state['db_result']}

    Based on the data above, write a natural-sounding answer to the user. 
    Be concise. Don't mention 'SQL' or 'Database'.
    """

    answer = llm.invoke(prompt)
    return {"final_answer": answer.strip()}

# Build langgraph
workflow = StateGraph(AgentState)
workflow.add_node("coder", sql_generator_node)
workflow.add_node("executor", sql_executor_node)
workflow.add_node("analyst", analyst_node)

workflow.set_entry_point("coder")
workflow.add_edge("coder", "executor")
workflow.add_edge("analyst", END)

workflow.add_conditional_edges(
    "executor",
    should_continue,
    {
        "retry": "coder",
        "summarize": "analyst",
        "end": END
    }
)

app = workflow.compile()

if __name__ == "__main__":
    inputs = {"question": "What is the most expensive item in the shop?", "attempts": 0}

    # 2. Start the Graph and wait for it to finish
    final_state = app.invoke(inputs)


    # 3. This is the part the 'Analyst' wrote!
    print(f"ANSWER: {final_state.get('final_answer')}")

    print("\n--- Technical Audit ---")
    print(f"SQL used: {final_state['sql_query']}")
    print(f"Raw Data: {final_state['db_result']}")
    print("=" * 30)
