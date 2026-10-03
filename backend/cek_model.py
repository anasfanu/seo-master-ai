import requests
import os
from dotenv import load_dotenv

# 1. Load file .env agar API key terbaca
load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("❌ ERROR: GROQ_API_KEY tidak ditemukan di file .env")
else:
    print(f"✅ API Key terbaca: {api_key[:10]}... (disembunyikan demi keamanan)")

    # 2. Setup request ke Groq
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 3. Kirim request
    response = requests.get(url, headers=headers)

    # 4. Tampilkan hasil
    if response.status_code == 200:
        models_data = response.json()["data"]
        print("\n" + "="*50)
        print("✅ BERHASIL! Daftar Model Text-Generation yang Tersedia:")
        print("="*50)
        
        for model in models_data:
            model_id = model["id"]
            # Kita filter hanya model yang relevan untuk chat/text (bukan model vision/audio)
            if "whisper" not in model_id and "llava" not in model_id:
                print(f"👉 {model_id}")
                
        print("="*50)
        print("💡 SALIN salah satu nama model di atas (misal: llama3-70b-8192)")
    else:
        print(f"\n❌ GAGAL MENGAMBIL DATA: Status {response.status_code}")
        print(response.text)