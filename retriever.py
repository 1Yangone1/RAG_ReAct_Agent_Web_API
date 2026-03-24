import chromadb
from chromadb.utils import embedding_functions

def get_retriever(collection_name="code_knowledge", top_k=5):
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name=collection_name, embedding_function=embedding_fn)
    
    def retrieve(query):
        results = collection.query(query_texts=[query], n_results=top_k)
        return results['documents'][0], results['metadatas'][0]
    return retrieve