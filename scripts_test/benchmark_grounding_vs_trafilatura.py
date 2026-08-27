"""
Benchmark Script: Google Search Grounding vs Trafilatura Direct Extraction
So sánh thực nghiệm:
- Phương pháp A: Gemini 2.5 Flash + Google Search Grounding (Hiện tại)
- Phương pháp B: Trafilatura bóc tách text trực tiếp + Gemini 2.5 Flash (Không Grounding)
"""

import os
import sys
import time
import json
import logging
from dotenv import load_dotenv

# Thêm đường dẫn root vào sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import trafilatura
from google import genai
from google.genai import types
from utils.rss_crawler import fetch_rss

# Load environment
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Khởi tạo Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
model_name = 'gemini-2.5-flash'

# Config có Google Search
grounding_tool = types.Tool(google_search=types.GoogleSearch())
config_with_search = types.GenerateContentConfig(
    tools=[grounding_tool],
    temperature=0.1,
    max_output_tokens=1024,
)

# Config không có Search (nhận text trực tiếp)
config_direct = types.GenerateContentConfig(
    temperature=0.1,
    max_output_tokens=1024,
)


def method_a_search_grounding(title: str, url: str):
    """Phương pháp A: Gemini + Google Search Grounding"""
    prompt = f"""
SỬ DỤNG GOOGLE SEARCH ĐỂ TÌM VÀ ĐỌC NỘI DUNG BÀI BÁO SAU:
URL: {url}
Tiêu đề: "{title}"

SAU KHI ĐỌC NỘI DUNG THỰC TẾ, phân tích:
- POSITIVE (sentiment = 1): Thành tựu, việc tốt, chữa bệnh, giáo dục, văn hóa, vượt khó.
- NEUTRAL (sentiment = 0): Thống kê, thủ tục, cảnh báo lừa đảo/tội phạm có ích.
- NEGATIVE (sentiment = -1): Tử vong, tai nạn nghiêm trọng, tội phạm bạo lực.
- TOXIC (is_toxic = true): Kích động thù hận, 18+, bạo lực thô tục, tin giả.

OUTPUT JSON:
{{"description": "Tóm tắt 1-2 câu tiếng Việt (max 200 chars)", "is_toxic": boolean, "sentiment": 1, 0 hoặc -1}}
CHỈ TRẢ JSON.
"""
    start_time = time.time()
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config_with_search,
        )
        elapsed = time.time() - start_time
        
        grounding_used = False
        if response.candidates and response.candidates[0].grounding_metadata:
            gm = response.candidates[0].grounding_metadata
            if gm.web_search_queries:
                grounding_used = True

        usage = response.usage_metadata if hasattr(response, 'usage_metadata') else None
        prompt_tokens = usage.prompt_token_count if usage else 0
        cand_tokens = usage.candidates_token_count if usage else 0

        return {
            "success": True,
            "latency": elapsed,
            "text": response.text.strip() if response.text else "",
            "grounding_used": grounding_used,
            "prompt_tokens": prompt_tokens,
            "candidate_tokens": cand_tokens,
            "total_tokens": prompt_tokens + cand_tokens
        }
    except Exception as e:
        return {"success": False, "error": str(e), "latency": time.time() - start_time}


def method_b_trafilatura(title: str, url: str):
    """Phương pháp B: Trafilatura bóc tách text + Gemini trực tiếp"""
    start_total = time.time()
    
    # Bước 1: Trafilatura fetch & extract
    start_extract = time.time()
    downloaded = trafilatura.fetch_url(url)
    extracted_text = trafilatura.extract(downloaded, include_comments=False, include_tables=False) if downloaded else ""
    extract_time = time.time() - start_extract

    if not extracted_text:
        extracted_text = title  # Fallback nếu không bóc tách được

    # Giới hạn 2000 ký tự đầu để tối ưu token
    clean_content = extracted_text[:2000]

    # Bước 2: Gửi text sạch sang Gemini
    prompt = f"""
ĐÂY LÀ NỘI DUNG THỰC TẾ BÀI BÁO:
Tiêu đề: "{title}"
Nội dung bài báo:
\"\"\"
{clean_content}
\"\"\"

DỰA TRÊN NỘI DUNG TRÊN, phân tích:
- POSITIVE (sentiment = 1): Thành tựu, việc tốt, chữa bệnh, giáo dục, văn hóa, vượt khó.
- NEUTRAL (sentiment = 0): Thống kê, thủ tục, cảnh báo lừa đảo/tội phạm có ích.
- NEGATIVE (sentiment = -1): Tử vong, tai nạn nghiêm trọng, tội phạm bạo lực.
- TOXIC (is_toxic = true): Kích động thù hận, 18+, bạo lực thô tục, tin giả.

OUTPUT JSON:
{{"description": "Tóm tắt 1-2 câu tiếng Việt (max 200 chars)", "is_toxic": boolean, "sentiment": 1, 0 hoặc -1}}
CHỈ TRẢ JSON.
"""
    start_llm = time.time()
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config_direct,
        )
        llm_time = time.time() - start_llm
        total_time = time.time() - start_total

        usage = response.usage_metadata if hasattr(response, 'usage_metadata') else None
        prompt_tokens = usage.prompt_token_count if usage else 0
        cand_tokens = usage.candidates_token_count if usage else 0

        return {
            "success": True,
            "extract_time": extract_time,
            "llm_time": llm_time,
            "total_latency": total_time,
            "extracted_chars": len(extracted_text),
            "text": response.text.strip() if response.text else "",
            "prompt_tokens": prompt_tokens,
            "candidate_tokens": cand_tokens,
            "total_tokens": prompt_tokens + cand_tokens
        }
    except Exception as e:
        return {"success": False, "error": str(e), "total_latency": time.time() - start_total}


def run_benchmark(num_articles=3):
    print("=" * 80, flush=True)
    print(f"🚀 BẮT ĐẦU BENCHMARK: SEARCH GROUNDING vs TRAFILATURA ({num_articles} BÀI BÁO THỰC TẾ)", flush=True)
    print("=" * 80, flush=True)

    # 1. Lấy bài báo mới nhất từ RSS VnExpress
    print("📡 Đang lấy bài báo mới nhất từ RSS VnExpress...", flush=True)
    entries = fetch_rss("https://vnexpress.net/rss/tin-moi-nhat.rss")
    if not entries:
        print("❌ Không lấy được tin RSS!", flush=True)
        return

    test_articles = entries[:num_articles]
    print(f"✅ Đã chọn {len(test_articles)} bài báo mới nhất.\n", flush=True)

    results_a = []
    results_b = []

    for i, article in enumerate(test_articles, 1):
        title = article.get('title', '')
        link = article.get('link', '')

        print("-" * 80, flush=True)
        print(f"[{i}/{num_articles}] 📰 {title[:70]}...", flush=True)
        print(f"🔗 URL: {link}", flush=True)

        # Test Phương pháp A (Search Grounding)
        print("  ⏳ [Phương pháp A] Chạy Gemini + Google Search Grounding...", flush=True)
        res_a = method_a_search_grounding(title, link)
        results_a.append(res_a)
        if res_a['success']:
            print(f"     ⏱️ Thời gian: {res_a['latency']:.2f}s | Search Triggered: {res_a['grounding_used']} | Tokens: {res_a['total_tokens']}", flush=True)
            print(f"     💬 Output: {res_a['text']}", flush=True)
        else:
            print(f"     ❌ Lỗi: {res_a.get('error')}", flush=True)

        time.sleep(0.5)

        # Test Phương pháp B (Trafilatura)
        print("  ⏳ [Phương pháp B] Chạy Trafilatura + Gemini Direct...", flush=True)
        res_b = method_b_trafilatura(title, link)
        results_b.append(res_b)
        if res_b['success']:
            print(f"     ⏱️ Thời gian: {res_b['total_latency']:.2f}s (Extract: {res_b['extract_time']:.2f}s + LLM: {res_b['llm_time']:.2f}s) | Chars bóc tách: {res_b['extracted_chars']} | Tokens: {res_b['total_tokens']}", flush=True)
            print(f"     💬 Output: {res_b['text']}", flush=True)
        else:
            print(f"     ❌ Lỗi: {res_b.get('error')}", flush=True)

        print(flush=True)
        time.sleep(0.5)

    # Tổng kết
    print("=" * 80, flush=True)
    print("📊 BẢNG TỔNG KẾT SO SÁNH HIỆU NĂNG THỰC TẾ:", flush=True)
    print("=" * 80, flush=True)

    valid_a = [r for r in results_a if r['success']]
    valid_b = [r for r in results_b if r['success']]

    avg_lat_a = sum(r['latency'] for r in valid_a) / len(valid_a) if valid_a else 0
    avg_lat_b = sum(r['total_latency'] for r in valid_b) / len(valid_b) if valid_b else 0
    avg_extract_b = sum(r['extract_time'] for r in valid_b) / len(valid_b) if valid_b else 0
    avg_llm_b = sum(r['llm_time'] for r in valid_b) / len(valid_b) if valid_b else 0

    avg_tokens_a = sum(r['total_tokens'] for r in valid_a) / len(valid_a) if valid_a else 0
    avg_tokens_b = sum(r['total_tokens'] for r in valid_b) / len(valid_b) if valid_b else 0

    print(f"1. ⏱️ THỜI GIAN TRUNG BÌNH MỖI BÀI:", flush=True)
    print(f"   - Phương pháp A (Search Grounding): {avg_lat_a:.2f} giây", flush=True)
    print(f"   - Phương pháp B (Trafilatura):      {avg_lat_b:.2f} giây (Extract: {avg_extract_b:.2f}s, LLM: {avg_llm_b:.2f}s)", flush=True)
    if avg_lat_b > 0 and avg_lat_a > 0:
        speedup = ((avg_lat_a - avg_lat_b) / avg_lat_a) * 100
        print(f"   👉 Trafilatura NHANH HƠN: {speedup:.1f}%", flush=True)

    print(f"\n2. 🪙 TOKEN TIÊU THỤ TRUNG BÌNH:", flush=True)
    print(f"   - Phương pháp A (Search Grounding): ~{avg_tokens_a:.0f} tokens", flush=True)
    print(f"   - Phương pháp B (Trafilatura):      ~{avg_tokens_b:.0f} tokens", flush=True)

    print("\n" + "=" * 80, flush=True)


if __name__ == "__main__":
    run_benchmark(num_articles=3)
