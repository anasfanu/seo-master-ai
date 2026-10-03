"""
Script runner - jalankan backend + serve frontend sekaligus.
Hemat resource, cocok untuk PC 4GB RAM.
"""
import uvicorn
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("\n🚀 SEO Master AI Starting...")
    print("📍 Frontend: http://localhost:8000")
    print("📍 API Docs:  http://localhost:8000/docs")
    print("⚙️  Workers: 1 (hemat RAM)\n")
    
    # Buka browser otomatis setelah 2 detik
    Timer(2, open_browser).start()
    
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        workers=1,        # 1 worker = hemat RAM
        log_level="info"
    )