import re
from typing import List

import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools.retriever import create_retriever_tool

from config.agent_config.agent_config import llm
from config.db_config.db_config import caching_store, vector_store
from config.tools import *
from config.tools.manual_tool.debugging_tool import debug_check_messages


@tool
def block_ip_via_api(ip: str) -> str:
    """
    주어진 IP를 리눅스 서버에서 iptables 명령어로 차단하는 API를 호출합니다.

    Args:
        ip (str): 차단할 IP 주소

    Returns:
        str: 차단 결과 메시지
    """

    # 서버에 IP 차단 요청을 보낼 API 엔드포인트 URL (예시)
    api_url = "http://localhost:8000/block_ip"

    # curl 커맨드 형식으로 실행 (실제론 requests 등으로 대체 가능)
    import subprocess

    cmd = [
        "curl",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", f'{{"ip": "{ip}"}}',
        api_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"IP {ip} 차단 요청 성공: {result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return f"IP {ip} 차단 요청 실패: {e.stderr.strip()}"


@tool
def explain_log(log_line: str) -> str:
    """
    한 줄의 로그를 사람의 언어로 해석해줍니다. (LLM 기반 설명)

    Args:
        log_line (str): 로그 한 줄

    Returns:
        str: 자연어 설명
    """

    prompt = f"""다음 로그 한 줄을 사람이 이해할 수 있도록 설명해주세요:

    {log_line}

    설명:"""

    # 예시용 LLM 응답 호출 (실제론 langchain LLM or OpenAI API 사용)
    return llm.invoke(prompt)


@tool
def log_threat_inference(log_text: str) -> str:
    """
    주어진 로그 텍스트에서 보안 위협 가능성을 자연어로 추론합니다.
    LLM이 활용되어 어떤 공격 가능성이 있는지 요약합니다.

    Args:
        log_text (str): 에러 로그 또는 웹 로그 전체

    Returns:
        str: 추정된 위협 종류 및 원인 해석 (예: RCE 가능성, 취약한 엔드포인트 등)
    """

    prompt = f"""아래 로그를 보고, 보안 관점에서 어떤 위협이 숨어있을 수 있는지 설명해주세요.

    로그:
    {log_text}

    답변:"""

    # 아래는 Pseudo 코드: 실제론 OpenAI API 또는 LangChain LLM 사용
    # from openai import OpenAI
    response = llm.invoke(prompt)  # 또는 LangChain LLM.invoke(prompt)
    return response


retriever = vector_store.as_retriever(search_kwargs={'k': 3})

retriever_tool = create_retriever_tool(
    retriever=retriever,
    name='real_log_retriever',
    description='해당 Vector database는 nginx 로그를 가지고 있습니다.'
)


@tool
def rate_limit_check_tool(ip: str, log_lines: list[str]) -> str:
    """
    특정 IP의 과도한 요청을 감지합니다.

    Args:
        ip (str): 요청을 보낸 IP 주소
        log_lines (list[str]): Nginx 등 access log 라인 리스트

    Returns:
        str: 의심 여부 결과
    """
    count = sum(1 for line in log_lines if ip in line)
    if count > 100:  # 예: 5분간 100회 이상
        return f"{ip}: 과도한 요청 감지됨 (DoS 의심)"
    return f"{ip}: 정상 요청"


@tool(description="NGINX 로그 중 공격에 해당되는 ip를 차단합니다.")
def add_to_blacklist(ip: List[str]) -> str:
    """
    지정된 IP 주소 목록을 Gateway의 블랙리스트에 등록하여 접근을 차단합니다.

    Args:
        ip (List[str]): 차단 대상이 될 IP 주소 목록

    Returns:
        str: 성공 시 'Success', 실패 시 에러 메시지
    """
    debug_check_messages()

    url = "http://localhost:8000/gateway/blacklist"  # Gateway Collector API
    try:
        response = requests.post(url, json={"ipList": ip}, timeout=5)
        if response.status_code == 200:
            return "Success"
        else:
            return f"Failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def check_whitelist(ip: str, path: str) -> bool:
    """요청이 화이트리스트에 존재하는지 확인하여 신속히 allow 가능"""
    ...


# Web Search Tool
@tool
def web_search_tool(query: str) -> str:
    """
    검색 쿼리를 받아서 웹에서 관련 정보를 찾아 반환합니다.
    """
    duck_search = DuckDuckGoSearchRun()
    return duck_search.run(query)


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


@tool(description="NGINX 로그 중 LLM이 악성 여부를 판단해서 예시 포맷으로 변환합니다.")
def classify_logs_with_llm(logs: List[str]) -> str:
    """
    LLM을 활용하여 웹 로그에서 악의적인 요청 여부를 판단하고,
    "block"으로 판단된 로그만 지정된 형식으로 반환합니다.

    주의: "allow"로 판단된 요청은 어떤 경우에도 출력하지 않으며,
    오직 "block" 응답만 예시로 포맷하여 리턴합니다.
    """
    debug_check_messages()

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """\
            너는 웹 보안 분석 전문가야. 아래는 HTTP 로그야.
            각 로그가 공격으로 의심되면 다음 형식으로 응답해:
            
            요청 내용:
            <요청 로그>
            응답:
            {{ "action": "block" }}
            이유:
            <판단 사유>
            
            반드시 "요청 내용:"과 실제 로그를 그대로 포함해. 로그가 없거나 생략된 응답은 잘못된 응답으로 간주될 수 있어.
            단, 공격이 아니라고 판단되면 {{ "action": "allow" }} 형식으로만 응답하고, 이 경우는 출력하지 마.
            중요: "예시 1:", "---" 같은 포맷 구분선은 절대 출력하지 마. 내가 따로 붙일 거야.
            """),
        ("human", "{log}")
    ])

    chain = prompt_template | llm | StrOutputParser()

    result_texts = []
    count = 1  # 예시 N 번호
    for log_entry in logs:
        try:
            output = chain.invoke({"log": log_entry}).strip()
            if '"action": "block"' in output and "요청 내용:" in output:
                formatted = f"---\n예시 {count}:\n{output}\n"
                result_texts.append(formatted)
                count += 1
            # allow 응답은 무시
        except Exception as e:
            formatted_error = (
                f"---\n예시 {count}:\n요청 내용:\n{log_entry}\n"
                f"응답:\n{{ \"action\": \"block\" }}\n이유:\n분석 중 오류 발생: {str(e)}\n"
            )
            result_texts.append(formatted_error)
            count += 1

    return "\n".join(result_texts)


# 캐싱용 툴 정의 (잘라서 캐싱으로 넣을 툴)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


@tool(description="LLM에서 생성된 예시들을 벡터 저장소에 임베딩하고 저장합니다. 예시는 '---'로 구분되어야 합니다.")
def caching_for_few_shot(raw_output: str) -> str:
    """
    LLM의 분석 결과 문자열(raw_output)을 받아 Qdrant 벡터 저장소에 저장합니다.

    처리 단계:
    1. 입력 문자열은 '---' 기준으로 분리된 여러 개의 예시로 구성되어 있어야 합니다.
    2. 각 예시는 LangChain Document 객체로 변환됩니다.
    3. 예시가 너무 길 경우 RecursiveCharacterTextSplitter로 추가 분할됩니다.
    4. 최종적으로 분할된 문서들이 임베딩되어 Qdrant에 저장됩니다.

    매개변수:
    - raw_output (str): LLM이 출력한 여러 예시들을 포함한 문자열. 각 예시는 '---'로 구분되어야 하며, 아래 형식에 따라야 합니다:

        예시 형식:
        ---
        예시 N:
        요청 내용:
        <요청 로그 또는 HTTP 요청 원문>
        응답:
        { "action": "block" } 또는 { "action": "allow" }
        이유:
        <LLM이 판단한 사유>
        ---

        또는 JSON 바디가 포함될 수 있음:
        ---
        예시 N:
        요청 내용:
        POST /login HTTP/1.1
        Host: example.com
        Content-Type: application/json

        {
          "username": "' OR '1'='1",
          "password": "' OR '1'='1"
        }

        응답:
        { "action": "block" }
        이유:
        SQL Injection 공격으로 판단됨
        ---

    반환값:
    - str: 저장된 문서의 수를 포함한 성공 메시지. 예: "총 23개의 문서를 Qdrant에 저장 완료했습니다."
    """

    debug_check_messages()
    # --- Step 1: '---' 기준으로 쪼개기
    raw_examples = re.split(r'\n*---\n*', raw_output)

    # --- Step 2: 빈 내용 제외 후 Document 객체로 변환
    docs = [Document(page_content=ex.strip()) for ex in raw_examples if ex.strip()]

    if not docs:
        return "처리할 예시가 없습니다."

    # --- Step 3: 문서 분할기 설정 (너무 긴 경우 대비)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
        separators=["\n\n예시", "\n\n", "\n", " "]
    )
    split_docs = splitter.split_documents(docs)

    # --- Step 4: 벡터 저장소에 batch 업로드
    BATCH_SIZE = 5000
    for i in range(0, len(split_docs), BATCH_SIZE):
        batch = split_docs[i:i + BATCH_SIZE]
        caching_store.add_documents(batch)

    return f"총 {len(split_docs)}개의 문서를 Qdrant에 저장 완료했습니다."


@tool(description="현재 LangGraph 내부 상태에 저장된 메시지의 총 개수를 반환합니다.")
def get_message_length() -> int:
    """
    LangGraph 내부 상태에서 현재 저장되어 있는 메시지 개수를 반환합니다.

    이 함수는 메시지 수가 지정된 임계값을 초과했는지 판단할 때 사용됩니다.
    예를 들어, 메시지 수가 너무 많으면 토큰 초과를 방지하기 위해 메시지를 제거하거나 요약하는 등의 처리가 필요합니다.

    Returns:
        int: 현재 상태에 저장된 전체 메시지 개수.
    """
    debug_check_messages()
    from config.agent_config.agent_config import agent_graph, config

    current_message_list = agent_graph.get_state(config).values['messages']
    total_messages = len(current_message_list)

    return total_messages
