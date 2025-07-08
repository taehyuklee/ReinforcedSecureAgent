from config.nodes.nodes import retriever_node
from config.agent_config.agent_config import agent_graph, config, llm

from config.prompts.prompts import build_secure_prompt, build_agent_human_prompt, build_agent_system_message, test_prompt \
    ,build_llm_system_prompt, build_llm_prompt
from fastapi import FastAPI, Request
import json
from typing import List
import httpx
from starlette.responses import Response, JSONResponse
from config.memory.singleton import WhiteList, Blacklist
from router.acl_router import router
import uvicorn

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import time  # RAG 성능 측정을 위한 time import

app = FastAPI()

# Router 등록
app.include_router(router)

# HTTP 클라이언트 설정 (https는 일단 껐습니다 verify)
client = httpx.AsyncClient(timeout=120.0, verify=False)

whitelist = WhiteList()
blacklist = Blacklist()


def get_few_shot_from_db(str_full_context: str):

    start = time.time()

    # few shot을 위한 예제 불러오기
    retriever = retriever_node().as_retriever(
        search_kwargs={
            "k": 3,  # 여러 개 받아서 confidence 기반 판단 가능
            # "score_threshold": 0.5
            # "search_params": {
            #     "hnsw_ef": 32,  # 기본 64 ~ 128 / 낮추면 속도↑ 정확도↓
            #     "exact": False  # True는 느리지만 완전 탐색 (쓰지 않는게 좋음)
            # }
        }
    )

    query = f'{str_full_context}'
    results = retriever.invoke(query)

    # print(results)

    end = time.time()
    print(f"rag search 시간: {end - start:.4f}초")

    return format_few_shot_examples([r.page_content for r in results])


# --- 형식의 few-shot 예시 문자열 자동 생성
def format_few_shot_examples(docs: List[str]) -> str:
    formatted = []
    for idx, doc in enumerate(docs, start=1):
        formatted.append(f"""\n{doc.strip()}\n---""")
    return "\n\n".join(formatted)


def debugging_stream(secure_prompt: str, system_message: str):
    start = time.time()
    for chunk in agent_graph.stream(
            {'messages': [HumanMessage(content=secure_prompt), SystemMessage(content=system_message)]}, config=config,
            stream_mode='values'):
        chunk['messages'][-1].pretty_print()
    end = time.time()
    print(f"llm response search 시간: {end - start:.4f}초")


async def routing_url(request: Request, url: str, request_body):
    proxied_response = await client.request(
        method=request.method,
        url=url + request.url.path,
        headers=request.headers.raw,
        content=request_body
    )
    return Response(
        content=proxied_response.content,
        status_code=proxied_response.status_code,
        headers=dict(proxied_response.headers)
    )


@app.middleware("http")
async def secure_agent_gateway(request: Request, call_next):
    global whitelist

    request_body = await request.body()
    request.state.body = request_body

    if request.url.path == '/gateway/whitelist' or request.url.path == '/gateway/blacklist':
        return await call_next(request)

    full_context = {
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "body": request_body.decode("utf-8", errors="ignore")
    }

    # JSON 직렬화로 구조 유지
    str_full_context = json.dumps(full_context, ensure_ascii=False, indent=2)

    secure_prompt = build_llm_prompt(str_full_context)
    system_message = build_llm_system_prompt()

    # print(secure_prompt)

    free_pass_ip = whitelist.get_whitelist()
    ban_ip = blacklist.get_blacklist()

    # 추후에 white list관련해서
    action_result = 'allow'

    if(str(request.client.host)) in ban_ip:
        action_result = 'block'
    elif (str(request.client.host)) not in free_pass_ip:
        # Agent에게 판단 요청

        decision = await llm.ainvoke([
            SystemMessage(content=system_message),
            HumanMessage(content=secure_prompt)
        ])

        # print(decision)

        result = json.loads(decision.content)
        action_result = result['action']

    print(action_result)
    if action_result == "block":
        return JSONResponse(content={"detail": "보안상 이슈 발생"}, status_code=403)
    elif action_result == "review":

        print("review가 필요 합니다.")
        few_shot_examples = get_few_shot_from_db(str_full_context)
        secure_prompt = build_agent_human_prompt(few_shot_examples, str_full_context)

        # print(secure_prompt)
        system_message = build_agent_system_message()

        # debugging_stream(secure_prompt, system_message)
        decision = await agent_graph.ainvoke(
            {'messages': [HumanMessage(content=secure_prompt), SystemMessage(content=system_message)]}, config=config
        )
        result = json.loads(decision['messages'][-1].content)
        action_result = result['action']

        print(action_result)
        if action_result == "block":
            return JSONResponse(content={"detail": "보안상 이슈 발생"}, status_code=403)

    return await routing_url(request, "routing_ip/path", request_body)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
