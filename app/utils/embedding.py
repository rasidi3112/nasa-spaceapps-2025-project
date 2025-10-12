# app/utils/embedding.py
from typing import List, Optional
from sentence_transformers import SentenceTransformer, util  # type: ignore
import qdrant_client  # type: ignore
from deep_translator import GoogleTranslator  # type: ignore
from app.publication_model import PublicationModel
from app.db import get_publication_by_id_object, list_publications_objects

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_COLLECTION = "nasa_bioscience"

# ==========================================================
# Inisialisasi model embedding
# ==========================================================
try:
    _vector_model = SentenceTransformer(MODEL_NAME)
    print(f"[INFO] Model embedding '{MODEL_NAME}' berhasil dimuat ✅")
except Exception as e:
    print(f"[WARN] Gagal memuat model embedding: {e}")
    _vector_model = None

# ==========================================================
# Inisialisasi Qdrant
# ==========================================================
try:
    _qdrant = qdrant_client.QdrantClient(url="http://localhost:6333")
    _qdrant.get_collections()
    _qdrant_connected = True
    print("[INFO] Qdrant terhubung di localhost:6333 ✅")
except Exception as e:
    print(f"[WARN] Tidak dapat terhubung ke Qdrant: {e}")
    _qdrant = None
    _qdrant_connected = False

# ==========================================================
# Default fallback response
# ==========================================================
_DEFAULT_RESPONSE = {
    "bullet_summary": ["Ringkasan tidak tersedia."],
    "key_findings": ["Belum ada temuan yang dapat diringkas."],
    "risk_assessment": ["Belum ada penilaian risiko yang tersedia."],
    "recommended_actions": ["Tidak ada rekomendasi aksi saat ini."],
}

# ==========================================================
# Helper: translate query
# ==========================================================
def translate_query(text: str) -> str:
    """Terjemahkan query ke bahasa Inggris agar embedding lebih akurat."""
    if not text:
        return ""
    try:
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        print(f"[DEBUG] Terjemahan query: '{text}' → '{translated}'")
        return translated
    except Exception as e:
        print(f"[WARN] Gagal menerjemahkan query: {e}")
        return text  # fallback

# ==========================================================
# Helper: extract sentences
# ==========================================================
def _extract_sentences(text: str) -> List[str]:
    if not text:
        return []
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 10]
    seen, unique = set(), []
    for s in sentences:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique

# ==========================================================
# Fallback summarizer lokal
# ==========================================================
def _fallback_summarize(text: str) -> dict:
    if not text or not _vector_model:
        return _DEFAULT_RESPONSE.copy()

    sentences = _extract_sentences(text)
    if not sentences:
        return _DEFAULT_RESPONSE.copy()

    try:
        embeddings = _vector_model.encode(sentences, convert_to_tensor=True)
        centroid = embeddings.mean(dim=0)
        scores = util.cos_sim(centroid, embeddings)[0]
        top_indices = scores.argsort(descending=True)[:5]
        top_sentences = [sentences[i] for i in top_indices]

        bullet_summary = top_sentences[:3]
        key_findings = [
            s for s in top_sentences if any(k in s.lower() for k in ["result", "finding", "discover", "show"])
        ] or bullet_summary[:2]
        risk_assessment = [
            s for s in sentences if any(k in s.lower() for k in ["risk", "hazard", "limitation", "challenge"])
        ][:3] or ["Tidak ada risiko yang secara eksplisit disebutkan."]
        recommended_actions = [
            s for s in sentences if any(k in s.lower() for k in ["should", "recommend", "suggest", "propose"])
        ][:3] or ["Belum ada rekomendasi spesifik yang tercatat."]

        return {
            "bullet_summary": bullet_summary,
            "key_findings": key_findings,
            "risk_assessment": risk_assessment,
            "recommended_actions": recommended_actions,
        }

    except Exception as e:
        print(f"[WARN] Gagal ringkasan fallback: {e}")
        return _DEFAULT_RESPONSE.copy()

# ==========================================================
# Fallback search sederhana
# ==========================================================
def fallback_search(query: str, top_k: int = 5) -> List[PublicationModel]:
    """Pencarian sederhana jika Qdrant tidak tersedia."""
    all_pubs = list_publications_objects()
    q_lower = query.lower()
    results: List[PublicationModel] = []
    for p in all_pubs:
        title = getattr(p, "title", "") or ""
        abstract = getattr(p, "abstract", "") or ""
        text = f"{title} {abstract}".lower()
        if q_lower in text:
            results.append(p)
    print(f"[INFO] Fallback search menemukan {len(results)} hasil untuk query '{query}'")
    return results[:top_k]

# ==========================================================
# Pencarian utama (Qdrant + fallback)
# ==========================================================
def semantic_search(query: str, top_k: int = 5) -> List[PublicationModel]:
    """
    Cari publikasi paling relevan menggunakan embedding query di Qdrant.
    Fallback ke text search jika Qdrant tidak tersedia.
    """
    if not query:
        print("[WARN] Query kosong, tidak ada hasil.")
        return []

    query_en = translate_query(query)

    if _qdrant_connected and _vector_model:
        try:
            query_vector = _vector_model.encode(query_en).tolist()
            hits = _qdrant.search(
                collection_name=_COLLECTION,
                query_vector=query_vector,
                limit=top_k
            )

            results: List[PublicationModel] = []
            for hit in hits:
                payload = hit.payload or {}
                pub_id = payload.get("id") or str(hit.id)
                try:
                    pub = get_publication_by_id_object(pub_id)
                except Exception:
                    pub = PublicationModel(
                        id=pub_id,
                        title=payload.get("title", "Untitled Publication"),
                        authors=[],
                        year=payload.get("year", 2024),
                        abstract=payload.get("abstract", ""),
                        mission=payload.get("mission", ""),
                        organism=payload.get("organism", ""),
                        system=payload.get("system", ""),
                        keywords=[]
                    )
                results.append(pub)

            print(f"[INFO] Qdrant search menemukan {len(results)} hasil untuk query '{query_en}'")
            return results

        except Exception as e:
            print(f"[ERROR] Gagal melakukan pencarian di Qdrant: {e}")

    # fallback
    print("[INFO] Menggunakan fallback pencarian teks sederhana 🔍")
    return fallback_search(query_en, top_k=top_k)
