"""Test Gemini with actual article"""
import os
import logging
from dotenv import load_dotenv
from utils.news_analyzer import NewsAnalyzer

logging.basicConfig(level=logging.DEBUG)

load_dotenv(override=True)
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key: {api_key[:20]}...")

analyzer = NewsAnalyzer(api_key)

# Test với article thật
rss_data = {
    'title': 'Lợi ích khi ăn hạt điều thường xuyên',
    'link': 'https://vnexpress.net/loi-ich-khi-an-hat-dieu-thuong-xuyen-4840533.html',
    'category': 'suc-khoe',
    'summary': '',
    'image_url': '',
    'published': ''
}

print("\n" + "="*50)
print("Testing analysis...")
print("="*50)

result = analyzer.analyze_and_transform(rss_data)
print(f"\nFinal result: {result}")
