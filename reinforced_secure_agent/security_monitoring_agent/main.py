# from config.graph.graph_builder import build_graph
import time

from fastapi import FastAPI
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage


from config.prompts.prompts import build_system_prompt, build_final_secure_prompt
from config.agent_config.agent_config import agent_graph, config

app = FastAPI()

# final_graph = build_graph()

summary_prompt = build_final_secure_prompt()
build_system_prompt = build_system_prompt()


def debugging_stream(secure_prompt: str, system_message: str):
    start = time.time()
    for chunk in agent_graph.stream(
            {'messages': [HumanMessage(content=secure_prompt), SystemMessage(content=system_message)]},
            config=config,
            stream_mode='values'):
        messages = chunk.get('messages', [])
        if messages:
            messages[-1].pretty_print()
        else:
            print("[경고] chunk에 messages가 비어있습니다:", chunk)
    end = time.time()
    print(f"llm response search 시간: {end - start:.4f}초")


def debugging_stream_with_retry(secure_prompt: str, system_message: str, max_retries=5, initial_delay=2):
    delay = initial_delay
    for i in range(max_retries):
        try:
            debugging_stream(secure_prompt, system_message)
            return  # 성공 시 종료
        except Exception as e:
            msg = str(e).lower()
            print(f"[Attempt {i + 1}/{max_retries}] 예외 발생: {e}")

            # Azure Content Filter 에러 처리
            if "azure has not provided the response due to a content filter" in msg:
                print("[ContentFilterBlocked] 민감한 응답 내용이 필터에 차단됨 → Prompt 완화 또는 구조 변경 필요")
                # Prompt를 완화하거나 에러 로깅 후 재시도
                if i == max_retries - 1:
                    raise ValueError("Content Filter에 의해 반복 차단됨. prompt를 완화하거나 예시를 수정하세요.")
                time.sleep(delay)
                delay *= 2

            elif "rate limit" in msg or "429" in msg:
                print(f"[RateLimitError] {e} → {delay}초 대기 후 재시도")
                time.sleep(delay)
                delay *= 2

            elif "tool_call_id" in msg:
                print(f"[ToolCallIDError] {e} → 누락된 tool 응답 메시지 처리 시도")
                try:
                    current_messages = agent_graph.get_state(config).values['messages']
                    if current_messages:
                        last_msg = current_messages[-1]
                        agent_graph.update_state(config, {'message': RemoveMessage(id=last_msg.id)})
                        print("[ToolCallIDError] 마지막 메시지를 삭제했습니다.")
                    else:
                        print("[ToolCallIDError] 삭제할 메시지가 없습니다.")
                except Exception as inner_e:
                    print(f"[ToolCallIDError 처리 중 에러] {inner_e}")
                time.sleep(delay)
                delay *= 2

            else:
                print(f"[UnknownError] {e} → 종료")
                raise e


# 실제 호출부에서 기존 debugging_stream 대신 아래 함수 호출하도록 변경

while True:
    debugging_stream_with_retry(summary_prompt, build_system_prompt)

