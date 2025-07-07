import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from config.prompts.prompts import build_system_prompt, build_final_secure_prompt


from config.tools.acting_tools import *
from config.tools.summary_tools import *
from langchain_core.messages.utils import (
    trim_messages,
    count_tokens_approximately
)

from langchain_core.messages import RemoveMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain_core.messages import ToolMessage


summary_prompt = build_final_secure_prompt()
build_system_prompt = build_system_prompt()


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


def count_message_types(messages):
    human_count = sum(1 for m in messages if isinstance(m, HumanMessage))
    ai_count = sum(1 for m in messages if isinstance(m, AIMessage))
    tool_count = sum(1 for m in messages if isinstance(m, ToolMessage))
    system_count = sum(1 for m in messages if isinstance(m, SystemMessage))

    print(f" HumanMessage: {human_count}개")
    print(f" AIMessage: {ai_count}개")
    print(f" ToolMessage: {tool_count}개")
    print(f" SystemMessage: {system_count}개")

    return human_count, ai_count, tool_count


def trimming_messages(state):
    print("====================== trimming중입니다 =====================")
    original_messages = state["messages"]

    total_tokens = count_tokens_approximately(original_messages)

    if total_tokens <= 12000:
        print("trimming 없이 원본 메시지 사용 (총 토큰 수:", total_tokens, ")")
        trimmed_messages = original_messages
    else:
        trimmed_messages = trim_messages(
            state["messages"],
            strategy="last",
            token_counter=count_tokens_approximately,
            max_tokens=10000,
            start_on="human",
            end_on=("human", "tool"),
        )
        print("trimming 해서 사용 (총 토큰 수:", trimmed_messages, ")")

        # HumanMessage 보장
        if not any(isinstance(m, HumanMessage) for m in trimmed_messages):
            last_human = next((m for m in reversed(original_messages) if isinstance(m, HumanMessage)), None)
            if last_human:
                trimmed_messages.insert(0, last_human)
            else:
                trimmed_messages.insert(0, HumanMessage(content=build_final_secure_prompt()))

        # SystemMessage 보장
        if not any(isinstance(m, SystemMessage) for m in trimmed_messages):
            last_system = next((m for m in reversed(state["messages"]) if isinstance(m, SystemMessage)), None)
            if last_system:
                trimmed_messages.insert(0, last_system)
            else:
                trimmed_messages.insert(0, SystemMessage(content=build_system_prompt))

        # 필터: 맨 앞에 tool 메시지가 오는 경우 제거
        while trimmed_messages and isinstance(trimmed_messages[0], ToolMessage):
            trimmed_messages.pop(0)

    print("최종 메시지 수:", len(trimmed_messages))
    print("최종 token 수:", count_tokens_approximately(trimmed_messages))
    count_message_types(trimmed_messages)

    return {
        "messages": [RemoveMessage(REMOVE_ALL_MESSAGES)] + trimmed_messages,
        "llm_input_messages": trimmed_messages
    }


tools = [fetch_logs_from_collector, check_collector_queue_size, read_recent_summary_lines, write_summary_log, \
         summarize_logs_tool, add_to_blacklist, classify_logs_with_llm, caching_for_few_shot, get_message_length, \
         think_aloud, web_search_tool]


config = {
    'configurable': {
        'thread_id': 'monitoring'
    },
    'recursion_limit': 200
}

# 이전에 bind_tools해서 should Continue했던거랑 같은 graph가 나옴
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

agent_graph = create_react_agent(model=llm, tools=tools, pre_model_hook=trimming_messages, checkpointer=checkpointer)
