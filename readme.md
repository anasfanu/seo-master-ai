# 🚀 SEO Master AI by anasfanu

<p align="center">
  <strong>Tools Optimasi SEO Lokal Berbasis AI (Groq) untuk Crawling, Analisis SERP, dan Penulisan Artikel Human-like.</strong>
</p>

---

## ✨ Tentang Proyek

**SEO Master AI** adalah aplikasi web lokal yang dirancang untuk membantu blogger, content writer, dan SEO specialist mengoptimalkan halaman website atau artikel secara mendalam. 

Aplikasi ini menggunakan kekuatan AI (**Llama 3 via Groq**) untuk menganalisis struktur on-page, melacak posisi SERP secara real-time, dan menulis ulang artikel agar lolos dari deteksi AI.

---

## 🛠️ Tech Stack

Aplikasi ini dibangun menggunakan kombinasi teknologi modern:

*   **Backend:** Python 🐍, FastAPI, httpx, BeautifulSoup4, Trafilatura
*   **AI Engine:** Groq API (Llama 3)
*   **Frontend:** HTML5, Tailwind CSS, Alpine.js
*   **SERP Tracking:** DuckDuckGo HTML Scraping *(Tanpa perlu API Key)*

---

## ✨ Fitur Utama

### 1. Dual Mode Input
*   **🌐 Crawl Website:** Ekstrak data SEO langsung dari URL target secara otomatis, sangat ringan dan hemat RAM.
*   **📝 Input Artikel Manual:** Tempel (*paste*) teks artikel mentah dari Word atau Notepad untuk langsung dianalisis.

### 2. Analisis & Pelacakan Real-Time
*   **Skor On-Page:** Menghitung persentase UI/UX, Kualitas Konten, dan Struktur Halaman.
*   **SERP Tracker:** Melacak posisi URL target di mesin pencari DuckDuckGo secara *real-time*.
*   **Estimasi Ranking Realistis:** Menggunakan algoritma multi-faktor untuk memprediksi potensi posisi halaman setelah dioptimasi.

### 3. AI-Powered Optimization
*   **Optimasi On-Page Lengkap:** Menghasilkan Meta Title, Meta Description, Tag H1-H3, SEO Friendly URL, LSI Keywords, dan Alt Text.
*   **Tren Keyword Kontekstual:** Mendeteksi keyword trending Indonesia & Global yang relevan dengan topik Anda.
*   **Iterative Loop:** AI otomatis melakukan revisi berkelanjutan hingga estimasi ranking mencapai target Top 10.

### 4. Human-like Article Rewriter (Anti-AI Detector)
*   Menulis ulang artikel dengan gaya bahasa manusia yang *conversational*, variatif, dan natural.
*   **Strategi Penempatan Keyword:** Otomatis menanamkan keyword utama di H1, 100 kata pertama, H2/H3, dan LSI di bagian kesimpulan.
*   **Output HTML Rapi:** Menghasilkan artikel lengkap dengan tag `<p>`, `<strong>`, `<em>`, dan heading yang siap diterbitkan ke WordPress atau Blogger.

### 5. UI/UX Modern & Privasi Terjaga
*   **Dark Mode & Responsive:** Tampilan visual yang nyaman di mata menggunakan Tailwind CSS & Alpine.js.
*   **100% Lokal & Privat:** Semua data dan API Key hanya tersimpan di komputer Anda sendiri.
*   **Export HTML:** Unduh laporan SEO lengkap atau artikel hasil rewrite hanya dalam satu klik.

---

## 📦 Instalasi & Setup

### Prasyarat
*   Python 3.11 atau 3.12
*   Akun Groq (Dapatkan API Key gratis di [://groq.com](https://://groq.com))

### Langkah-langkah

1. **Clone atau Download proyek ini**
   ```bash
   git clone https://github.com
   cd seo-master-ai
   ```

2. **Buat Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Aktifkan Virtual Environment**
   *   **Windows:**
       ```bash
       venv\Scripts\activate
       ```
   *   **Mac/Linux:**
       ```bash
       source venv/bin/activate
       ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Setup Environment Variables**
   Salin file `.env.example` menjadi `.env`, lalu masukkan API Key Groq Anda:
   ```env
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

6. **Jalankan Aplikasi**
   ```bash
   python run.py
   ```
   Aplikasi akan otomatis terbuka di browser Anda pada alamat: `http://localhost:8000`

---

## 📖 Cara Penggunaan

1. **Pilih Mode:** Klik tab **Crawl Website** untuk menganalisis URL, atau **Input Artikel Manual** untuk teks mentah.
2. **Load Model:** Klik tombol **1. Load Model** untuk mengambil daftar model AI aktif dari Groq.
3. **Proses SEO:** Klik tombol **Crawling & Optimasi SEO**. Tunggu hingga analisis awal, skor, dan prediksi ranking muncul.
4. **Tinjau Hasil:** Salin Meta Tags, H1, H2, dan LSI Keywords optimal yang disarankan oleh sistem.
5. **Tulis Ulang (Opsional):** Klik tombol ungu **✨ Tulis Ulang Artikel** untuk menghasilkan konten yang lolos AI Detector. Tab baru akan terbuka menampilkan artikel HTML yang siap di-export.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE.md).
