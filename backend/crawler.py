"""
Crawler ringan - tanpa Playwright (hemat RAM).
Menggunakan httpx + trafilatura + BeautifulSoup.
"""
import time
import httpx
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .models import CrawlResult, ScoreBreakdown

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEO-Master-AI/1.0)",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

async def crawl(url: str) -> CrawlResult:
    """Crawl website target dan ekstrak semua data SEO."""
    start = time.time()
    
    async with httpx.AsyncClient(
        headers=HEADERS, 
        follow_redirects=True, 
        timeout=15.0
    ) as client:
        response = await client.get(str(url))
        response.raise_for_status()
    
    load_time_ms = (time.time() - start) * 1000
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    
    # Extract main content dengan trafilatura (paling mirip cara Google baca)
    main_text = trafilatura.extract(
        html, 
        include_comments=False, 
        include_tables=True,
        favor_precision=True
    ) or ""
    
    # Meta tags
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else None
    
    # Headings
    h1 = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2 = [h.get_text(strip=True) for h in soup.find_all("h2")]
    h3 = [h.get_text(strip=True) for h in soup.find_all("h3")]
    
    # Images
    images = soup.find_all("img")
    images_total = len(images)
    images_with_alt = sum(1 for img in images if img.get("alt", "").strip())
    
    # Links
    domain = urlparse(str(url)).netloc
    internal_links = 0
    external_links = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("http://", "https://")):
            if domain in href:
                internal_links += 1
            else:
                external_links += 1
        elif href.startswith("/"):
            internal_links += 1
    
    # Technical SEO checks
    has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
    has_canonical = bool(soup.find("link", attrs={"rel": "canonical"}))
    
    word_count = len(main_text.split())
    
    # Hitung skor (dipisah ke analyzer untuk kebersihan kode)
    from .analyzer import calculate_scores, estimate_rank
    
    scores = calculate_scores(
            html=html,
            main_text=main_text,
            word_count=word_count,
            h1=h1, h2=h2, h3=h3,
            images_total=images_total,
            images_with_alt=images_with_alt,
            has_viewport=has_viewport,
            has_canonical=has_canonical,
            title=title,
            meta_description=meta_description,
            load_time_ms=load_time_ms
        )
        
    estimated_rank = estimate_rank(scores.overall, word_count, False)
    
    return CrawlResult(
        url=str(url),
        title=title,
        meta_description=meta_description,
        h1=h1, h2=h2, h3=h3,
        images_total=images_total,
        images_with_alt=images_with_alt,
        internal_links=internal_links,
        external_links=external_links,
        word_count=word_count,
        main_text=main_text[:5000],  # batasi 5000 char agar hemat RAM & token AI
        has_viewport=has_viewport,
        has_canonical=has_canonical,
        load_time_ms=round(load_time_ms, 2),
        scores=scores,
        estimated_rank=estimated_rank
    )