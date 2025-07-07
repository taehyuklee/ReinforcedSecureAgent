import time  # RAG 성능 측정을 위한 time import
from typing import Callable, Any


# Proxy Pattern을 이용해서 모든 함수에 대해 시간을 측정한다.
def check_of_time(func: Callable[..., Any], log_sentence: str):
    start = time.time()
    func()
    end = time.time()
    print(f"{log_sentence} 시간: {end - start:.4f}초")
    