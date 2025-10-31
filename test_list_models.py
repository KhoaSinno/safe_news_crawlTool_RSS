"""
Test script để list available Gemini models
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

print(f"✅ Loaded API key: {api_key[:10]}...")

# Configure API
genai.configure(api_key=api_key)

# List all available models
print("\n📋 Available Gemini models:")
print("=" * 80)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✅ Model: {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(
                f"   Supported methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
