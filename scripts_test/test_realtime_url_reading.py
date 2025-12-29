"""
TEST KHOA HỌC: Gemini có thực sự đọc URL hay chỉ dựa vào Training Data?

PHƯƠNG PHÁP KIỂM CHỨNG:
1. Lấy bài báo MỚI TINH từ RSS "tin-moi-nhat" (xuất bản trong vài giờ qua)
2. Yêu cầu Gemini trả về CHI TIẾT CỤ THỂ chỉ có trong bài (không có trong tiêu đề)
3. So sánh với knowledge cutoff của model

NẾU Gemini trả về đúng chi tiết từ bài MỚI TINH -> Chứng minh nó đọc URL
NẾU Gemini đoán mò/sai -> Chứng minh nó chỉ dựa vào training data
"""

import json
import feedparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


load_dotenv()


def get_freshest_articles(max_articles=5):
    """Lấy các bài báo MỚI NHẤT từ RSS tin-moi-nhat"""
    url = "https://vnexpress.net/rss/tin-moi-nhat.rss"
    feed = feedparser.parse(url)

    articles = []
    now = datetime.now()

    for entry in feed.entries[:max_articles]:
        # Parse thời gian xuất bản
        published_str = entry.get('published', '')

        articles.append({
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': published_str,
            'summary': entry.get('summary', '')[:100] + '...' if entry.get('summary') else ''
        })

    return articles


def test_realtime_reading(api_key: str):
    """Test với bài báo mới nhất"""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    print("=" * 80)
    print("🧪 TEST KHOA HỌC: GEMINI CÓ THỰC SỰ ĐỌC URL KHÔNG?")
    print("=" * 80)
    print(f"⏰ Thời điểm test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Knowledge cutoff của Gemini 2.5: ~Tháng 1/2025")
    print("=" * 80)

    # Lấy bài mới nhất
    articles = get_freshest_articles(5)

    print(f"\n📰 Tìm thấy {len(articles)} bài báo mới nhất:")
    for i, art in enumerate(articles, 1):
        print(f"  {i}. [{art['published']}] {art['title'][:60]}...")

    results = []

    for i, article in enumerate(articles, 1):
        print(f"\n{'='*80}")
        print(f"🔬 TEST {i}/{len(articles)}")
        print(f"📰 Tiêu đề: {article['title']}")
        print(f"🔗 URL: {article['link']}")
        print(f"📅 Xuất bản: {article['published']}")
        print("-" * 80)

        # Prompt yêu cầu chi tiết CỤ THỂ chỉ có trong bài
        prompt = f"""
        BÀI KIỂM TRA: Bạn có thể đọc nội dung từ URL không?
        
        URL: {article['link']}
        Tiêu đề: "{article['title']}"
        
        QUAN TRỌNG: Đây là bài báo MỚI TINH, vừa xuất bản ngày hôm nay {datetime.now().strftime('%d/%m/%Y')}.
        
        NẾU BẠN CÓ THỂ ĐỌC ĐƯỢC NỘI DUNG TỪ URL, hãy trả về JSON sau với thông tin CỤ THỂ:
        
        {{
            "can_read_url": true hoặc false,
            "reading_method": "direct_url_access" hoặc "training_data" hoặc "cannot_access",
            "specific_details": {{
                "first_paragraph": "Copy nguyên văn 1-2 câu đầu tiên của bài báo",
                "person_names": ["Tên người cụ thể được nhắc đến trong bài"],
                "locations": ["Địa điểm cụ thể"],
                "numbers_statistics": ["Số liệu cụ thể: tiền, %, số người..."],
                "quotes": ["Trích dẫn nguyên văn từ bài báo nếu có"]
            }},
            "confidence": "HIGH nếu đọc được URL, LOW nếu đoán từ tiêu đề",
            "explanation": "Giải thích nguồn thông tin của bạn"
        }}
        
        LƯU Ý: 
        - Nếu bạn KHÔNG THỂ truy cập URL, hãy thành thật nói "cannot_access"
        - Nếu bạn chỉ ĐOÁN từ tiêu đề, hãy nói "training_data" 
        - CHỈ nói "direct_url_access" nếu bạn THỰC SỰ đọc được nội dung từ link
        
        Trả về JSON ONLY, không giải thích thêm.
        """

        try:
            from google.generativeai.types import HarmCategory, HarmBlockThreshold

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

            raw_response = response.text
            print(f"\n📝 RAW RESPONSE:")
            print(raw_response[:2000])

            # Parse JSON
            text = raw_response.strip()
            if '```json' in text:
                import re
                json_match = re.search(
                    r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    text = json_match.group(1)
            elif '```' in text:
                text = text.replace('```', '').strip()

            result = json.loads(text)

            print(f"\n🔍 PHÂN TÍCH KẾT QUẢ:")
            print(f"  - Có thể đọc URL: {result.get('can_read_url', 'N/A')}")
            print(f"  - Phương thức: {result.get('reading_method', 'N/A')}")
            print(f"  - Độ tin cậy: {result.get('confidence', 'N/A')}")
            print(f"  - Giải thích: {result.get('explanation', 'N/A')}")

            details = result.get('specific_details', {})
            print(f"\n  📌 Chi tiết cụ thể:")
            print(
                f"    - Đoạn đầu: {details.get('first_paragraph', 'N/A')[:150]}...")
            print(f"    - Tên người: {details.get('person_names', [])}")
            print(f"    - Địa điểm: {details.get('locations', [])}")
            print(f"    - Số liệu: {details.get('numbers_statistics', [])}")

            results.append({
                'article': article,
                'gemini_response': result,
                'test_time': datetime.now().isoformat()
            })

        except Exception as e:
            print(f"❌ Lỗi: {e}")
            results.append({
                'article': article,
                'error': str(e),
                'test_time': datetime.now().isoformat()
            })

    # Tổng kết
    print("\n" + "=" * 80)
    print("📊 TỔNG KẾT KIỂM CHỨNG")
    print("=" * 80)

    direct_access_count = 0
    training_data_count = 0
    cannot_access_count = 0

    for r in results:
        if 'gemini_response' in r:
            method = r['gemini_response'].get('reading_method', '')
            if method == 'direct_url_access':
                direct_access_count += 1
            elif method == 'training_data':
                training_data_count += 1
            else:
                cannot_access_count += 1

    print(f"  ✅ Direct URL Access: {direct_access_count}/{len(results)}")
    print(f"  📚 Training Data: {training_data_count}/{len(results)}")
    print(f"  ❌ Cannot Access: {cannot_access_count}/{len(results)}")

    if direct_access_count > 0:
        print("\n🎯 KẾT LUẬN: Gemini CÓ KHẢ NĂNG đọc URL trực tiếp!")
    elif training_data_count == len(results):
        print("\n⚠️ KẾT LUẬN: Gemini CHỈ dựa vào Training Data!")
    else:
        print("\n❓ KẾT LUẬN: Cần thêm dữ liệu để xác định")

    # Lưu kết quả
    output_file = f"realtime_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path = os.path.join(os.path.dirname(
        __file__), '..', 'log_test_json', output_file)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'test_time': datetime.now().isoformat(),
            'model': 'gemini-2.5-flash',
            'purpose': 'Verify if Gemini can read URLs in real-time or only uses training data',
            'results': results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Kết quả đã lưu: {output_file}")

    return results


if __name__ == "__main__":
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Thiếu GEMINI_API_KEY trong .env")
        sys.exit(1)

    test_realtime_reading(api_key)
