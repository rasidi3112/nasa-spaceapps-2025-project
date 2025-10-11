import csv
import qdrant_client # type: ignore
from qdrant_client.models import PointStruct, VectorParams # type: ignore
from sentence_transformers import SentenceTransformer # type: ignore

CSV_PATH = "data/SB_publication_PMC.csv"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION = "nasa_bioscience"

print("🚀 Menghubungkan ke Qdrant...")
client = qdrant_client.QdrantClient(url="http://localhost:6333")
model = SentenceTransformer(MODEL_NAME)

# Buat koleksi kalau belum ada
client.recreate_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=384, distance="Cosine")
)

print("📄 Memuat CSV...")
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    points = []
    for i, row in enumerate(reader):
        text = f"{row['Title']} {row.get('Abstract', '')}"
        vector = model.encode(text).tolist()
        points.append(PointStruct(id=i, vector=vector, payload=row))

        if len(points) == 50:  # batch insert per 50
            client.upsert(collection_name=COLLECTION, points=points)
            points = []

    if points:
        client.upsert(collection_name=COLLECTION, points=points)

print("✅ Indexing selesai! Semua publikasi NASA siap dipakai.")
