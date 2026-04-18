import chromadb
from embeddings import get_embedding_function

def get_retriever(collection_name="code_knowledge", top_k=5):
    from config import ZHIPUAI_API_KEY, CHROMA_DB_PATH
    embedding_fn = get_embedding_function(ZHIPUAI_API_KEY, use_local=True)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name=collection_name, embedding_function=embedding_fn)
    
    def retrieve(query):
        results = collection.query(query_texts=[query], n_results=top_k)
        return results['documents'][0], results['metadatas'][0]
    return retrieve