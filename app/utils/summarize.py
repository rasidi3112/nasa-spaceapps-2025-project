import json
from typing import Dict, List, Optional

from sentence_transformers import SentenceTransformer, util

# ==========================================================
# Config fallback
# ==========================================================
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_DEFAULT_RESPONSE = {
    "bullet_summary": ["Ringkasan tidak tersedia."],
    "key_findings": ["Belum ada temuan yang dapat diringkas."],
    "risk_assessment": ["Belum ada penilaian risiko yang tersedia."],
    "recommended_actions": ["Tidak ada rekomendasi aksi saat ini."],
}

try:
    _MODEL = SentenceTransformer(MODEL_NAME)
    print(f"[INFO] Model lokal '{MODEL_NAME}' berhasil dimuat ✅")
except Exception as e:
    print(f"[WARN] Gagal memuat model lokal: {e}")
    _MODEL = None

# ==========================================================
# Helper functions
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

def _fallback_summarize(text: str) -> Dict[str, List[str]]:
    if not text or not _MODEL:
        return _DEFAULT_RESPONSE.copy()
    
    sentences = _extract_sentences(text)
    if not sentences:
        return _DEFAULT_RESPONSE.copy()

    try:
        embeddings = _MODEL.encode(sentences, convert_to_tensor=True)
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
# Fungsi utama
# ==========================================================
def generate_summary(publication: object, focus_section: Optional[str] = None, persona: str = "scientist") -> Dict[str, List[str]]:
    if publication is None:
        return _DEFAULT_RESPONSE.copy()

    # Gunakan abstrak dulu, jika kosong pakai judul
    text_source = getattr(publication, "abstract", "") or getattr(publication, "title", "")
    
    if not text_source.strip():
        return _DEFAULT_RESPONSE.copy()

    print("[INFO] Menggunakan fallback summarizer lokal 🧠")
    return _fallback_summarize(text_source)
