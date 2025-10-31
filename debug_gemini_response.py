"""
Debug script - xem Gemini response thực tế
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print("🔍 Debug: Xem raw response từ Gemini")
print("=" * 80)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# Test với 1 article title + URL
title = "Phụ huynh trông chờ con được học Tiếng Anh từ lớp 1"
url = "https://vnexpress.net/phu-huynh-trong-cho-con-duoc-hoc-tieng-anh-tu-lop-1-4957956.html"

prompt = f"""
BẠN LÀ MỘT CHUYÊN GIA PHÂN TÍCH TIN TỨC TIẾNG VIỆT

NHIỆM VỤ:
1. Truy cập và đọc TOÀN BỘ bài báo từ URL
2. Phân tích cảm xúc và tính độc hại

BÀI BÁO:
URL: {url}
Tiêu đề: "{title}"

TRẢ VỀ JSON (KHÔNG THÊM MARKDOWN):
{{
  "category": "string - danh mục phù hợp",
  "description": "string - mô tả ngắn 1-2 câu",
  "sentiment": 1 hoặc 0 hoặc -1,
  "is_toxic": true hoặc false
}}
"""

try:
    response = model.generate_content(
        prompt,
        generation_config={
            'temperature': 0.1,
            'max_output_tokens': 200,
            'top_p': 0.8,
            'top_k': 10
        },
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    print("✅ API call successful")
    print("\n📝 RAW RESPONSE TEXT:")
    print("-" * 80)
    print(response.text)
    print("-" * 80)

    print("\n🔍 Response metadata:")
    print(f"   Candidates: {len(response.candidates)}")
    if response.candidates:
        print(f"   Finish reason: {response.candidates[0].finish_reason}")
        print(f"   Has content: {bool(response.candidates[0].content.parts)}")

except Exception as e:
    print(f"❌ Error: {e}")
