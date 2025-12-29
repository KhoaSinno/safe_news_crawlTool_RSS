"""
TEST: Google Search Grounding Tool có giúp đọc được bài mới không?

Mục tiêu: Kiểm tra xem với tool google_search có đọc được bài mới tinh không
"""

import json
import feedparser
from datetime import datetime
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


load_dotenv()


def get_freshest_articles(max_articles=3):
    """Lấy các bài báo MỚI NHẤT từ RSS tin-moi-nhat"""
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


def test_with_grounding(api_key: str):
    """Test với Google Search Grounding"""

    genai.configure(api_key=api_key)

    print("=" * 80)
    print("🧪 TEST GOOGLE SEARCH GROUNDING TOOL")
    print("=" * 80)
    print(f"⏰ Thời điểm test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Import Tool class
    from google.generativeai.types import Tool

    # Thử các cấu hình tool khác nhau
    tool_configs = [
        {
            'name': 'google_search_retrieval (gemini-2.0-flash)',
            'tools': Tool(google_search_retrieval={}),
            'model': 'gemini-2.0-flash'
        },
        {
            'name': 'google_search_retrieval (gemini-2.5-flash)',
            'tools': Tool(google_search_retrieval={}),
            'model': 'gemini-2.5-flash'
        },
    ]

    articles = get_freshest_articles(2)
    print(f"\n📰 Test với {len(articles)} bài mới nhất:")
    for i, art in enumerate(articles, 1):
        print(f"  {i}. [{art['published']}]")
        print(f"     {art['title'][:60]}...")

    results = []

    for config in tool_configs:
        print(f"\n{'='*80}")
        print(f"🔧 Testing config: {config['name']}")
        print(f"📦 Model: {config['model']}")
        print("-" * 80)

        try:
            model = genai.GenerativeModel(
                config['model'],
                tools=config['tools']
            )

            article = articles[0]  # Test với bài đầu tiên

            prompt = f"""
            HÃY SỬ DỤNG GOOGLE SEARCH ĐỂ TÌM VÀ ĐỌC NỘI DUNG TỪ BÀI BÁO SAU:
            
            URL: {article['link']}
            Tiêu đề: "{article['title']}"
            
            Đây là bài báo MỚI TINH vừa xuất bản hôm nay {datetime.now().strftime('%d/%m/%Y')}.
            
            SAU KHI TÌM KIẾM VÀ ĐỌC NỘI DUNG, trả về JSON:
            {{
                "search_used": true nếu đã dùng Google Search, false nếu không,
                "content_found": true nếu tìm thấy nội dung bài báo,
                "first_paragraph": "Copy 1-2 câu đầu của bài báo",
                "specific_names": ["Tên người được nhắc trong bài"],
                "specific_numbers": ["Số liệu cụ thể từ bài"],
                "source_verification": "Nguồn thông tin: search/training_data/cannot_access"
            }}
            
            CHỈ TRẢ JSON, không giải thích.
            """

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

            print(f"\n📝 Response:")
            print(response.text[:1500])

            # Check grounding metadata nếu có
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    print(
                        f"\n🔍 Grounding Metadata: {candidate.grounding_metadata}")

            results.append({
                'config': config['name'],
                'model': config['model'],
                'status': 'success',
                'response': response.text[:500]
            })

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'config': config['name'],
                'model': config['model'],
                'status': 'error',
                'error': str(e)
            })

    # Tổng kết
    print("\n" + "=" * 80)
    print("📊 TỔNG KẾT")
    print("=" * 80)
    for r in results:
        status_icon = "✅" if r['status'] == 'success' else "❌"
        print(f"{status_icon} {r['config']} ({r['model']}): {r['status']}")
        if r['status'] == 'error':
            print(f"   Error: {r.get('error', 'Unknown')[:100]}")

    return results


if __name__ == "__main__":
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Thiếu GEMINI_API_KEY")
        sys.exit(1)

    test_with_grounding(api_key)
