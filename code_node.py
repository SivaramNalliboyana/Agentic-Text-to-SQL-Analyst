import chromadb
from langchain_ollama import OllamaLLM, OllamaEmbeddings

from store_schema_embeddings import embeddings_model

# Connect to the chromdb embeddings
client = chromadb.PersistentClient(path="./chroma_storage")
collection = client.get_collection(name="sql_schema")

llm = OllamaLLM(model="llama3.2", temperature=0)  # Temperature defines how much freedom model has to be creative

def generate_sql(user_question):
    # Ask db for correct schema depending on question
    results = collection.query(query_texts=[user_question], n_results=1)

    # Get the correct schema
    relevant_schema = results['documents'][0][0]

    prompt = f"""
    ### ROLE
    You are a professional SQL Developer
    
    ## CONTEXT
    Use the following table schema to write the SQL query:
    {relevant_schema}
    
    ## TASK
    Generate a SQL query to answer this question : "{user_question}"
    
    ### CONSTRAINTS
    - Return ONLY the SQL code.
    - Do not include backticks (```) or the world 'sql'
    - Do not explain the code
    
    SQL:"""

    # Invole llama
    sql_query = llm.invoke(prompt)
    return sql_query.strip(), relevant_schema


if __name__ == "__main__":
    test_question = "What is the price of a Laptop?"
    query, schema = generate_sql(test_question)

    print(f"Question: {test_question}")
    print(f"RAG suggested: {schema}")
    print(f"Llama's SQL: {query}")