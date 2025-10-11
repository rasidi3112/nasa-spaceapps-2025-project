from typing import List, Optional
import csv
import requests # type: ignore
import io
from app.publication_model import PublicationModel

# Path ke CSV di GitHub (data 608 publikasi NASA)
CSV_PATH = "data/SB_publication_PMC.csv"

def load_publications() -> List[PublicationModel]:  # type: ignore
    """Memuat publikasi NASA langsung dari CSV di GitHub."""
    publications = []
    try:
        # Ambil file CSV langsung dari GitHub
        response = requests.get(CSV_PATH)
        response.raise_for_status()

        # Ubah teks CSV ke bentuk file-like agar bisa dibaca csv.DictReader
        csv_content = io.StringIO(response.text)
        reader = csv.DictReader(csv_content)

        for row in reader:
            # Pastikan PublicationModel punya method from_dict
            publications.append(PublicationModel.from_dict(row))

        print(f"[INFO] Loaded {len(publications)} publications from NASA GitHub.")
    except Exception as e:
        print(f"[ERROR] Failed to load publications: {e}")

    return publications


# Cache publikasi di memory
PUBLICATIONS = load_publications()

def list_publications(
    page: int = 1,
    page_size: int = 20,
    organism: Optional[str] = None,
    mission: Optional[str] = None,
    system: Optional[str] = None,
) -> List[PublicationModel]:  # type: ignore
    """Mengembalikan daftar publikasi dengan filter dan pagination."""
    filtered = PUBLICATIONS
    if organism:
        filtered = [p for p in filtered if p.organism and organism.lower() in p.organism.lower()]
    if mission:
        filtered = [p for p in filtered if p.mission and mission.lower() in p.mission.lower()]
    if system:
        filtered = [p for p in filtered if p.system and system.lower() in p.system.lower()]

    start = (page - 1) * page_size
    end = start + page_size
    return filtered[start:end]


def get_publication_by_id(pub_id: str) -> PublicationModel:
    """Mengambil satu publikasi berdasarkan ID."""
    for p in PUBLICATIONS:
        if str(p.id) == str(pub_id):
            return p
    raise ValueError(f"Publication {pub_id} not found")
