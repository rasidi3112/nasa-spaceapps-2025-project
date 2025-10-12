from typing import List, Optional
import csv
import requests
import io
from app.publication_model import PublicationModel

CSV_PATH = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"

def load_publications() -> List[PublicationModel]:
    publications = []
    try:
        response = requests.get(CSV_PATH)
        response.raise_for_status()
        csv_content = io.StringIO(response.text)
        reader = csv.DictReader(csv_content)

        for i, row in enumerate(reader):
            pub = PublicationModel.from_dict(row)

            if not getattr(pub, "id", None):
                pub.id = str(i + 1)

            pub.title = pub.title or f"Publication {i+1}"
            pub.link = getattr(pub, "link", row.get("link", ""))
            pub.authors = getattr(pub, "authors", [])
            pub.year = getattr(pub, "year", 0)
            pub.abstract = getattr(pub, "abstract", "")
            pub.mission = getattr(pub, "mission", "")
            pub.organism = getattr(pub, "organism", "")
            pub.system = getattr(pub, "system", "")
            pub.keywords = getattr(pub, "keywords", [])

            publications.append(pub)

        print(f"[INFO] Loaded {len(publications)} publications from NASA GitHub.")
        if publications:
            print("Sample publication:", publications[0].__dict__)
    except Exception as e:
        print(f"[ERROR] Failed to load publications: {e}")

    return publications

# cache publikasi
PUBLICATIONS = load_publications()

# ====== Normalisasi dict =====
def normalize_publication(pub: PublicationModel):
    return {
        "id": str(pub.id),
        "title": pub.title or "",
        "link": getattr(pub, "link", ""),
        "authors": pub.authors if isinstance(pub.authors, list) else [],
        "year": int(pub.year) if pub.year else 0,
        "abstract": pub.abstract or "",
        "mission": (pub.mission or "").strip(),
        "organism": (pub.organism or "").strip(),
        "system": (pub.system or "").strip(),
        "keywords": pub.keywords if isinstance(pub.keywords, list) else [],
    }

# ====== API-like helpers =====
def list_publications(
    page: int = 1,
    page_size: int = 20,
    organism: Optional[str] = None,
    mission: Optional[str] = None,
    system: Optional[str] = None
) -> List[dict]:
    filtered = PUBLICATIONS
    if organism:
        filtered = [p for p in filtered if p.organism and organism.lower() in p.organism.lower()]
    if mission:
        filtered = [p for p in filtered if p.mission and mission.lower() in p.mission.lower()]
    if system:
        filtered = [p for p in filtered if p.system and system.lower() in p.system.lower()]

    start = (page - 1) * page_size
    end = start + page_size
    return [normalize_publication(p) for p in filtered[start:end]]

def get_publication_by_id(pub_id: str) -> dict:
    for p in PUBLICATIONS:
        if str(p.id) == str(pub_id):
            return normalize_publication(p)
    raise ValueError(f"Publication {pub_id} not found")

# ====== PublicationModel versions =====
def list_publications_objects(
    page: int = 1,
    page_size: int = 20,
    organism: Optional[str] = None,
    mission: Optional[str] = None,
    system: Optional[str] = None
) -> List[PublicationModel]:
    dict_list = list_publications(page, page_size, organism, mission, system)
    return [PublicationModel(**d) for d in dict_list]

def get_publication_by_id_object(pub_id: str) -> PublicationModel:
    for p in PUBLICATIONS:
        if str(p.id) == str(pub_id):
            return p
    raise ValueError(f"Publication {pub_id} not found")

# khusus persona.py
def list_publications_models(
    page: int = 1,
    page_size: int = 20,
    organism: Optional[str] = None,
    mission: Optional[str] = None,
    system: Optional[str] = None
) -> List[PublicationModel]:
    return list_publications_objects(page, page_size, organism, mission, system)
