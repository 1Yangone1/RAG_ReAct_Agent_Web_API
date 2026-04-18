from zhipuai import ZhipuAI
from sentence_transformers import SentenceTransformer

class ZhipuEmbeddingFunction:
    """Chroma-compatible embedding function backed by ZhipuAI."""
    def __init__(self, api_key: str, model: str = "embedding-3"):
        self.client = ZhipuAI(api_key=api_key)
        self.model = model

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]

        vectors = []
        for text in input:
            resp = self.client.embeddings.create(model=self.model, input=text)
            vectors.append(resp.data[0].embedding)
        return vectors

    def embed_query(self, input):
        return self.__call__(input)

    def embed_documents(self, input):
        return self.__call__(input)

    def name(self) -> str:
        # Newer Chroma versions use this to validate EF compatibility.
        return "zhipu"


class LocalEmbeddingFunction:
    """本地 sentence-transformers embedding 函数"""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        # sentence-transformers 的 encode 直接返回向量列表
        vectors = self.model.encode(input).tolist()
        return vectors
    
    def embed_query(self, input):
        return self.__call__(input)
    
    def embed_documents(self, input):
        return self.__call__(input)
    
    def name(self) -> str:
        return "local_sentence_transformer"

def get_embedding_function(zhipu_api_key: str, use_local: bool = False):
    if use_local or not zhipu_api_key:
        # 如果明确要求本地，或者没有 API key，就用本地
        print("使用本地 sentence-transformers 模型生成 embedding")
        return LocalEmbeddingFunction()
    else:
        # 否则尝试使用智谱 API
        if zhipu_api_key:
            return ZhipuEmbeddingFunction(api_key=zhipu_api_key)
        raise RuntimeError("未检测到 ZHIPUAI_API_KEY，且未选择本地模型。")