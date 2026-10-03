"""
FastAPI entry point - endpoint untuk crawling, analisis, dan optimasi AI.
Mendukung Crawl URL, Input Artikel Manual, dan Human-like Rewriting.
"""
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
import httpx
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Import modul lokal kita
from .crawler import crawl
from .models import CrawlResult, ScoreBreakdown
from .analyzer import calculate_scores, estimate_rank
from . import ai_engine

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(title="SEO Master AI", version="4.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@app.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/api/models")
async def get_available_models():
    """Mengambil daftar model Groq yang tersedia."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=400, detail="GROQ_API_KEY tidak ditemukan")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
            )
            if response.status_code == 200:
                data = response.json()
                models = [m["id"] for m in data["data"] if "whisper" not in m["id"] and "llava" not in m["id"]]
                return {"models": models}
            else:
                raise HTTPException(status_code=response.status_code, detail="Gagal mengambil model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Model Request (TANPA auth_key)
class OptimizeRequest(BaseModel):
    url: Optional[str] = None
    article_text: Optional[str] = None
    model: str = "llama3-70b-8192"

def analyze_html_content(html_content: str, title: str = "") -> dict:
    """
    Menganalisis HTML hasil tulis ulang untuk menghasilkan skor.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract headings
    h1 = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2 = [h.get_text(strip=True) for h in soup.find_all("h2")]
    h3 = [h.get_text(strip=True) for h in soup.find_all("h3")]
    
    # Extract paragraphs dan hitung kata
    paragraphs = soup.find_all("p")
    main_text = " ".join([p.get_text(strip=True) for p in paragraphs])
    word_count = len(main_text.split()) if main_text else len(html_content.split())
    
    # Hitung images dan alt text
    images = soup.find_all("img")
    images_total = len(images)
    images_with_alt = sum(1 for img in images if img.get("alt", "").strip())
    
    # Hitung links
    links = soup.find_all("a", href=True)
    internal_links = 0
    external_links = 0
    for a in links:
        href = a["href"]
        if href.startswith(("http://", "https://")):
            external_links += 1
        else:
            internal_links += 1
    
    # Buat HTML sederhana untuk analisis rasio teks
    simple_html = f"<html><body>{html_content}</body></html>"
    
    # Hitung skor menggunakan analyzer yang sudah ada
    scores = calculate_scores(
        html=simple_html,
        main_text=main_text,
        word_count=word_count,
        h1=h1, h2=h2, h3=h3,
        images_total=images_total,
        images_with_alt=images_with_alt,
        has_viewport=True,
        has_canonical=False,
        title=title,
        meta_description=None,
        load_time_ms=0
    )
    
    estimated_rank = estimate_rank(scores.overall, word_count, True)
    
    return {
        "scores": scores,
        "word_count": word_count,
        "h1_count": len(h1),
        "h2_count": len(h2),
        "h3_count": len(h3),
        "paragraph_count": len(paragraphs),
        "estimated_rank": estimated_rank
    }

@app.post("/api/optimize")
async def api_optimize(req: OptimizeRequest):
    """Optimasi SEO dari URL Website atau Teks Artikel Manual."""
    
    if not req.url and not req.article_text:
        raise HTTPException(status_code=400, detail="URL atau Artikel Manual wajib diisi!")
    
    crawl_result = None
    keyword_for_search = ""

    try:
        # 1. Crawl atau Parse Manual
        if req.url:
            crawl_result = await crawl(req.url)
            keyword_for_search = crawl_result.h1[0] if crawl_result.h1 else (crawl_result.title or "")
        elif req.article_text:
            text = req.article_text.strip()
            word_count = len(text.split())
            temp_title = text.split('\n')[0].strip()[:100] if text else "Artikel Manual"
            keyword_for_search = temp_title 
            
            crawl_result = CrawlResult(
                url="manual-input", title=temp_title, meta_description=None,
                h1=[temp_title], h2=[], h3=[],
                images_total=0, images_with_alt=0,
                internal_links=0, external_links=0,
                word_count=word_count, main_text=text[:5000],
                has_viewport=True, has_canonical=False, load_time_ms=0,
                scores=ScoreBreakdown(ui_ux=0, content=0, structure=0, overall=0),
                estimated_rank=100,
                serp_status="Belum dicek"
            )

        # 2. Lakukan Pelacakan SERP Real-time (DuckDuckGo)
        from .serp_tracker import get_real_rank
        clean_keyword = keyword_for_search[:50] 
        serp_data = await get_real_rank(clean_keyword, req.url if req.url else "manual-input")
        
        # 3. Update data crawl_result
        if serp_data["rank"]:
            crawl_result = crawl_result.model_copy(update={
                "estimated_rank": serp_data["rank"],
                "serp_status": serp_data["status"]
            })
        else:
            crawl_result = crawl_result.model_copy(update={
                "serp_status": serp_data["status"]
            })

        # 4. Jalankan AI Engine
        ai_engine.SELECTED_MODEL = req.model
        optimization = await ai_engine.optimize_seo(crawl_result)
        
        if "error" in optimization:
            raise HTTPException(status_code=500, detail=optimization["error"])
            
        # 5. Hitung Estimasi Rank Baru
        has_keyword = False
        if crawl_result.title:
            has_keyword = optimization.get("meta_title", "").lower() in crawl_result.title.lower()
            
        optimization["estimated_rank_after"] = estimate_rank(
            optimization.get("simulated_score", 85), 
            crawl_result.word_count, 
            has_keyword
        )
        optimization["serp_data"] = serp_data 
            
        return {
            "original_data": crawl_result,
            "optimization": optimization
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Website tidak bisa diakses: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/optimize-human")
async def api_optimize_human(req: OptimizeRequest):
    """Optimasi artikel agar human-like dan lolos AI detector."""
    
    if not req.url and not req.article_text:
        raise HTTPException(status_code=400, detail="URL atau Artikel Manual wajib diisi!")
    
    crawl_result = None

    try:
        # 1. Crawl atau Parse Manual
        if req.url:
            crawl_result = await crawl(req.url)
        elif req.article_text:
            text = req.article_text.strip()
            word_count = len(text.split())
            temp_title = text.split('\n')[0].strip()[:100] if text else "Artikel Manual"
            
            crawl_result = CrawlResult(
                url="manual-input", title=temp_title, meta_description=None,
                h1=[temp_title], h2=[], h3=[],
                images_total=0, images_with_alt=0,
                internal_links=0, external_links=0,
                word_count=word_count, main_text=text[:5000],
                has_viewport=True, has_canonical=False, load_time_ms=0,
                scores=ScoreBreakdown(ui_ux=0, content=0, structure=0, overall=0),
                estimated_rank=100,
                serp_status="Belum dicek"
            )

        # 2. Jalankan AI Engine untuk optimasi SEO biasa dulu (dapatkan keyword)
        ai_engine.SELECTED_MODEL = req.model
        seo_optimization = await ai_engine.optimize_seo(crawl_result)
        
        if "error" in seo_optimization:
            raise HTTPException(status_code=500, detail=seo_optimization["error"])
        
        # 3. Jalankan Human-like Rewriter dengan keyword dari hasil SEO
        human_result = await ai_engine.optimize_human_like(
            crawl_result=crawl_result,
            trending_id=seo_optimization.get("trending_id", []),
            trending_global=seo_optimization.get("trending_global", []),
            lsi_keywords=seo_optimization.get("lsi_keywords", "")
        )
        
        if human_result.get("status") == "error":
            raise HTTPException(status_code=500, detail=human_result["error"])
        
        # 4. Analisis skor untuk artikel hasil tulis ulang
        html_content = human_result["html_content"]
        title = seo_optimization.get("meta_title", crawl_result.title or "")
        analysis = analyze_html_content(html_content, title)
        
        return {
            "human_html": html_content,
            "word_count": human_result["word_count"],
            "seo_data": seo_optimization,
            "analysis": analysis  # <-- Skor analisis artikel hasil tulis ulang
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Website tidak bisa diakses: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")