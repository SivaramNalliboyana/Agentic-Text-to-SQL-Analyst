import chromadb
from langchain_ollama import OllamaEmbeddings
from ollama import embeddings

# Connect to chromdb
client = chromadb.PersistentClient(path="./chroma_storage")  # Creates folder on computer

# Create the embedding model which translates text into embeddings
embeddings_model = OllamaEmbeddings(model="nomic-embed-text")

# Create collection
#  = Like a specific bookshelf for sql info
collection = client.get_or_create_collection(name="sql_schema")


# Define table info
# Describe table name , columns and what its used for
tables_to_index = [
    {
        "id" : "customers",
        "description" : "Table: customers. Columns: id, name, city. Use this table for customer names, identity and their locations."
    },
    {
        "id": "products",
        "description": "Table: products. Columns: id, name, price, category. Use this table for item names, how much things cost, and grouping by category"
    }
]

# Add table to memory
for table in tables_to_index:
    # This turns text description into numbers ( vectors )
    collection.add(
        ids=[table["id"]],
        documents=[table["description"]]
    )
