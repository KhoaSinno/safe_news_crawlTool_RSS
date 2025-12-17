"""Debug Gemini API response"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv(override=True)
api_key = os.getenv('GEMINI_API_KEY')

print(f"Using API Key: {api_key}")
print("-" * 50)

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# Test simple request
try:
    response = model.generate_content("Hello, are you working?")
    print("Response successful!")
    print(f"Text: {response.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}")
    print(f"Message: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response}")
