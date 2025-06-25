"""
Test Script - Exact 20 Articles Analysis
Kiểm tra chính xác 20 bài báo và đánh giá kết quả chi tiết
"""

import os
import json
import logging
import time
from dotenv import load_dotenv
from utils.news_analyzer import NewsAnalyzer
from utils.firebase_handler import store_to_firebase
from utils.rss_crawler import fetch_rss

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_20_articles.log'),
        logging.StreamHandler()
    ]
)


def test_exactly_20_articles():
    """Test với chính xác 20 bài báo và đánh giá chi tiết"""

    # Kiểm tra API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False

    print("🎯 Testing Exactly 20 Articles")
    print("=" * 60)

    # Khởi tạo analyzer
    analyzer = NewsAnalyzer(api_key)

    # Collect articles từ RSS feeds
    print("📡 Collecting articles from RSS feeds...")

    rss_feeds = [
        {"url": "https://vnexpress.net/rss/giao-duc.rss", "category": "giao-duc"},
        {"url": "https://vnexpress.net/rss/suc-khoe.rss", "category": "suc-khoe"},
        {"url": "https://vnexpress.net/rss/gia-dinh.rss", "category": "gia-dinh"},
        {"url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss",
            "category": "khoa-hoc-cong-nghe"},
    ]

    all_articles = []

    # Lấy articles từ multiple RSS feeds
    for feed in rss_feeds:
        print(f"📊 Fetching from {feed['category']}...")
        try:
            entries = fetch_rss(feed['url'])
            if entries:
                # Lấy 5 bài từ mỗi feed
                selected = entries[:5]
                for entry in selected:
                    article = {
                        "title": entry.get('title', ''),
                        "link": entry.get('link', ''),
                        "summary": entry.get('description', ''),
                        "image_url": entry.get('image_url', ''),
                        "published": entry.get('published', ''),
                        "source_category": feed['category']
                    }
                    all_articles.append(article)
                print(f"   ✅ Added {len(selected)} articles")
            else:
                print(f"   ⚠️ No articles found")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Đảm bảo chính xác 20 articles
    if len(all_articles) > 20:
        all_articles = all_articles[:20]
    elif len(all_articles) < 20:
        print(
            f"⚠️ Only found {len(all_articles)} articles, continuing with available...")

    print(f"\n🎯 Testing with exactly {len(all_articles)} articles")
    print("=" * 60)

    # Statistics tracking
    stats = {
        'total': len(all_articles),
        'analyzed': 0,
        'positive': 0,
        'negative': 0,
        'neutral': 0,
        'stored': 0,
        'errors': 0,
        'categories': {},
        'results': []
    }

    # Process each article
    for i, article in enumerate(all_articles, 1):
        title = article['title']
        print(f"\n📝 [{i:2d}/20] {title[:70]}...")
        print(f"🔗 {article['link']}")
        print(f"📂 Source: {article['source_category']}")

        try:
            # Rate limiting - đợi 3 giây giữa các requests
            if i > 1:
                print("⏳ Waiting 3 seconds (rate limiting)...")
                time.sleep(3)

            # Phân tích bài báo
            result = analyzer.analyze_and_transform(article)
            stats['analyzed'] += 1

            if result:
                # Track sentiment
                sentiment = result.get('sentiment', 0)
                if sentiment == 1:
                    stats['positive'] += 1
                elif sentiment == -1:
                    stats['negative'] += 1
                else:
                    stats['neutral'] += 1

                # Track category
                category = result.get('category', 'unknown')
                stats['categories'][category] = stats['categories'].get(
                    category, 0) + 1

                # Store result details
                article_result = {
                    'index': i,
                    'title': title[:80],
                    'category': category,
                    'sentiment': sentiment,
                    'is_toxic': result.get('is_toxic', False),
                    'description': result.get('description', '')[:150],
                    'source_category': article['source_category']
                }
                stats['results'].append(article_result)

                print(f"✅ Analysis successful!")
                print(f"   📂 Category: {category}")
                print(
                    f"   😊 Sentiment: {sentiment} ({'POSITIVE' if sentiment==1 else 'NEGATIVE' if sentiment==-1 else 'NEUTRAL'})")
                print(f"   🚫 Toxic: {result.get('is_toxic', False)}")
                print(
                    f"   📝 Description: {result.get('description', '')[:100]}...")

                # Lưu vào Firebase nếu positive và không toxic
                if sentiment == 1 and not result.get('is_toxic', True):
                    try:
                        if store_to_firebase(result, collection_name='test_20_articles'):
                            stats['stored'] += 1
                            print(f"   💾 ✅ Stored to Firebase")
                        else:
                            print(f"   💾 ❌ Failed to store")
                    except Exception as e:
                        print(f"   💾 ❌ Store error: {e}")
                else:
                    print(f"   💾 ⚠️ Not stored (negative or toxic)")
            else:
                print(f"❌ Analysis failed or filtered out")
                stats['results'].append({
                    'index': i,
                    'title': title[:80],
                    'status': 'FAILED',
                    'source_category': article['source_category']
                })

        except Exception as e:
            stats['errors'] += 1
            print(f"❌ Error processing article: {e}")
            stats['results'].append({
                'index': i,
                'title': title[:80],
                'status': 'ERROR',
                'error': str(e),
                'source_category': article['source_category']
            })

    # Print detailed results
    print("\n" + "=" * 60)
    print("📊 DETAILED TEST RESULTS")
    print("=" * 60)

    print(f"📈 OVERALL STATISTICS:")
    print(f"   Total Articles: {stats['total']}")
    print(f"   Successfully Analyzed: {stats['analyzed']}")
    print(f"   Errors: {stats['errors']}")
    print(f"   Success Rate: {(stats['analyzed']/stats['total']*100):.1f}%")

    print(f"\n😊 SENTIMENT BREAKDOWN:")
    print(
        f"   Positive: {stats['positive']} ({stats['positive']/max(stats['analyzed'],1)*100:.1f}%)")
    print(
        f"   Negative: {stats['negative']} ({stats['negative']/max(stats['analyzed'],1)*100:.1f}%)")
    print(
        f"   Neutral: {stats['neutral']} ({stats['neutral']/max(stats['analyzed'],1)*100:.1f}%)")

    print(f"\n📂 CATEGORY DISTRIBUTION:")
    for category, count in stats['categories'].items():
        print(f"   {category}: {count} articles")

    print(f"\n💾 STORAGE:")
    print(f"   Stored to Firebase: {stats['stored']}")
    print(
        f"   Storage Rate: {(stats['stored']/max(stats['positive'],1)*100):.1f}% of positive articles")

    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 60)
    for result in stats['results']:
        index = result['index']
        title = result['title']

        if 'status' in result:
            print(f"[{index:2d}] ❌ {title}")
            print(f"     Status: {result['status']}")
            if 'error' in result:
                print(f"     Error: {result['error']}")
        else:
            sentiment_emoji = "✅" if result['sentiment'] == 1 else "❌" if result['sentiment'] == -1 else "⚪"
            print(f"[{index:2d}] {sentiment_emoji} {title}")
            print(
                f"     Category: {result['category']} | Sentiment: {result['sentiment']} | Toxic: {result['is_toxic']}")
            print(f"     Description: {result['description']}...")
        print(f"     Source: {result['source_category']}")
        print()

    # Save results to JSON
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"

    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Failed to save results: {e}")

    print("\n" + "=" * 60)
    print("🎯 TEST COMPLETED!")
    print(f"🔍 Check Firebase collection 'test_20_articles' for stored results")
    print(f"📄 Detailed results saved to: {results_file}")
    print("=" * 60)

    return stats['analyzed'] > 0


if __name__ == "__main__":
    print("🧪 20 Articles Test Script")
    print("This will test exactly 20 articles and provide detailed analysis")
    print("Make sure you have sufficient Gemini API quota (20 requests needed)")

    input("\nPress Enter to start the test...")

    success = test_exactly_20_articles()

    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n⚠️ Test encountered issues. Check logs for details.")
