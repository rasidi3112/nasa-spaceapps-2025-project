# app/utils/embedding.py
from typing import List
from sentence_transformers import SentenceTransformer  # type: ignore
import numpy as np  # type: ignore
import qdrant_client  # type: ignore
from app.publication_model import PublicationModel
from app.db import get_publication_by_id
from ..db import get_publication_by_id  # naik satu folder ke app/

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_vector_model = SentenceTransformer(MODEL_NAME)
_qdrant = qdrant_client.QdrantClient(url="http://localhost:6333")
_COLLECTION = "nasa_bioscience"

def semantic_search(query: str, top_k: int) -> List[PublicationModel]:  # type: ignore
    """
    Cari publikasi paling relevan menggunakan embedding query.
    """
    query_vector = _vector_model.encode(query).tolist()
    hits = _qdrant.search(
        collection_name=_COLLECTION,
        query_vector=query_vector,
        limit=top_k
    )

    results: List[PublicationModel] = [] # type: ignore
    for hit in hits:
        pub_id = hit.payload.get("id")
        try:
            pub = get_publication_by_id(pub_id)
            results.append(pub)
        except Exception:
            # skip jika id tidak ditemukan
            continue

    return results
