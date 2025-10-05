# app/db.py
from typing import List, Optional
import csv
from app.publication_model import PublicationModel

# Path ke CSV
CSV_PATH = "data/SB_publication_PMC.csv"

# Load semua publikasi dari CSV saat startup
def load_publications() -> List[PublicationModel]: # type: ignore
    publications = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            publications.append(PublicationModel.from_dict(row))
    return publications

# Cache publikasi di memory
PUBLICATIONS = load_publications()

def list_publications(
    page: int = 1,
    page_size: int = 20,
    organism: Optional[str] = None,
    mission: Optional[str] = None,
    system: Optional[str] = None
) -> List[PublicationModel]: # type: ignore
    filtered = PUBLICATIONS
    if organism:
        filtered = [p for p in filtered if p.organism and p.organism.lower() == organism.lower()]
    if mission:
        filtered = [p for p in filtered if p.mission and p.mission.lower() == mission.lower()]
    if system:
        filtered = [p for p in filtered if p.system and p.system.lower() == system.lower()]
    
    start = (page - 1) * page_size
    end = start + page_size
    return filtered[start:end]

def get_publication_by_id(pub_id: str) -> PublicationModel:
    for p in PUBLICATIONS:
        if p.id == pub_id:
            return p
    raise ValueError(f"Publication {pub_id} not found")
