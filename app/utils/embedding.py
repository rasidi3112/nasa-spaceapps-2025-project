# app/utils/embedding.py
from typing import List
from sentence_transformers import SentenceTransformer  # type: ignore
import qdrant_client  # type: ignore
from app.publication_model import PublicationModel
from app.db import get_publication_by_id, list_publications

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_COLLECTION = "nasa_bioscience"

# Inisialisasi model embedding
try:
    _vector_model = SentenceTransformer(MODEL_NAME)
    print(f"[INFO] Model embedding '{MODEL_NAME}' berhasil dimuat ✅")
except Exception as e:
    print(f"[WARN] Gagal memuat model embedding: {e}")
    _vector_model = None

# Inisialisasi Qdrant (dengan pengecekan koneksi)
try:
    _qdrant = qdrant_client.QdrantClient(url="http://localhost:6333")
    _qdrant.get_collections()  # Tes koneksi
    _qdrant_connected = True
    print("[INFO] Qdrant terhubung di localhost:6333 ✅")
except Exception as e:
    print(f"[WARN] Tidak dapat terhubung ke Qdrant: {e}")
    _qdrant = None
    _qdrant_connected = False


def semantic_search(query: str, top_k: int = 5) -> List[PublicationModel]:  # type: ignore
    """
    Cari publikasi paling relevan menggunakan embedding query.
    Jika Qdrant tidak aktif, fallback ke pencarian teks sederhana.
    """
    if not query or not _vector_model:
        print("[WARN] Query kosong atau model embedding belum siap.")
        return []

    # ⚙️ Mode 1: Gunakan Qdrant jika tersedia
    if _qdrant_connected:
        try:
            query_vector = _vector_model.encode(query).tolist()
            hits = _qdrant.search(
                collection_name=_COLLECTION,
                query_vector=query_vector,
                limit=top_k
            )

            results: List[PublicationModel] = []  # type: ignore
            for hit in hits:
                pub_id = hit.payload.get("id")
                if not pub_id:
                    continue
                try:
                    pub = get_publication_by_id(pub_id)
                    results.append(pub)
                except Exception:
                    continue
            print(f"[INFO] Qdrant search menemukan {len(results)} hasil untuk query '{query}'")
            return results

        except Exception as e:
            print(f"[ERROR] Gagal melakukan pencarian di Qdrant: {e}")

    # ⚙️ Mode 2 (fallback): pencarian teks biasa
    print("[INFO] Menggunakan fallback pencarian teks sederhana 🔍")
    all_pubs = list_publications(page_size=9999)
    q_lower = query.lower()

    results: List[PublicationModel] = []
    for p in all_pubs:
        # pastikan semua field ada
        title = getattr(p, "title", "") or ""
        abstract = getattr(p, "abstract", "") or ""
        # gabungkan semua teks yang relevan, termasuk link atau metadata jika perlu
        text = f"{title} {abstract}".lower()
        if q_lower in text:
            results.append(p)

    print(f"[INFO] Fallback search menemukan {len(results)} hasil untuk query '{query}'")
    return results[:top_k]
