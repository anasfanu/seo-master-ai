"""
DuckDuckGo SERP Tracker (Ringan & Tanpa API Key)
Mencari posisi URL target di hasil pencarian.
"""
import httpx
import warnings
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Supress warning SSL yang muncul saat verify=False
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

async def get_real_rank(keyword: str, target_url: str) -> dict:
    """
    Mencari keyword di DuckDuckGo dan mengecek di posisi berapa target_url muncul.
    """
    if not keyword or not target_url:
        return {"rank": None, "status": "Data tidak lengkap"}

    # Ambil domain utama dari URL (misal: https://web.com/halaman -> web.com)
    target_domain = urlparse(target_url).netloc.replace("www.", "")
    
    # URL pencarian DuckDuckGo versi HTML (sangat ringan)
    search_url = f"https://html.duckduckgo.com/html/?q={keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Tambahkan verify=False untuk mengabaikan error sertifikat SSL DuckDuckGo
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0, verify=False) as client:
            response = await client.get(search_url, headers=headers)
            
            if response.status_code != 200:
                return {"rank": None, "status": f"Gagal akses DuckDuckGo ({response.status_code})"}
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("a", class_="result__a", href=True)
            
            # Cek 30 hasil pertama
            for index, link in enumerate(results[:30], start=1):
                href = link["href"]
                # DuckDuckGo sering menggunakan redirect URL, kita cek domainnya
                if target_domain in href:
                    return {
                        "rank": index,
                        "status": "Ditemukan",
                        "found_url": href
                    }
            
            return {"rank": None, "status": "Tidak Terindeks (Tidak ada di 30 besar)"}

    except Exception as e:
        return {"rank": None, "status": f"Error: {str(e)}"}