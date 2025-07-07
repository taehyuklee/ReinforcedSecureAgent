from config.tools import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


@tool
def log_cluster_anomaly_detector(log_lines: list[str]) -> list[str]:
    """
    로그를 클러스터링 기반으로 분류하고, 이상치 로그를 탐지합니다.
    특정 로그 형태와 다른 로그들을 '의심 로그'로 분리합니다.

    Args:
        log_lines (list[str]): 로그 라인 리스트

    Returns:
        list[str]: 이상 징후로 의심되는 로그 라인들
    """

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(log_lines)

    model = KMeans(n_clusters=3, random_state=42)
    labels = model.fit_predict(X)

    # 가장 작은 군집을 이상치로 간주
    from collections import Counter
    label_count = Counter(labels)
    rare_label = min(label_count, key=label_count.get)

    anomalies = [log for log, label in zip(log_lines, labels) if label == rare_label]
    return anomalies
