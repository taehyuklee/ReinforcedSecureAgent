import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent

from config.tools.tools import *


# ENV 설정 및 Qdrant 연결
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

# Azure OpenAI 설정
env_api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai_api_base = os.getenv("AZURE_OPENAI_API_ENDPOINT")
deployment_name = os.getenv("DEPLOYMENT_NAME")

# Prompt & 모델 설정
llm = AzureChatOpenAI(
    openai_api_key=env_api_key,
    azure_endpoint=openai_api_base,
    deployment_name=deployment_name,
    openai_api_version="2024-02-15-preview"
)

# rate_limit_check_tool
tools = [suspicious_pattern_detector, think_aloud, web_search_tool, base64_decode_tool, unicode_decode_tool,
         split_string, join_strings]


config = {
    'configurable': {
        'thread_id': 'block_hacking'
    }
}

agent_graph = create_react_agent(model=llm, tools=tools)
