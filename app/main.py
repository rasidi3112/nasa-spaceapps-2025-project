# app/main.py
import os
from typing import List, Optional
from fastapi import FastAPI, Query # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.responses import FileResponse # type: ignore
from pydantic import BaseModel # type: ignore
from app.utils.embedding import semantic_search
from app.utils.summarizer import generate_summary # type: ignore
from app.utils.graph import fetch_subgraph
from app.utils.persona import personalize_insights
from app.db import get_publication_by_id, list_publications

app = FastAPI(
    title="AstroBio Insight Navigator API",
    description="API untuk eksplorasi publikasi biosains NASA",
    version="1.0.0",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# === Serve Static Files ====
# ============================
# Mount folder "static" untuk serve file HTML, CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route default ke index.html
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# ============================
# ====== Data Models =========
# ============================
class Publication(BaseModel):
    id: str
    title: str
    authors: List[str]
    year: int
    abstract: Optional[str]
    mission: Optional[str]
    organism: Optional[str]
    system: Optional[str]
    keywords: List[str]

class SummaryRequest(BaseModel):
    publication_id: str
    focus_section: Optional[str] = None  # intro, results, conclusion
    persona: Optional[str] = "scientist" # scientist, manager, architect

class SummaryResponse(BaseModel):
    bullet_summary: List[str]
    key_findings: List[str]
    risk_assessment: List[str]
    recommended_actions: List[str]

class SearchResponse(BaseModel):
    query: str
    results: List[Publication]

class GraphResponse(BaseModel):
    nodes: List[dict]
    edges: List[dict]

class InsightResponse(BaseModel):
    persona: str
    insights: List[str]
    suggested_publications: List[str]

# ============================
# ====== API Endpoints =======
# ============================

@app.get("/publications", response_model=List[Publication])
async def get_publications(
    page: int = 1, 
    page_size: int = 20,
    organism: Optional[str] = None,
    mission: Optional[str] = None,
    system: Optional[str] = None,
):
    return list_publications(page, page_size, organism, mission, system)

@app.get("/publications/{pub_id}", response_model=Publication)
async def get_publication(pub_id: str):
    return get_publication_by_id(pub_id)

@app.get("/search", response_model=SearchResponse)
async def search_publications(
    q: str = Query(..., min_length=2, description="Kata kunci atau pertanyaan"),
    top_k: int = 10
):
    results = semantic_search(q, top_k)
    return SearchResponse(query=q, results=results)

@app.post("/summary", response_model=SummaryResponse)
async def summarize_publication(req: SummaryRequest):
    publication = get_publication_by_id(req.publication_id)
    return generate_summary(publication, req.focus_section, req.persona)

@app.get("/graph", response_model=GraphResponse)
async def knowledge_graph(
    seed: str,
    depth: int = 2,
    filter_mission: Optional[str] = None
):
    return fetch_subgraph(seed, depth, filter_mission)

@app.get("/insights", response_model=InsightResponse)
async def persona_insights(persona: str = "scientist"):
    return personalize_insights(persona)
