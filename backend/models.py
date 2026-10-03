from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class CrawlRequest(BaseModel):
    url: HttpUrl

class ScoreBreakdown(BaseModel):
    ui_ux: float
    content: float
    structure: float
    overall: float

class CrawlResult(BaseModel):
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: List[str] = []
    h2: List[str] = []
    h3: List[str] = []
    images_total: int = 0
    images_with_alt: int = 0
    internal_links: int = 0
    external_links: int = 0
    word_count: int = 0
    main_text: str = ""
    has_viewport: bool = False
    has_canonical: bool = False
    load_time_ms: float = 0
    scores: ScoreBreakdown
    estimated_rank: int = 0
    serp_status: str = "Belum dicek"  # <-- Field baru ditambahkan di sini