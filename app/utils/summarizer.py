# app/utils/summarizer.py
from utils.summarize import generate_summary # type: ignore

def generate_summary(publication, focus_section=None, persona="scientist"):
    # sementara ini hanya dummy agar server tidak error
    return {
        "bullet_summary": ["Ringkasan poin penting belum diimplementasikan."],
        "key_findings": ["Belum ada temuan kunci."],
        "risk_assessment": ["Belum ada analisis risiko."],
        "recommended_actions": ["Belum ada rekomendasi."]
    }
