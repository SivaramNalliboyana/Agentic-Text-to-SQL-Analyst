import sqlite3
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from code_node import generate_sql
from executor_node import execute_sql

# Define states
class AgentState(TypedDict):
    question: str
    sql_query: str
    db_result: Optional[list]
    error: Optional[str]
    attempts: int

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
    if state["error"] is None or state["attempts"] >= 3:
        return "end"
    else:
        return "retry"

# Build langgraph
workflow = StateGraph(AgentState)
workflow.add_node("coder", sql_generator_node)
workflow.add_node("executor", sql_executor_node)

workflow.set_entry_point("coder")
workflow.add_edge("coder", "executor")

workflow.add_conditional_edges(
    "executor",
    should_continue,
    {
        "retry": "coder",
        "end": END
    }
)

app = workflow.compile()

if __name__ == "__main__":
    inputs = {"question": "What is the price of the Laptop?", "attempts": 0}
    final_state = app.invoke(inputs)

    print("\n--- FINAL RESULT ---")
    print(f"Question: {final_state['question']}")
    print(f"SQL Used: {final_state['sql_query']}")
    print(f"Data Found: {final_state['db_result']}")