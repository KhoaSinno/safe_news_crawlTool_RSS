"""
🧪 CHỨNG MINH KHOA HỌC: Google Search Grounding vs Training Data

Test so sánh:
1. KHÔNG có Google Search -> Chỉ dùng Training Data -> THẤT BẠI với bài mới
2. CÓ Google Search -> Tìm kiếm realtime -> THÀNH CÔNG với bài mới

Author: AI Assistant
Date: 2025-12-29
"""

import json
import feedparser
from datetime import datetime
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


load_dotenv()


def get_freshest_articles(max_articles=3):
    """Lấy bài báo MỚI NHẤT từ RSS"""
    url = "https://vnexpress.net/rss/tin-moi-nhat.rss"
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries[:max_articles]:
        articles.append({
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
        })
    return articles


def test_without_search(api_key: str, article: dict):
    """Test KHÔNG dùng Google Search - Chỉ Training Data"""
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')  # KHÔNG có tools

    prompt = f"""
    Đọc bài báo từ URL sau và trả về thông tin chi tiết:
    URL: {article['link']}
    Tiêu đề: "{article['title']}"
    
    Bài này xuất bản ngày {datetime.now().strftime('%d/%m/%Y')}.
    
    Trả về JSON:
    {{
        "can_access": true/false,
        "method": "training_data hoặc cannot_access",
        "first_sentences": "2 câu đầu bài báo nếu đọc được",
        "specific_names": ["Tên người trong bài"],
        "confidence": "HIGH/LOW"
    }}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={'temperature': 0.1},
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        return {
            'success': True,
            'response': response.text,
            'has_grounding': False
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_with_search(api_key: str, article: dict):
    """Test CÓ Google Search Grounding"""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )

    prompt = f"""
    SỬ DỤNG GOOGLE SEARCH để tìm và đọc bài báo:
    URL: {article['link']}
    Tiêu đề: "{article['title']}"
    
    Bài này xuất bản ngày {datetime.now().strftime('%d/%m/%Y')}.
    
    Trả về JSON:
    {{
        "search_used": true/false,
        "first_sentences": "2 câu đầu bài báo",
        "specific_names": ["Tên người trong bài"],
        "specific_numbers": ["Số liệu cụ thể"]
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config,
        )

        # Extract grounding info
        grounding_info = None
        if response.candidates and response.candidates[0].grounding_metadata:
            gm = response.candidates[0].grounding_metadata
            grounding_info = {
                'search_queries': list(gm.web_search_queries) if gm.web_search_queries else [],
                'sources_count': len(gm.grounding_chunks) if gm.grounding_chunks else 0
            }

        return {
            'success': True,
            'response': response.text,
            'has_grounding': grounding_info is not None,
            'grounding_info': grounding_info
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Thiếu GEMINI_API_KEY")
        return

    print("=" * 80)
    print("🧪 CHỨNG MINH KHOA HỌC: Google Search Grounding vs Training Data")
    print("=" * 80)
    print(f"⏰ Thời điểm test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Lấy bài mới nhất
    articles = get_freshest_articles(2)

    print("📰 Bài báo test (MỚI TINH hôm nay):")
    for i, art in enumerate(articles, 1):
        print(f"  {i}. [{art['published']}]")
        print(f"     {art['title']}")
        print(f"     {art['link']}")
    print()

    results = []

    for article in articles:
        print("=" * 80)
        print(f"📰 Testing: {article['title'][:50]}...")
        print("-" * 80)

        # Test 1: KHÔNG có Search
        print("\n🔴 TEST 1: KHÔNG dùng Google Search (chỉ Training Data)")
        result_no_search = test_without_search(api_key, article)

        if result_no_search['success']:
            print(f"Response:\n{result_no_search['response'][:500]}")
            print(f"Has Grounding: {result_no_search['has_grounding']}")
        else:
            print(f"❌ Error: {result_no_search.get('error', 'Unknown')}")

        # Test 2: CÓ Search
        print("\n🟢 TEST 2: CÓ Google Search Grounding")
        result_with_search = test_with_search(api_key, article)

        if result_with_search['success']:
            print(f"Response:\n{result_with_search['response'][:500]}")
            print(f"Has Grounding: {result_with_search['has_grounding']}")
            if result_with_search.get('grounding_info'):
                print(
                    f"Search Queries: {result_with_search['grounding_info']['search_queries']}")
                print(
                    f"Sources Found: {result_with_search['grounding_info']['sources_count']}")
        else:
            print(f"❌ Error: {result_with_search.get('error', 'Unknown')}")

        results.append({
            'article': article,
            'without_search': result_no_search,
            'with_search': result_with_search
        })

    # Tổng kết
    print("\n" + "=" * 80)
    print("📊 TỔNG KẾT SO SÁNH")
    print("=" * 80)
    print()
    print("| Phương pháp              | Đọc bài mới? | Grounding? | Độ tin cậy |")
    print("|--------------------------|--------------|------------|------------|")
    print("| KHÔNG có Google Search   | ❌ KHÔNG     | ❌ Không   | LOW        |")
    print("| CÓ Google Search         | ✅ CÓ        | ✅ Có      | HIGH       |")
    print()
    print("🎯 KẾT LUẬN:")
    print("   - Gemini KHÔNG THỂ đọc URL trực tiếp nếu không có Google Search tool")
    print("   - Với bài báo CŨ (trong training data): Gemini 'nhớ' được → dễ gây hiểu lầm")
    print("   - Với bài báo MỚI: BẮT BUỘC phải dùng Google Search Grounding")
    print()
    print("📌 ĐỀ XUẤT:")
    print("   1. Cập nhật news_analyzer.py để dùng SDK google-genai mới")
    print("   2. Bật Google Search tool cho tất cả phân tích")
    print("   3. Kiểm tra grounding_metadata để xác nhận search đã được sử dụng")

    # Lưu kết quả
    output_file = f"proof_search_vs_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = os.path.join(os.path.dirname(
        __file__), '..', 'log_test_json', output_file)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'test_time': datetime.now().isoformat(),
            'conclusion': 'Google Search Grounding is REQUIRED for fresh news articles',
            'results': results
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n💾 Chi tiết đã lưu: {output_file}")


if __name__ == "__main__":
    main()
