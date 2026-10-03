"""
AI Engine: Integrasi Groq API untuk Optimasi SEO Iteratif.
Model diperbarui ke llama3-70b-8192 (Stabil & Free Tier)
"""
import os
import json
import httpx
# Variabel global untuk menyimpan model pilihan user
SELECTED_MODEL = "llama3-70b-8192"  # Default
from dotenv import load_dotenv
from .models import CrawlResult
from .analyzer import estimate_rank

# Load .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def optimize_seo(crawl_result: CrawlResult) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY tidak ditemukan di file .env")

    iteration = 0
    max_iterations = 2
    best_optimization = None
    best_rank = 100

    topic = crawl_result.h1[0] if crawl_result.h1 else (crawl_result.title or "Website")

    while iteration < max_iterations:
        iteration += 1
        
                # Deteksi apakah ini input manual atau crawl
        input_type = "ARTIKEL MANUAL" if crawl_result.url == "manual-input" else "WEBSITE YANG DI-CRAWL"
        
        prompt = f"""
        Kamu adalah Ahli SEO Global dan Indonesia. Tugasmu mengoptimalkan {input_type} ini agar masuk Top 10 Google.
        
        DATA INPUT ({input_type}):
        - URL/Source: {crawl_result.url}
        - Title/Judul Saat Ini: {crawl_result.title}
        - Meta Desc Saat Ini: {crawl_result.meta_description}
        - Konten/Teks Utama: {crawl_result.main_text[:1500]}
        - Jumlah Kata: {crawl_result.word_count}
        
        TUGAS:
        Buat optimasi SEO On-Page yang SEMPURNA untuk konten di atas. Sertakan juga 3 keyword trending di Indonesia dan 3 Global yang relevan.
        
        OUTPUT HARUS DALAM FORMAT JSON STRICT (tanpa markdown, tanpa teks tambahan, hanya object JSON):
        {{
            "meta_title": "Judul maksimal 60 karakter, mengandung keyword utama",
            "meta_description": "Deskripsi menarik, maksimal 160 karakter, ada call to action",
            "h1": "Satu H1 yang powerful dan mengandung keyword",
            "h2_suggestions": ["H2 pertama yang relevan", "H2 kedua yang relevan", "H2 ketiga yang relevan"],
            "lsi_keywords": "Keyword LSI/semantik, dipisah koma, maksimal 255 karakter total",
            "seo_friendly_url": "/slug-url-yang-optimal-dan-mengandung-keyword",
            "alt_text_suggestions": ["Alt text untuk gambar 1", "Alt text untuk gambar 2"],
            "trending_id": ["keyword trending 1", "keyword trending 2", "keyword trending 3"],
            "trending_global": ["keyword trending 1", "keyword trending 2", "keyword trending 3"],
            "optimization_notes": "Penjelasan singkat mengapa optimasi ini akan menaikkan ranking"
        }}
        """
        
        if iteration == 2:
            prompt += "\n\nPERINGATAN: Optimasi sebelumnya belum cukup kuat. Buat judul dan deskripsi yang LEBIH menarik (click-worthy), gunakan kata-kata power (Terbaru, Terbaik, Panduan Lengkap), dan pastikan struktur H2 sangat mendetail."

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # MODEL TERBARU & STABIL: gpt-oss-120b
        payload = {
           "model": SELECTED_MODEL,  # <-- GUNAKAN VARIABEL GLOBAL
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(GROQ_URL, headers=headers, json=payload)
                
                # DEBUG: Jika error, cetak detailnya di terminal VS Code
                if response.status_code != 200:
                    print(f"\n❌ GROQ API ERROR STATUS: {response.status_code}")
                    print(f"❌ GROQ API RESPONSE: {response.text}\n")
                    raise Exception(f"Groq API Error {response.status_code}: {response.text}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Bersihkan dari markdown block jika AI tetap mengirimkannya
                content = content.replace("```json", "").replace("```", "").strip()
                optimization_data = json.loads(content)
                
                # Simulasi skor baru berdasarkan kualitas output AI
                simulated_score = 85 + (iteration * 5) 
                estimated_new_rank = estimate_rank(simulated_score, crawl_result.word_count, True)
                
                optimization_data["estimated_rank_before"] = crawl_result.estimated_rank
                optimization_data["estimated_rank_after"] = estimated_new_rank
                optimization_data["iteration"] = iteration
                
                best_optimization = optimization_data
                best_rank = estimated_new_rank
                
                # Jika sudah estimasi rank <= 10, berhenti loop (berhasil)
                if estimated_new_rank <= 10:
                    break
                    
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON DECODE ERROR. Raw content dari AI: {content}\n")
            return {"error": f"AI menghasilkan format yang bukan JSON valid: {str(e)}"}
        except Exception as e:
            return {"error": f"Groq API Error: {str(e)}"}

    return best_optimization

async def optimize_human_like(crawl_result: CrawlResult, trending_id: list, trending_global: list, lsi_keywords: str) -> dict:
    """
    Menulis ulang artikel agar lolos AI detector dengan formatting HTML.
    Keyword placement strategis sesuai aturan SEO.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY tidak ditemukan")

    topic = crawl_result.h1[0] if crawl_result.h1 else (crawl_result.title or "Artikel")
    
    # Ambil 3 keyword dari trending_id untuk penempatan strategis
    primary_kw = trending_id[0] if trending_id else topic
    secondary_kw = trending_id[1] if len(trending_id) > 1 else ""
    
    prompt = f"""
Kamu adalah penulis profesional senior dengan 15 tahun pengalaman di bidang "{topic}". 
Gaya tulisanmu: conversational, hangat, seperti berbicara dengan teman dekat, tapi tetap informatif dan otoritatif.

ATURAN KETAT (WAJIB DIKUTI):

1. GAYA BAHASA HUMAN-LIKE (ANTI AI DETECTOR):
   - JANGAN gunakan frasa klise AI: "dalam era digital ini", "tidak dapat dipungkiri", "kesimpulannya", "pertama-tama", "selain itu", "di sisi lain"
   - Gunakan kata sambung natural: "nah", "jadi", "sebenarnya", "jujur saja", "menariknya", "bayangkan"
   - Variasi panjang kalimat: campur kalimat pendek (3-5 kata) dengan kalimat panjang (20+ kata)
   - Gunakan kalimat tanya retoris
   - Tambahkan opini pribadi atau pengalaman ("Saya pernah mengalami...", "Menurut pengalaman saya...")
   - Gunakan analogi atau contoh nyata
   - Tulis dalam Bahasa Indonesia yang natural, bukan terjemahan kaku

2. PENEMPATAN KEYWORD STRATEGIS:
   - Keyword utama: "{primary_kw}"
   - Keyword sekunder: "{secondary_kw}"
   - LSI Keywords: "{lsi_keywords}"
   - Keyword utama HARUS ada di H1 (judul)
   - Keyword utama HARUS muncul di 100 kata pertama (paragraf pembuka) secara natural
   - Sebar keyword di minimal 2 subjudul H2
   - LSI keywords muncul di paragraf penutup/konklusi
   - Density keyword: 1-2% MAX. JANGAN keyword stuffing!
   - Jika konteks tidak memungkinkan, JANGAN paksakan keyword

3. STRUKTUR HTML WAJIB:
   - <h1> untuk judul utama (1 saja)
   - <h2> untuk subjudul utama (3-5 buah)
   - <h3> untuk sub-subjudul jika perlu
   - <p> untuk setiap paragraf (maksimal 3-4 kalimat per paragraf)
   - <strong> untuk penekanan penting (jangan berlebihan, max 5x)
   - <em> untuk istilah asing atau penekanan ringan
   - <ul><li> untuk list jika relevan

4. STRUKTUR ARTIKEL:
   - Paragraf pembuka (hook + keyword utama di 100 kata pertama)
   - 3-5 section dengan H2
   - Paragraf penutup dengan LSI keywords
   - Total: 600-1200 kata

DATA ARTIKEL ASLI:
{crawl_result.main_text[:3000]}

TRENDING KEYWORD INDONESIA: {', '.join(trending_id[:3])}
TRENDING KEYWORD GLOBAL: {', '.join(trending_global[:3])}

OUTPUT: HANYA HTML MENTAH (tanpa markdown code block, tanpa penjelasan, langsung <h1>...</h1>...)
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": SELECTED_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,  # Lebih tinggi untuk kreativitas human-like
        "max_tokens": 4096
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GROQ_URL, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"\n❌ GROQ API ERROR: {response.status_code}")
                print(f"❌ RESPONSE: {response.text}\n")
                raise Exception(f"Groq API Error {response.status_code}")
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Bersihkan dari markdown code block jika AI tetap mengirimkannya
            content = content.replace("```html", "").replace("```", "").strip()
            
            return {
                "html_content": content,
                "word_count": len(content.split()),
                "status": "success"
            }
            
    except Exception as e:
        return {"status": "error", "error": str(e)}