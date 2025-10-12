import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer  # type: ignore
import qdrant_client  # type: ignore
from qdrant_client.http import models  # type: ignore
from app.db import list_publications

print("\n[INFO] Memulai pengisian Qdrant...")

# === Inisialisasi Qdrant & Model ===
qdrant = qdrant_client.QdrantClient(
    url="http://localhost:6333",
    prefer_grpc=False,
    timeout=60,
    check_compatibility=False  # ✅ hilangkan warning versi
)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# === Konfigurasi koleksi ===
collection_name = "nasa_bioscience"

if not qdrant.collection_exists(collection_name=collection_name):
    print(f"[INFO] Membuat koleksi baru: {collection_name}")
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )
else:
    print(f"[INFO] Koleksi '{collection_name}' sudah ada, menghapus isinya...")
    qdrant.delete(
        collection_name=collection_name,
        points_selector=models.FilterSelector(filter=models.Filter())
    )

# === Ambil publikasi dari database/CSV ===
publications = list_publications(page_size=9999)
print(f"[INFO] Menambahkan {len(publications)} publikasi...")

# === Proses dan masukkan ke Qdrant ===
batch_size = 50
ids, vectors, payloads = [], [], []

for i, pub in enumerate(publications, start=1):
    # pastikan teks bersih dan tidak kosong
    title = str(pub.get("title", "") or "").strip()
    abstract = str(pub.get("abstract", "") or "").strip()
    text = f"{title} {abstract}".strip()

    if not text:
        continue

    # pastikan id adalah integer unik (CSV kadang string / kosong)
    pub_id = int(pub.get("id") or i)

    # buat vektor embedding
    vector = model.encode(text).tolist()

    ids.append(pub_id)
    vectors.append(vector)
    payloads.append({
        "title": title,
        "abstract": abstract,
        "mission": str(pub.get("mission", "") or ""),
        "organism": str(pub.get("organism", "") or ""),
        "system": str(pub.get("system", "") or "")
    })

    # kirim per batch agar efisien
    if len(ids) >= batch_size or i == len(publications):
        qdrant.upsert(
            collection_name=collection_name,
            points=models.Batch(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )
        )
        print(f"[INFO] {i}/{len(publications)} publikasi dimasukkan...")
        ids, vectors, payloads = [], [], []

print(f"\n[✅] Selesai! Total {len(publications)} publikasi berhasil dimasukkan ke Qdrant.\n")
