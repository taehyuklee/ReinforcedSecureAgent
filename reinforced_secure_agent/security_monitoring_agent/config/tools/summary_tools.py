# 요약된 결과를 summary_log.txt로 저장
from datetime import datetime
import os
import json
from typing import List

import requests

from config.agent_config.agent_config import llm
from config.prompts.prompts import build_log_summary_prompt
from config.tools.manual_tool.debugging_tool import debug_check_messages
from langchain_community.tools import DuckDuckGoSearchRun

from config.tools import *

# 기존 summary 파일 읽기
SUMMARY_LOG_PATH = "D:/github_repo/new_git/SK-Inc-CnC/AIPlatform/ai_dev_agent/langgraph_secure_agent/security_monitoring_agent/summary_file/summary_log.txt"


# SUMMARY_LOG_PATH = "D:/github/SK-Inc-CnC/AIPlatform/security_monitoring_agent/summary_file/summary_log.txt"


@tool(description="Collector로부터 최신 로그를 가져옵니다.")
def fetch_logs_from_collector(limit: int = 1000):
    """
    Collector 서버로부터 최신 로그 데이터를 조회하는 도구 함수입니다.

    Args:
        limit (int): 가져올 로그의 최대 개수 (기본값: 1000)

    Returns:
        List[str]: 문자열 형태의 로그 리스트.
                   응답 형식이 JSON 배열이 아닐 경우 빈 리스트를 반환합니다.

    예외:
        요청 중 오류가 발생하거나 응답 형식이 잘못된 경우,
        오류 메시지를 출력하고 빈 리스트를 반환합니다.
    """

    debug_check_messages()
    url = "http://localhost:9000/new-logs"  # Collector API 주소
    try:
        response = requests.get(url, params={"limit": limit}, timeout=5)
        # 응답이 string 형태의 JSON 배열이라면 예: '["log1", "log2", "log3"]'
        raw_data = response.text.strip()
        if raw_data.startswith("[") and raw_data.endswith("]"):
            logs = json.loads(raw_data)
            return logs  # 리스트 형태로 반환
        else:
            print("Invalid response format:", raw_data)
            return []
    except Exception as e:
        print("Error fetching logs:", e)
        return []


@tool(description="Collector의 로그 처리 대기열(queue)에 남아 있는 로그 개수를 반환합니다.")
def check_collector_queue_size() -> int:
    """
    Collector 서버의 로그 대기열 크기를 확인하는 도구 함수입니다.

    Returns:
        int: 현재 Collector의 로그 queue에 쌓여 있는 로그 개수.
             요청 실패 또는 응답이 숫자가 아닐 경우 -1을 반환합니다.
    """

    debug_check_messages()
    url = "http://localhost:9000/queue-size"  # Collector API 주소
    try:
        response = requests.get(url, timeout=5)
        queue_size = response.text.strip()
        return int(queue_size)
    except Exception as e:
        print("Error fetching queue size:", e)
        return -1


@tool(description="기존 요약 summary_log.txt 파일에서 마지막 N줄을 반환합니다. 파일이 없을 경우 빈 문자열을 반환합니다.")
def read_recent_summary_lines(n: int = 100) -> str:
    """
    summary_log.txt 파일에서 마지막 n줄을 반환합니다.
    파일이 없으면 빈 문자열 반환.
    """
    debug_check_messages()
    if os.path.exists(SUMMARY_LOG_PATH):
        with open(SUMMARY_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return "".join(lines[-n:])  # 마지막 n줄
    return ""


@tool(description="요약된 텍스트를 summary_log.txt 파일에 저장합니다.")
def write_summary_log(summary_text: str) -> str:
    """
    요약된 텍스트를 summary_log.txt에 저장합니다. 기존 내용에 추가되며,
    저장 시각이 함께 기록됩니다.

    Args:
        summary_text (str): 저장할 요약 결과

    Returns:
        str: 저장 완료 메시지
    """

    debug_check_messages()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = os.path.dirname(SUMMARY_LOG_PATH)
    os.makedirs(log_dir, exist_ok=True)

    entry = f"\n--- 요약 시각: {timestamp} ---\n{summary_text}\n"

    try:
        with open(SUMMARY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
        return "요약 로그 저장 완료 (추가됨)"
    except Exception as e:
        return f"파일 저장 실패: {str(e)}"


# LLM이 사용하는 요약 처리 도구
@tool(description="입력된 로그 문자열 목록을 요약합니다.")
def summarize_logs_tool(logs: List[str]) -> str:
    """
    서버 로그 데이터를 요약합니다.

    Args:
        logs (List[str]): 로그 문자열 리스트

    Returns:
        str: 요약된 로그 내용 또는 오류 메시지
    """

    debug_check_messages()
    try:
        # chain 이용해서 요약
        prompt = build_log_summary_prompt()
        chain = prompt | llm
        result = chain.invoke({"logs": "\n".join(logs)})
        return result.content.strip()
    except Exception as e:
        return f"[요약 실패] {str(e)}"


@tool(description="입력된 로그나 상황 설명을 받아 상황을 논리적으로 분석하고, 원인과 대응 방안을 단계별로 제시합니다.")
def inference_helper(context: str) -> str:
    """
    상황을 이해하고 분석하는 데 도움을 주는 추론 보조 툴입니다.
    - 문제 상황을 요약
    - 가능한 원인 및 영향 분석
    - 다음 대응 단계 제안

    Args:
        context (str): 현재 요청이나 문제 상황

    Returns:
        str: 에이전트가 논리적으로 생각한 추론 결과 및 제안
    """
    # 아래는 간단한 예시 문장. 실제로는 LLM에게 prompt로 보내거나 규칙 기반 분석 가능
    reasoning = (
        f"상황 요약: {context}\n\n"
        "1. 문제의 주요 원인 분석을 시도합니다.\n"
        "2. 발생 가능한 영향 및 위험도를 평가합니다.\n"
        "3. 적절한 다음 조치나 대응 방향을 제안합니다.\n\n"
        "이 정보를 바탕으로 최적의 결정을 내릴 수 있도록 돕겠습니다."
    )
    return reasoning


@tool(description="검색 쿼리를 받아서 DuckDuckGo를 통해 웹에서 관련 정보를 찾아 반환합니다.")
def web_search_tool(query: str) -> str:
    """
    검색 쿼리를 받아서 웹에서 관련 정보를 찾아 반환합니다.
    """
    duck_search = DuckDuckGoSearchRun()
    return duck_search.run(query)


@tool(description="현재 상황을 논리적으로 분석하고, 필요한 경우 적절한 도구 사용을 제안합니다.")
def think_aloud(context: str) -> str:
    """
    상황을 이해하고 분석하는 데 도움을 주는 추론 보조 툴입니다.
    - 문제 상황을 요약
    - 필요한 경우 웹 검색 수행
    - 가능한 원인 및 영향 분석
    - 다음 대응 단계 제안

    Log를 분석하고, 모르는 내용이 있으면 web_search_tool 사용을 권장하는 추론 도구입니다.

    Args:
        context (str): 현재 문제 상황 또는 로그들

    Returns:
        str: 분석 결과 및 도구 사용 권장 메시지
    """
    return (
        f"이 상황을 이렇게 이해했습니다: {context}\n\n"
        "만약 해결책이나 정보가 부족하다면, 'web_search_tool'을 사용해서 추가 검색을 시도하세요."
    )
