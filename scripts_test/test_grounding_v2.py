"""
Test Script để xác minh Google Search Grounding có thực sự đọc URL không
================================================================================
Version 2: Sử dụng google_search tool thay vì google_search_retrieval
"""

from utils.rss_crawler import fetch_rss
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)


def test_different_tool_configs(api_key: str, title: str, url: str):
    """
    Test nhiều cấu hình tool khác nhau để tìm ra cái nào hoạt động
    """
    genai.configure(api_key=api_key)

    results = {}

    # ========== CONFIG 1: google_search (theo lỗi gợi ý) ==========
    print("\n🔧 Testing Config 1: google_search tool...")
    try:
        from google.generativeai import protos

        # Cách 1: Dùng Tool object
        google_search_tool = genai.protos.Tool(
            google_search=genai.protos.GoogleSearch()
        )

        model1 = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=[google_search_tool]
        )

        response1 = model1.generate_content(
            f"""
            Hãy search và đọc nội dung bài báo từ URL sau:
            URL: {url}
            Title: {title}
            
            Sau khi đọc, trả về JSON:
            {{
                "summary": "tóm tắt nội dung chính (KHÔNG phải chỉ tiêu đề)",
                "specific_details": ["chi tiết 1 từ bài báo", "chi tiết 2", "chi tiết 3"],
                "sentiment": 1/0/-1
            }}
            """,
            generation_config={'temperature': 0.1}
        )

        results['config1_google_search'] = {
            'success': True,
            'response': response1.text if response1.text else None,
            'has_grounding': hasattr(response1.candidates[0], 'grounding_metadata') if response1.candidates else False
        }

        # Check grounding metadata
        if response1.candidates and hasattr(response1.candidates[0], 'grounding_metadata'):
            gm = response1.candidates[0].grounding_metadata
            if gm:
                results['config1_google_search']['grounding_info'] = str(gm)[
                    :500]

        print(f"✅ Config 1 SUCCESS")
        print(
            f"   Response: {response1.text[:300] if response1.text else 'None'}...")

    except Exception as e:
        results['config1_google_search'] = {'success': False, 'error': str(e)}
        print(f"❌ Config 1 FAILED: {e}")

    # ========== CONFIG 2: Không dùng tool, chỉ yêu cầu model đọc URL ==========
    print("\n🔧 Testing Config 2: No tool (baseline)...")
    try:
        model2 = genai.GenerativeModel('gemini-2.5-flash')

        response2 = model2.generate_content(
            f"""
            Đọc bài báo từ URL sau và phân tích:
            URL: {url}
            Title: {title}
            
            Trả về JSON:
            {{
                "summary": "tóm tắt nội dung",
                "specific_details": ["chi tiết 1", "chi tiết 2", "chi tiết 3"],
                "sentiment": 1/0/-1,
                "did_you_actually_read_url": true/false
            }}
            """,
            generation_config={'temperature': 0.1}
        )

        results['config2_no_tool'] = {
            'success': True,
            'response': response2.text if response2.text else None,
        }
        print(f"✅ Config 2 SUCCESS")
        print(
            f"   Response: {response2.text[:300] if response2.text else 'None'}...")

    except Exception as e:
        results['config2_no_tool'] = {'success': False, 'error': str(e)}
        print(f"❌ Config 2 FAILED: {e}")

    # ========== CONFIG 3: gemini-2.0-flash-exp với google_search ==========
    print("\n🔧 Testing Config 3: gemini-2.0-flash-exp + google_search...")
    try:
        google_search_tool = genai.protos.Tool(
            google_search=genai.protos.GoogleSearch()
        )

        model3 = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            tools=[google_search_tool]
        )

        response3 = model3.generate_content(
            f"""
            Hãy dùng Google Search để tìm và đọc nội dung từ URL này:
            URL: {url}
            Title: {title}
            
            Trả về JSON với các chi tiết CỤ THỂ từ bài báo:
            {{
                "summary": "tóm tắt nội dung",
                "specific_details": ["chi tiết 1", "chi tiết 2", "chi tiết 3"],
                "sentiment": 1/0/-1
            }}
            """,
            generation_config={'temperature': 0.1}
        )

        results['config3_2.0_flash_exp'] = {
            'success': True,
            'response': response3.text if response3.text else None,
            'has_grounding': False
        }

        if response3.candidates and hasattr(response3.candidates[0], 'grounding_metadata'):
            gm = response3.candidates[0].grounding_metadata
            if gm:
                results['config3_2.0_flash_exp']['has_grounding'] = True
                results['config3_2.0_flash_exp']['grounding_info'] = str(gm)[
                    :500]

        print(f"✅ Config 3 SUCCESS")
        print(
            f"   Response: {response3.text[:300] if response3.text else 'None'}...")
        print(
            f"   Has Grounding: {results['config3_2.0_flash_exp']['has_grounding']}")

    except Exception as e:
        results['config3_2.0_flash_exp'] = {'success': False, 'error': str(e)}
        print(f"❌ Config 3 FAILED: {e}")

    return results


def main():
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return

    print("=" * 80)
    print("🔍 GOOGLE SEARCH TOOL CONFIGURATION TEST")
    print("=" * 80)

    # Lấy 1 bài báo để test
    print("\n📰 Đang lấy bài báo từ VNExpress RSS...")
    rss_url = "https://vnexpress.net/rss/tin-moi-nhat.rss"
    articles = fetch_rss(rss_url)

    if not articles:
        print("❌ Không lấy được bài báo nào")
        return

    # Chọn bài báo đầu tiên
    article = articles[0]
    print(f"\n📝 Test Article: {article['title']}")
    print(f"🔗 URL: {article['link']}")

    # Test các config
    results = test_different_tool_configs(
        api_key, article['title'], article['link'])

    # Save results
    output_file = f'grounding_config_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n{'='*80}")
    print(f"💾 Results saved to: {output_file}")
    print("=" * 80)

    # Summary
    print("\n📊 CONFIGURATION SUMMARY:")
    print("-" * 40)
    for config, result in results.items():
        status = "✅" if result.get('success') else "❌"
        grounding = "🔍 GROUNDING" if result.get('has_grounding') else ""
        print(f"{status} {config}: {grounding}")


if __name__ == "__main__":
    main()
