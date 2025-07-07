import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

# ENV 설정 및 Qdrant 연결
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

# Qdrant 서버 연결
qdrant = QdrantClient(host="localhost", port=6333)


# SentenceTransformer 모델 직접 로드
model = SentenceTransformer('all-MiniLM-L6-v2')

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",  # 여기에 모델 이름 직접
    model_kwargs={"device": "cpu"}  # or "cuda" 가능
)


# LangChain Qdrant VectorStore 생성
caching_store = QdrantVectorStore(
    client=qdrant,
    collection_name="caching",
    embedding=embeddings
)


def get_caching_store():
    global caching_store
    return caching_store

