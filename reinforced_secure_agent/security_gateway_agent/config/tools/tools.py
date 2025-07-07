from config.tools import *
from langchain_community.tools import DuckDuckGoSearchRun
import base64


@tool
def suspicious_pattern_detector(request_payload: str) -> str:
    """
    웹 요청에서 SQL Injection, XSS 등의 악성 패턴 여부를 탐지합니다.

    Args:
        request_payload (str): HTTP 요청 파라미터 또는 본문

    Returns:
        str: 악성 여부 판단
    """
    import re
    patterns = [
        r"(?i)(\bselect\b|\binsert\b|\bupdate\b|\bdelete\b|\bdrop\b)",  # SQL Injection
        r"(?i)<script.*?>.*?</script>",  # XSS
        r"(?i)\bUNION\b.*\bSELECT\b",  # SQL Union Injection
        r"\.\./",  # Path Traversal
    ]
    for pattern in patterns:
        if re.search(pattern, request_payload):
            return "악성 요청 감지됨"
    return "SQL, XSS,SQL Union Injection, Path Traversal Pattern 통과"


# Web Search Tool
web_search_tool = DuckDuckGoSearchRun()


'''
Rate Limit Tool
'''
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


@tool
def think_aloud(context: str) -> str:
    """
    어떤 툴을 사용해야 할지 모를 때, 자신이 상황을 어떻게 이해했는지 생각을 정리합니다.

    Args:
        context (str): 현재 요청이나 문제 상황

    Returns:
        str: 에이전트의 추론 과정
    """
    return (f"이 상황을 어떻게 판단할 수 있을지 논리적으로 생각해봅니다."
            f"또한 도구를 사용하다 실패할 경우도 web_search를 찾아서 생각해봅니다"
            f" (만약 이해가 안되면, web_search 도구를 사용해서 검색하세요): {context}")


# @tool(description="상황을 논리적으로 분석하고, 추가 도구 사용이 필요한지 판단합니다.")
# def think_aloud(context: str) -> str:
#     """
#     로그나 요청 정보를 바탕으로 현재 상황을 스스로 분석하고, 필요한 경우 적절한 도구 사용을 제안합니다.
#
#     주요 기능:
#     - 공격 가능성 또는 이상 행위 탐지
#     - 의심되는 패턴에 대한 해석
#     - 추가 분석이 필요할 경우 관련 도구(base64_decode, web_search 등) 추천
#     - 다음 액션에 대한 제안
#
#     Args:
#         context (str): 현재 로그, 요청, 또는 상황 설명
#
#     Returns:
#         str: 분석된 내용, 의심 포인트, 도구 사용 권장 등
#     """
#     return (
#         f"[상황 분석 결과]\n{context}\n\n"
#         "💡 만약 분석이 불완전하거나 의심되는 인코딩, 의도 등이 포함되어 있다면:\n"
#         "- Encoding되어 있다고 생각하는 부분을 base64_decode 도구로 디코딩을 시도하거나\n"
#         "- web_search_tool을 활용해 추가 정보를 수집하는 것이 좋습니다."
#     )


# DuckDuckGo를 직접 감싸서 tool 함수로 변환
@tool
def web_search_tool(query: str) -> str:
    """
    검색 쿼리를 받아서 웹에서 관련 정보를 찾아 반환합니다.
    """
    duck_search = DuckDuckGoSearchRun()
    return duck_search.run(query)


@tool(description="Base64로 인코딩된 문자열을 디코딩합니다. 일반적으로 평문 문자열을 확인할 때 사용합니다.")
def base64_decode_tool(encoded: str) -> str:
    """Base64로 한 번 또는 여러 번 인코딩된 문자열을 디코딩합니다."""
    try:
        first = base64.b64decode(encoded)
        second = base64.b64decode(first)
        return second.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Double Decoding Failed] {str(e)}"


@tool(description="Unicode로 인코딩된 문자열을 디코딩합니다. 예: \\u003cscript\\u003e 등")
def unicode_decode_tool(encoded: str) -> str:
    """
    Unicode escape 형태의 문자열 (예: \\uXXXX, &#xXXXX;)을 사람이 읽을 수 있는 문자열로 디코딩합니다.

    Args:
        encoded (str): 유니코드 이스케이프가 포함된 문자열

    Returns:
        str: 디코딩된 결과
    """
    try:
        # HTML-style escape 먼저 처리 (예: &#x41;)
        import html
        decoded_html = html.unescape(encoded)

        # Python-style Unicode escape 처리 (예: \u0041)
        return decoded_html.encode().decode("unicode_escape")
    except Exception as e:
        return f"[Unicode Decoding Failed] {str(e)}"


@tool(description="문자열을 구분자 기준으로 나눕니다.")
def split_string(text: str, delimiter: str = " ") -> list[str]:
    """
    문자열을 지정한 구분자를 기준으로 분리합니다.
    예: 명령어 시퀀스, 파라미터 등 쪼개야 할 때 사용

    Args:
        text (str): 전체 문자열
        delimiter (str): 나눌 기준 문자 (기본: 공백)

    Returns:
        list[str]: 쪼개진 문자열 리스트
    """
    return text.split(delimiter)


@tool(description="문자열 리스트를 하나의 문자열로 합칩니다.")
def join_strings(parts: list[str], delimiter: str = " ") -> str:
    """
    문자열 리스트를 하나로 결합합니다.

    Args:
        parts (list[str]): 문자열 리스트
        delimiter (str): 결합할 구분자 (기본: 공백)

    Returns:
        str: 결합된 문자열
    """
    return delimiter.join(parts)
