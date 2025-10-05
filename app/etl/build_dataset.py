# etl/build_dataset.py
import csv
import json
from pathlib import Path
import uuid
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def load_csv(csv_path: Path):
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        return list(reader)

def fetch_full_text(url: str) -> str:
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        article = soup.find("article") or soup.find("body")
        return article.get_text(separator="\n")[:20000]
    except Exception:
        return ""

def build_publication_records(rows):
    records = []
    for row in rows:
        pub_id = str(uuid.uuid4())
        text = fetch_full_text(row["url"])
        record = {
            "id": pub_id,
            "title": row["title"],
            "authors": row.get("authors", ""),
            "year": int(row.get("year", 0)),
            "abstract": row.get("abstract", ""),
            "mission": row.get("mission", ""),
            "organism": row.get("organism", ""),
            "system": row.get("system", ""),
            "keywords": row.get("keywords", ""),
            "url": row.get("url", ""),
            "osdr_id": row.get("osdr_id", ""),
            "taskbook_id": row.get("taskbook_id", ""),
            "full_text": text,
        }
        records.append(record)
    return records

def save_json(records, path: Path):
    with path.open("w") as f:
        json.dump(records, f, indent=2)

if __name__ == "__main__":
    csv_rows = load_csv(Path("data/nasa_bioscience_publications.csv"))
    records = build_publication_records(csv_rows)
    save_json(records, DATA_DIR / "publications.json")