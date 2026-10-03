"""
Analyzer: menghitung skor SEO berdasarkan heuristik algoritma Google.
Faktor: UI/UX, Content Quality, Technical Structure.
"""
from .models import ScoreBreakdown

def calculate_scores(
    html: str,
    main_text: str,
    word_count: int,
    h1: list, h2: list, h3: list,
    images_total: int,
    images_with_alt: int,
    has_viewport: bool,
    has_canonical: bool,
    title,
    meta_description,
    load_time_ms: float
) -> ScoreBreakdown:
    
    # ===== UI/UX SCORE =====
    ui_score = 0
    # Viewport mobile (25%)
    if has_viewport: ui_score += 25
    # Load time < 2s = bagus (25%)
    if load_time_ms < 2000: ui_score += 25
    elif load_time_ms < 4000: ui_score += 15
    else: ui_score += 5
    # HTML size reasonable < 500KB (20%)
    html_size_kb = len(html.encode()) / 1024
    if html_size_kb < 500: ui_score += 20
    elif html_size_kb < 1500: ui_score += 10
    # Text-to-HTML ratio > 10% (15%)
    text_len = len(main_text)
    html_len = len(html)
    ratio = (text_len / html_len * 100) if html_len > 0 else 0
    if ratio > 15: ui_score += 15
    elif ratio > 8: ui_score += 10
    elif ratio > 3: ui_score += 5
    # Canonical (15%)
    if has_canonical: ui_score += 15
    
    # ===== CONTENT SCORE =====
    content_score = 0
    # Word count ideal 600-2500 (35%)
    if 600 <= word_count <= 2500: content_score += 35
    elif 300 <= word_count < 600: content_score += 20
    elif word_count > 2500: content_score += 25
    elif word_count > 100: content_score += 10
    # Title exists & 50-60 char (25%)
    if title:
        t_len = len(title)
        if 50 <= t_len <= 60: content_score += 25
        elif 30 <= t_len <= 70: content_score += 18
        elif t_len > 0: content_score += 10
    # Meta desc exists & 120-160 char (25%)
    if meta_description:
        d_len = len(meta_description)
        if 120 <= d_len <= 160: content_score += 25
        elif 80 <= d_len <= 160: content_score += 18
        elif d_len > 0: content_score += 10
    # Paragraph structure (15%)
    paragraphs = main_text.count('\n\n') + main_text.count('</p>')
    if paragraphs >= 5: content_score += 15
    elif paragraphs >= 2: content_score += 8
    
    # ===== STRUCTURE SCORE =====
    struct_score = 0
    # H1 exactly 1 (30%)
    if len(h1) == 1: struct_score += 30
    elif len(h1) == 0: struct_score += 0
    else: struct_score += 10  # multiple H1 = penalty
    # H2 exists 2-8 (25%)
    if 2 <= len(h2) <= 8: struct_score += 25
    elif len(h2) > 0: struct_score += 15
    # H3 exists (15%)
    if len(h3) >= 1: struct_score += 15
    # Image alt ratio 100% (20%)
    if images_total == 0:
        struct_score += 20  # no image = no penalty
    else:
        alt_ratio = images_with_alt / images_total
        struct_score += int(alt_ratio * 20)
    # Heading hierarchy valid (10%)
    if h1 and h2: struct_score += 10
    
    overall = (ui_score + content_score + struct_score) / 3
    
    return ScoreBreakdown(
        ui_ux=round(min(ui_score, 100), 1),
        content=round(min(content_score, 100), 1),
        structure=round(min(struct_score, 100), 1),
        overall=round(min(overall, 100), 1)
    )

def estimate_rank(overall_score: float, word_count: int, has_keyword_in_title: bool, current_rank: int = None) -> int:
    """
    Algoritma estimasi ranking yang REALISTIS dengan mempertimbangkan:
    1. Skor on-page quality
    2. Panjang konten
    3. Optimasi keyword
    4. Ranking saat ini (jika ada)
    """
    
    # Hitung base rank dari skor on-page
    if overall_score >= 90: base_rank = 5
    elif overall_score >= 80: base_rank = 12
    elif overall_score >= 70: base_rank = 25
    elif overall_score >= 60: base_rank = 45
    else: base_rank = 80

    # Bonus jika artikel panjang (>1000 kata)
    if word_count > 1000:
        base_rank -= 5
    
    # Bonus jika keyword ada di title
    if has_keyword_in_title:
        base_rank -= 3

    # LOGIKA PENTING: Jika ada current_rank dari SERP, gunakan sebagai referensi
    if current_rank and current_rank < 100:
        # Jika sudah ranking, prediksi harus realistis
        if overall_score >= 85:
            # On-page bagus, pertahankan atau naikkan sedikit
            predicted_rank = min(current_rank, base_rank)
        elif overall_score >= 70:
            # On-page sedang, mungkin ranking karena faktor lain (backlink)
            # Prediksi: bisa turun jika tidak dioptimasi, atau stabil
            predicted_rank = min(current_rank + 5, base_rank)
        else:
            # On-page jelek tapi ranking? Mungkin temporary
            # Prediksi: akan turun kecuali dioptimasi
            predicted_rank = min(current_rank + 10, base_rank)
    else:
        # Tidak ada ranking saat ini, gunakan base_rank
        predicted_rank = base_rank

    # Tambahkan variasi acak kecil (realistis)
    import random
    variation = random.randint(-2, 3)
    
    final_rank = max(1, predicted_rank + variation)
    return final_rank