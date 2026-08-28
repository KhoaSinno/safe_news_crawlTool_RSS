import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from config import settings
from utils.news_analyzer import NewsAnalyzer

logging.basicConfig(level=logging.DEBUG)

settings.validate()
print(f"API Key: {settings.GEMINI_API_KEY[:20]}...")

analyzer = NewsAnalyzer(settings.GEMINI_API_KEY)

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
