"""Quick test - only 5 articles"""
import os
import sys
from dotenv import load_dotenv
from utils.news_analyzer import NewsAnalyzer
from utils.rss_crawler import fetch_rss

# Load environment
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print("🧪 Quick Test - 5 Articles with gemini-2.0-flash")
print("=" * 60)

# Get 5 articles
articles = fetch_rss('https://vnexpress.net/rss/tin-moi-nhat.rss')[:5]
print(f"📡 Got {len(articles)} articles\n")

# Test analysis
analyzer = NewsAnalyzer(api_key)
success_count = 0
blocked_count = 0

for i, article in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"📝 [{i}/5] {article['title'][:60]}...")

    result = analyzer.analyze_and_transform(article)

    if result:
        sentiment_text = ["❌ NEGATIVE", "⚠️ NEUTRAL",
                          "✅ POSITIVE"][result['sentiment'] + 1]
        toxic_text = "🚫 TOXIC" if result['is_toxic'] else "✅ SAFE"

        if result['description'] == 'Content blocked by safety filters':
            blocked_count += 1
            print(f"   🚧 BLOCKED by safety filter")
        else:
            success_count += 1
            print(f"   {sentiment_text} | {toxic_text}")
            print(f"   📝 {result['description'][:100]}...")
    else:
        print(f"   ❌ FAILED")

print(f"\n{'='*60}")
print(f"📊 RESULTS:")
print(f"   ✅ Success: {success_count}/5")
print(f"   🚧 Blocked: {blocked_count}/5")
print(f"   ❌ Failed: {5 - success_count - blocked_count}/5")
