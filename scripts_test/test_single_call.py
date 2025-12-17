"""
Test đơn giản: gọi 1 request duy nhất để check quota
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print("🧪 Testing single API call to check quota...")
print("=" * 60)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

try:
    print(f"⏰ Time: {time.strftime('%H:%M:%S')}")
    print("📞 Calling Gemini API...")

    response = model.generate_content(
        "Hello, just testing! Reply with 'OK' in JSON: {\"status\": \"ok\"}",
        generation_config={'temperature': 0.1, 'max_output_tokens': 50}
    )

    print(f"✅ SUCCESS!")
    print(f"📝 Response: {response.text}")
    print(f"⏰ Time: {time.strftime('%H:%M:%S')}")
    print("\n🎉 Your API quota is working!")

except Exception as e:
    print(f"❌ FAILED: {e}")

    if "429" in str(e):
        print("\n⚠️ Quota exhausted. Wait 1-2 minutes and try again.")
        print("   Free tier limit: 15 requests/minute")
    elif "404" in str(e):
        print("\n⚠️ Model not found. Try different model name.")

print("\n" + "=" * 60)
