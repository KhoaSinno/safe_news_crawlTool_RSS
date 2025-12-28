"""Test the new logging feature"""
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.rss_crawler import fetch_rss
from utils.news_analyzer import NewsAnalyzer
from utils.firebase_handler import store_to_firebase
import json

# Load environment
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize analyzer
analyzer = NewsAnalyzer(GEMINI_API_KEY)

# Test với một feed
print("Testing logging feature with 3 articles from RSS...")
print("=" * 50)

entries = fetch_rss("https://vnexpress.net/rss/tin-moi-nhat.rss")
print(f"Found {len(entries)} entries from RSS")

# Setup detailed logs
detailed_logs = {
    "total": 0,
    "analyzed": 0,
    "positive": 0,
    "negative": 0,
    "neutral": 0,
    "toxic": 0,
    "stored": 0,
    "errors": 0,
    "categories": {},
    "results": [],
    "timestamp": datetime.now().isoformat(),
    "collection": "test_logging_feature"
}

# Process first 3 articles
for i, entry in enumerate(entries[:3]):
    detailed_logs["total"] += 1

    title = entry.get('title', 'No title')
    link = entry.get('link', '')
    category = 'tin-moi-nhat'

    print(f"\n[{i+1}/3] Analyzing: {title[:60]}...")

    rss_data = {
        "title": title,
        "link": link,
        "category": category,
        "summary": entry.get('summary', ''),
        "image_url": entry.get('image_url', ''),
        "published": entry.get('published', '')
    }

    try:
        result = analyzer.analyze_and_transform(rss_data)
        detailed_logs["analyzed"] += 1

        log_entry = {
            "index": detailed_logs["total"],
            "title": title,
            "link": link,
            "source_category": category
        }

        if result:
            sentiment = result.get('sentiment', 0)
            is_toxic = result.get('is_toxic', False)
            result_category = result.get('category', category)

            # Update counters
            if sentiment == 1:
                detailed_logs["positive"] += 1
            elif sentiment == -1:
                detailed_logs["negative"] += 1
            else:
                detailed_logs["neutral"] += 1

            if is_toxic:
                detailed_logs["toxic"] += 1

            # Update category counter
            detailed_logs["categories"][result_category] = \
                detailed_logs["categories"].get(result_category, 0) + 1

            # Add to log entry
            log_entry.update({
                "category": result_category,
                "sentiment": sentiment,
                "is_toxic": is_toxic,
                "description": result.get('description', '')[:200]
            })

            print(
                f"  ✓ Sentiment: {sentiment}, Toxic: {is_toxic}, Category: {result_category}")
        else:
            log_entry["status"] = "FILTERED_OUT"
            print(f"  ✗ Filtered out")

        detailed_logs["results"].append(log_entry)

    except Exception as e:
        detailed_logs["errors"] += 1
        detailed_logs["results"].append({
            "index": detailed_logs["total"],
            "title": title,
            "link": link,
            "source_category": category,
            "status": "ERROR",
            "error": str(e)
        })
        print(f"  ✗ Error: {e}")

# Save logs
print("\n" + "=" * 50)
print("Saving detailed logs...")

os.makedirs("logs_prod", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"logs_prod/crawl_result_{timestamp}.json"

with open(log_filename, 'w', encoding='utf-8') as f:
    json.dump(detailed_logs, f, ensure_ascii=False, indent=2)

print(f"✓ Logs saved to: {log_filename}")
print(f"\nSummary:")
print(f"  Total: {detailed_logs['total']}")
print(f"  Analyzed: {detailed_logs['analyzed']}")
print(f"  Positive: {detailed_logs['positive']}")
print(f"  Neutral: {detailed_logs['neutral']}")
print(f"  Negative: {detailed_logs['negative']}")
print(f"  Toxic: {detailed_logs['toxic']}")
print(f"  Errors: {detailed_logs['errors']}")
print(f"  Categories: {detailed_logs['categories']}")
