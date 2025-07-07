# cluster_representatives.py
from qdrant_client import QdrantClient
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from sklearn.metrics import silhouette_score
import numpy as np
from qdrant_client.http.models import PointIdsList

# Qdrant 연결
qdrant = QdrantClient(host="localhost", port=6333)
collection = "caching"

# 벡터 + payload 조회
records, _ = qdrant.scroll(
    collection_name=collection,
    with_vectors=True,
    with_payload=True,
    limit=10000
)

vectors = [pt.vector for pt in records]
payloads = [pt.payload for pt in records]
ids = [pt.id for pt in records]

X = np.array(vectors)
k = 50  # 클러스터 수

kmeans = KMeans(n_clusters=k, random_state=42).fit(X)
labels = kmeans.labels_
centers = kmeans.cluster_centers_

# 1. 클러스터별 개수 출력
unique_labels, counts = np.unique(labels, return_counts=True)
print("클러스터별 데이터 개수:")
for label, count in zip(unique_labels, counts):
    print(f"  클러스터 {label}: {count}개")

# 2. Silhouette Score 출력 (클러스터 수 2 이상일 때만 계산)
if k > 1 and len(set(labels)) > 1:
    score = silhouette_score(X, labels)
    print(f"Silhouette Score: {score:.4f}")
else:
    print("Silhouette Score 계산 불가 (클러스터 수 부족)")

# 대표 예시 선택 및 대표-중심 거리 출력
representative_ids = []
print("\n클러스터 대표 예시와 중심 벡터 간 코사인 거리:")
for cluster_id in range(k):
    cluster_indices = np.where(labels == cluster_id)[0]
    cluster_vectors = X[cluster_indices]
    center = centers[cluster_id]

    dists = cdist(cluster_vectors, [center], metric="cosine")
    closest_index = cluster_indices[np.argmin(dists)]

    representative_ids.append(ids[closest_index])
    dist = dists.min()
    print(f"  클러스터 {cluster_id}: 거리 {dist:.4f}")

# 대표 예시에 태그 부여
for point_id in representative_ids:
    qdrant.set_payload(
        collection_name=collection,
        payload={"is_representative": True},
        points=[point_id]
    )

# 대표 예시가 아닌 나머지 삭제
to_delete = list(set(ids) - set(representative_ids))

if to_delete:
    qdrant.delete(
        collection_name=collection,
        points_selector=PointIdsList(points=to_delete)
    )

print(f"\n{len(representative_ids)} representative examples updated.")
print(f"{len(to_delete)} non-representative examples deleted.")
