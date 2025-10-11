# app/utils/persona.py
from typing import List
from app.db import list_publications

# Mock data fallback
MOCK_PUBLICATIONS = ["OSDR-244", "NASA-19-EPXR-0012", "MarsHabitat2035"]

PERSONA_INSIGHTS = {
    "scientist": {
        "insights": [
            "Kenaikan ekspresi gen inflamasi ditemukan konsisten pada eksperimen mikrogravitasi jangka panjang.",
            "Studi tanaman menunjukkan adaptasi akar signifikan dalam kondisi gravitasi fraksional."
        ],
        "filters": {"system": None, "organism": "Human"}
    },
    "manager": {
        "insights": [
            "Portofolio penelitian radiasi memiliki gap pada kombinasi radiasi + mikrogravitasi.",
            "Investasi terbesar berada pada studi cardiovascular, namun publikasi terbaru menunjukkan kebutuhan eksperimen ulang."
        ],
        "filters": {"system": "Cardiovascular"}
    },
    "architect": {
        "insights": [
            "Untuk habitat permukaan Mars, penelitian tentang regenerasi tulang menonjol sebagai area risiko tinggi.",
            "Eksperimen closed-loop life support menunjukkan keberhasilan tanaman berdaun lebar dalam kondisi CO₂ tinggi."
        ],
        "filters": {"mission": "Mars"}
    },
}

def personalize_insights(persona: str):
    persona = persona.lower()
    default = PERSONA_INSIGHTS.get("scientist")
    data = PERSONA_INSIGHTS.get(persona, default)

    # Ambil publikasi dari database
    pubs = list_publications(page=1, page_size=5, **data["filters"])
    pub_ids = [p.id for p in pubs]

    # Jika database kosong, pakai mock
    if not pub_ids:
        pub_ids = MOCK_PUBLICATIONS

    return {
        "persona": persona,
        "insights": data["insights"],
        "suggested_publications": pub_ids
    }
