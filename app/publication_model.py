# app/publication_model.py
from pydantic import BaseModel # type: ignore
from typing import Optional

class PublicationModel(BaseModel):
    id: str
    title: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[str] = None
    abstract: Optional[str] = None
    mission: Optional[str] = None
    organism: Optional[str] = None
    system: Optional[str] = None
    keywords: Optional[str] = None

    @staticmethod
    def from_dict(data: dict):
        """
        Membuat instance PublicationModel dari dictionary (row CSV)
        """
        return PublicationModel(
            id=data.get("id", ""),
            title=data.get("title"),
            authors=data.get("authors"),
            year=data.get("year"),
            abstract=data.get("abstract"),
            mission=data.get("mission"),
            organism=data.get("organism"),
            system=data.get("system"),
            keywords=data.get("keywords"),
        )
