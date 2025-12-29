"""
Test CHỨNG MINH Gemini có thực sự đọc URL không
================================================================================
Test này sẽ hỏi những chi tiết CỤ THỂ chỉ có trong bài báo, không có trong tiêu đề
"""

from utils.rss_crawler import fetch_rss
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def prove_url_reading(api_key: str, title: str, url: str):
    """
    Chứng minh Gemini đọc URL bằng cách hỏi những chi tiết không có trong tiêu đề
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Prompt yêu cầu chi tiết CỤ THỂ chỉ có trong bài báo
    prompt = f"""
    Tôi muốn CHỨNG MINH bạn có thực sự đọc được nội dung từ URL hay không.
    
    URL bài báo: {url}
    Tiêu đề: "{title}"
    
    HÃY TRẢ LỜI CÁC CÂU HỎI SAU (chỉ có thể trả lời nếu đọc được nội dung bài báo):
    
    1. Tên cụ thể của người/tổ chức được đề cập trong bài (KHÔNG có trong tiêu đề)?
    2. Ngày/thời gian cụ thể được đề cập trong bài?
    3. Địa điểm cụ thể (tên đường, quận, tỉnh) được đề cập?
    4. Số liệu cụ thể (số tiền, số người, tỷ lệ %) trong bài?
    5. Trích dẫn 1 câu nguyên văn từ bài báo (trong dấu ngoặc kép)?
    
    FORMAT JSON:
    {{
        "can_read_url": true/false,
        "specific_names": ["tên 1", "tên 2"],
        "specific_dates": ["ngày/giờ 1"],
        "specific_locations": ["địa điểm 1"],
        "specific_numbers": ["số liệu 1"],
        "direct_quote": "câu trích dẫn từ bài báo",
        "confidence_level": "HIGH/MEDIUM/LOW",
        "explanation": "giải thích ngắn gọn"
    }}
    
    NẾU KHÔNG ĐỌC ĐƯỢC URL, hãy thành thật nói can_read_url = false
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.1,
                'max_output_tokens': 2048
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        return {
            'title': title,
            'url': url,
            'response': response.text,
            'success': True
        }

    except Exception as e:
        return {
            'title': title,
            'url': url,
            'error': str(e),
            'success': False
        }


def main():
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return

    print("=" * 80)
    print("🔬 PROOF TEST: GEMINI URL READING VERIFICATION")
    print("=" * 80)
    print("Test này hỏi những chi tiết CỤ THỂ chỉ có trong bài báo,")
    print("không thể đoán được chỉ từ tiêu đề.")
    print("=" * 80)

    # Lấy bài báo
    articles = fetch_rss("https://vnexpress.net/rss/tin-moi-nhat.rss")

    if not articles:
        print("❌ Không lấy được bài báo")
        return

    # Test 3 bài
    test_count = 3
    results = []

    for i, article in enumerate(articles[:test_count], 1):
        print(f"\n{'='*80}")
        print(f"📝 TEST {i}/{test_count}")
        print(f"📰 Title: {article['title']}")
        print(f"🔗 URL: {article['link']}")
        print("-" * 80)

        result = prove_url_reading(api_key, article['title'], article['link'])
        results.append(result)

        if result['success']:
            print("\n📋 GEMINI RESPONSE:")
            print(result['response'])
        else:
            print(f"❌ Error: {result.get('error')}")

    # Save results
    output_file = f'url_reading_proof_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*80}")
    print(f"💾 Results saved to: {output_file}")
    print("=" * 80)

    # Đánh giá
    print("\n🎯 KẾT LUẬN:")
    print("-" * 40)
    print("Nếu Gemini trả về các chi tiết cụ thể như:")
    print("  - Tên người/tổ chức không có trong tiêu đề")
    print("  - Ngày giờ cụ thể")
    print("  - Địa điểm chi tiết")
    print("  - Số liệu cụ thể")
    print("  - Trích dẫn nguyên văn")
    print("=> Gemini CÓ THỂ đọc được nội dung từ URL!")


if __name__ == "__main__":
    main()
