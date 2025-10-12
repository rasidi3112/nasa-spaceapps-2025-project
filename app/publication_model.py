# app/publication_model.py
from pydantic import BaseModel # type: ignore
from typing import Optional, List

class PublicationModel(BaseModel):
    id: str
    title: Optional[str] = None
    link: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    mission: Optional[str] = None
    organism: Optional[str] = None
    system: Optional[str] = None
    keywords: Optional[List[str]] = None

    @staticmethod
    def from_dict(data: dict):
        """
        Membuat instance PublicationModel dari dictionary (row CSV)
        """
        # Jika authors / keywords ada tapi berupa string, kita ubah jadi list
        authors = data.get("authors")
        if authors and isinstance(authors, str):
            authors = [a.strip() for a in authors.split(",")]

        keywords = data.get("keywords")
        if keywords and isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]

        # Tahun diubah ke int kalau ada
        year = data.get("year")
        if year:
            try:
                year = int(year)
            except ValueError:
                year = None

        return PublicationModel(
            id=data.get("id", ""),
            title=data.get("title"),
            link=data.get("link"),
            authors=authors,
            year=year,
            abstract=data.get("abstract"),
            mission=data.get("mission"),
            organism=data.get("organism"),
            system=data.get("system"),
            keywords=keywords,
        )
