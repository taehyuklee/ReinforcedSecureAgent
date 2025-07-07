import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_openai import AzureOpenAIEmbeddings

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


# 해당 부분은 AzureOpenAI에서 제공해주고 있는 Embedding Model을 사용하는 케이스
env_api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai_api_base = os.getenv("AZURE_OPENAI_API_ENDPOINT")
deployment_name = os.getenv("DEPLOYMENT_NAME")

# Qdrant 서버 연결

embeddings = AzureOpenAIEmbeddings(
    openai_api_type="azure",
    azure_endpoint=openai_api_base,
    openai_api_key=env_api_key,
    chunk_size=1000,
    openai_api_version="2024-02-15-preview",
    model="text-embedding-3-small"
)

# LangChain Qdrant VectorStore 생성
vector_store = QdrantVectorStore(
    client=qdrant,
    collection_name="nginx_log2",
    embedding=embeddings
)


def get_nginx_vector_store():
    global vector_store
    return vector_store
