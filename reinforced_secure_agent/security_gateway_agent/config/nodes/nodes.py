# from langchain.agents import create_tool_calling_agent # 해당 method는 bind_tools를 가져오고 있다. (어차피 AzureOpenAI는 안됨)

from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph import MessagesState
from sentence_transformers import SentenceTransformer

from config.db_config.db_config import get_caching_store

# ========== Agent Executor 생성 ==========
# system_message = build_system_message()
# agent = create_react_agent(llm=llm, tools=tools) # 이걸로 변경 예정
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# agent를 initialize_agent method로 수동 실행 (llm bind tools 말고)
# agent_executor.run({"안녕 넌 누구니? 인터넷 검색해서 이태혁이라는 사람을 검색해줄 수 있어?"})

# Embedding 모델 설정 (로컬)
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)


# Vector Store 설정
def retriever_node():
    return get_caching_store()


# Agent Node
# def agent(state: MessagesState):
#     messages = state["messages"]
#     response = llm.invoke(messages)
#
#     messages.append(response.output)
#
#     print(response.output)
#
#     while response.tool_calls:
#         tool_results = []
#         for call in response.tool_calls:
#             result = handle_tool_call(call)
#             tool_results.append(result)
#             messages.append(result)  # tool result도 messages에 추가
#
#         print(messages)
#         # tool 실행 후 다시 LLM에게 reasoning 요청
#         response = llm.invoke(messages)
#         messages.append(response)
#
#     return {"messages": messages}

def agent(state: MessagesState):
    messages = state["messages"]

    # LangGraph의 MessagesState는 dict, AgentExecutor는 dict(input=input) 형태 필요
    last_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])

    result = agent_executor.invoke({"input": last_message})

    return {"messages": messages + [result["output"]]}


# 상태 전환 로직
def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    return 'tools' if getattr(last_message, "tool_calls", None) else 'end'
