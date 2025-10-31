"""
Script để kiểm tra API quota và model info
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ Không tìm thấy GEMINI_API_KEY trong .env file")
    exit(1)

print(f"✅ Loaded API key: {api_key[:20]}...")
print("\n" + "="*80)

# Configure API
genai.configure(api_key=api_key)

# List available models with details
print("\n📋 AVAILABLE MODELS WITH RATE LIMITS:")
print("="*80)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✅ Model: {model.name}")
            print(f"   Display Name: {model.display_name}")

            # Rate limits info (if available)
            if hasattr(model, 'input_token_limit'):
                print(f"   📊 Input Token Limit: {model.input_token_limit:,}")
            if hasattr(model, 'output_token_limit'):
                print(f"   📊 Output Token Limit: {model.output_token_limit:,}")

            # Supported methods
            print(
                f"   🔧 Methods: {', '.join(model.supported_generation_methods)}")

            # Only show first 3 models for readability
            if model.name in ['models/gemini-2.0-flash', 'models/gemini-2.5-flash', 'models/gemini-flash-latest']:
                print(f"   ⭐ RECOMMENDED for your use case")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("\n📝 NOTE:")
print("   Free tier limits (approx):")
print("   - Requests per minute (RPM): 15")
print("   - Tokens per minute (TPM): 1,000,000")
print("   - Requests per day (RPD): 1,500")
print("\n   For detailed quota info, visit:")
print("   🔗 https://aistudio.google.com/app/apikey")
print("   🔗 https://ai.google.dev/pricing")
