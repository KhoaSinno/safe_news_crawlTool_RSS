"""
Test Script - 30 Articles with Optimized Prompt
Kiểm tra 30 bài báo với prompt đã tối ưu tokens và ghi log chi tiết
"""

import os
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from utils.news_analyzer import NewsAnalyzer
from utils.firebase_handler import store_to_firebase
from utils.rss_crawler import fetch_rss

# Load environment variables
load_dotenv()

# Setup logging chi tiết
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"test_30_articles_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def test_30_articles():
    """Test với 30 bài báo và ghi log chi tiết"""

    # Kiểm tra API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False

    print("🎯 Testing 30 Articles with Optimized Prompt")
    print("=" * 60)
    logging.info("=" * 60)
    logging.info("🎯 STARTED: Testing 30 Articles with Optimized Prompt")
    logging.info("=" * 60)

    # Khởi tạo analyzer
    analyzer = NewsAnalyzer(api_key)

    # RSS feeds để lấy bài báo
    rss_feeds = [
        {"url": "https://vnexpress.net/rss/giao-duc.rss",
            "category": "giao-duc", "count": 8},
        {"url": "https://vnexpress.net/rss/suc-khoe.rss",
            "category": "suc-khoe", "count": 8},
        {"url": "https://vnexpress.net/rss/gia-dinh.rss",
            "category": "gia-dinh", "count": 7},
        {"url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss",
            "category": "khoa-hoc-cong-nghe", "count": 7},
    ]

    print("📡 Collecting 30 articles from RSS feeds...")
    logging.info("📡 Collecting 30 articles from RSS feeds...")

    all_articles = []

    # Lấy articles từ multiple RSS feeds
    for feed in rss_feeds:
        print(
            f"📊 Fetching {feed['count']} articles from {feed['category']}...")
        logging.info(
            f"📊 Fetching {feed['count']} articles from {feed['category']}...")

        try:
            entries = fetch_rss(feed['url'])
            if entries:
                selected = entries[:feed['count']]
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
                logging.info(
                    f"   ✅ Added {len(selected)} articles from {feed['category']}")
            else:
                print(f"   ⚠️ No articles found")
                logging.warning(
                    f"   ⚠️ No articles found for {feed['category']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            logging.error(f"   ❌ Error fetching {feed['category']}: {e}")

    # Đảm bảo đúng 30 articles
    if len(all_articles) > 30:
        all_articles = all_articles[:30]

    print(f"\n🎯 Processing exactly {len(all_articles)} articles")
    print("=" * 60)
    logging.info(f"🎯 Processing exactly {len(all_articles)} articles")
    logging.info("=" * 60)

    # Statistics tracking
    stats = {
        'total': len(all_articles),
        'analyzed': 0,
        'positive': 0,
        'negative': 0,
        'neutral': 0,
        'stored': 0,
        'errors': 0,
        'quota_errors': 0,
        'categories': {},
        'results': [],
        'start_time': datetime.now().isoformat(),
        'prompt_version': 'optimized_no_icons'
    }

    # Process each article
    for i, article in enumerate(all_articles, 1):
        title = article['title']
        print(f"\n📝 [{i:2d}/30] {title[:70]}...")
        print(f"🔗 {article['link']}")
        print(f"📂 Source: {article['source_category']}")

        logging.info(f"📝 [{i:2d}/30] Processing: {title}")
        logging.info(f"🔗 URL: {article['link']}")
        logging.info(f"📂 Source category: {article['source_category']}")

        try:
            # Rate limiting - đợi 3 giây giữa các requests
            if i > 1:
                print("⏳ Waiting 3 seconds (rate limiting)...")
                logging.info("⏳ Rate limiting: waiting 3 seconds...")
                time.sleep(3)

            # Ghi log trước khi phân tích
            logging.info(f"🤖 Calling Gemini API for article {i}")

            # Phân tích bài báo
            start_time = time.time()
            result = analyzer.analyze_and_transform(article)
            end_time = time.time()
            processing_time = end_time - start_time

            logging.info(f"⏱️ Processing time: {processing_time:.2f} seconds")

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
                    'title': title[:100],
                    'link': article.get('link', ''),
                    'category': category,
                    'sentiment': sentiment,
                    'is_toxic': result.get('is_toxic', False),
                    'description': result.get('description', '')[:200],
                    'source_category': article['source_category'],
                    'processing_time': processing_time
                }
                stats['results'].append(article_result)

                print(f"✅ Analysis successful!")
                print(f"   📂 Category: {category}")
                print(
                    f"   😊 Sentiment: {sentiment} ({'POSITIVE' if sentiment==1 else 'NEGATIVE' if sentiment==-1 else 'NEUTRAL'})")
                print(f"   🚫 Toxic: {result.get('is_toxic', False)}")
                print(
                    f"   📝 Description: {result.get('description', '')[:100]}...")
                print(f"   ⏱️ Time: {processing_time:.2f}s")

                logging.info(f"✅ Analysis successful for article {i}")
                logging.info(f"   📂 Category: {category}")
                logging.info(f"   😊 Sentiment: {sentiment}")
                logging.info(f"   🚫 Toxic: {result.get('is_toxic', False)}")
                logging.info(
                    f"   📝 Description: {result.get('description', '')}")

                # Lưu vào Firebase nếu positive hoặc neutral và không toxic
                if sentiment >= 0 and not result.get('is_toxic', True):
                    try:
                        if store_to_firebase(result, collection_name='test_30_articles'):
                            stats['stored'] += 1
                            print(f"   💾 ✅ Stored to Firebase")
                            logging.info(
                                f"   💾 ✅ Stored to Firebase collection: test_30_articles")
                        else:
                            print(f"   💾 ❌ Failed to store")
                            logging.warning(
                                f"   💾 ❌ Failed to store to Firebase")
                    except Exception as e:
                        print(f"   💾 ❌ Store error: {e}")
                        logging.error(f"   💾 ❌ Firebase store error: {e}")
                else:
                    print(f"   💾 ⚠️ Not stored (negative/toxic)")
                    logging.info(
                        f"   💾 ⚠️ Not stored - sentiment: {sentiment}, toxic: {result.get('is_toxic', False)}")
            else:
                print(f"❌ Analysis failed or filtered out")
                logging.warning(f"❌ Analysis failed for article {i}: {title}")
                stats['results'].append({
                    'index': i,
                    'title': title[:100],
                    'link': article.get('link', ''),
                    'status': 'FAILED',
                    'source_category': article['source_category'],
                    'processing_time': processing_time
                })

        except Exception as e:
            stats['errors'] += 1
            error_msg = str(e)

            # Check if it's a quota error
            if "quota" in error_msg.lower() or "429" in error_msg:
                stats['quota_errors'] += 1
                print(f"🚨 Quota exceeded! Stopping test at article {i}")
                logging.error(f"🚨 QUOTA EXCEEDED at article {i}: {error_msg}")
                break
            else:
                print(f"❌ Error processing article: {e}")
                logging.error(f"❌ Error processing article {i}: {error_msg}")
                stats['results'].append({
                    'index': i,
                    'title': title[:100],
                    'status': 'ERROR',
                    'error': error_msg,
                    'source_category': article['source_category']
                })

    # Finalize stats
    stats['end_time'] = datetime.now().isoformat()
    stats['total_duration'] = (datetime.fromisoformat(
        stats['end_time']) - datetime.fromisoformat(stats['start_time'])).total_seconds()

    # Print detailed results
    print("\n" + "=" * 60)
    print("📊 DETAILED TEST RESULTS - 30 ARTICLES")
    print("=" * 60)

    logging.info("=" * 60)
    logging.info("📊 DETAILED TEST RESULTS - 30 ARTICLES")
    logging.info("=" * 60)

    print(f"📈 OVERALL STATISTICS:")
    print(f"   Total Articles: {stats['total']}")
    print(f"   Successfully Analyzed: {stats['analyzed']}")
    print(f"   Errors: {stats['errors']}")
    print(f"   Quota Errors: {stats['quota_errors']}")
    print(f"   Success Rate: {(stats['analyzed']/stats['total']*100):.1f}%")
    print(f"   Total Duration: {stats['total_duration']:.1f} seconds")

    logging.info(f"📈 OVERALL STATISTICS:")
    logging.info(f"   Total Articles: {stats['total']}")
    logging.info(f"   Successfully Analyzed: {stats['analyzed']}")
    logging.info(f"   Errors: {stats['errors']}")
    logging.info(f"   Quota Errors: {stats['quota_errors']}")
    logging.info(
        f"   Success Rate: {(stats['analyzed']/stats['total']*100):.1f}%")
    logging.info(f"   Total Duration: {stats['total_duration']:.1f} seconds")

    print(f"\n😊 SENTIMENT BREAKDOWN:")
    print(
        f"   Positive: {stats['positive']} ({stats['positive']/max(stats['analyzed'],1)*100:.1f}%)")
    print(
        f"   Negative: {stats['negative']} ({stats['negative']/max(stats['analyzed'],1)*100:.1f}%)")
    print(
        f"   Neutral: {stats['neutral']} ({stats['neutral']/max(stats['analyzed'],1)*100:.1f}%)")

    logging.info(f"😊 SENTIMENT BREAKDOWN:")
    logging.info(
        f"   Positive: {stats['positive']} ({stats['positive']/max(stats['analyzed'],1)*100:.1f}%)")
    logging.info(
        f"   Negative: {stats['negative']} ({stats['negative']/max(stats['analyzed'],1)*100:.1f}%)")
    logging.info(
        f"   Neutral: {stats['neutral']} ({stats['neutral']/max(stats['analyzed'],1)*100:.1f}%)")

    print(f"\n📂 CATEGORY DISTRIBUTION:")
    for category, count in stats['categories'].items():
        print(f"   {category}: {count} articles")
        logging.info(f"   Category {category}: {count} articles")

    print(f"\n💾 STORAGE:")
    print(f"   Stored to Firebase: {stats['stored']}")
    print(
        f"   Storage Rate: {(stats['stored']/max(stats['positive'],1)*100):.1f}% of positive articles")

    logging.info(f"💾 STORAGE:")
    logging.info(f"   Stored to Firebase: {stats['stored']}")
    logging.info(
        f"   Storage Rate: {(stats['stored']/max(stats['positive'],1)*100):.1f}% of positive articles")

    # Save results to JSON
    results_file = f"test_results_30_{timestamp}.json"

    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
        print(f"📄 Log saved to: {log_filename}")
        logging.info(f"💾 Results saved to: {results_file}")
        logging.info(f"📄 Log saved to: {log_filename}")
    except Exception as e:
        print(f"⚠️ Failed to save results: {e}")
        logging.error(f"⚠️ Failed to save results: {e}")

    print("\n" + "=" * 60)
    print("🎯 TEST COMPLETED!")
    print(f"🔍 Check Firebase collection 'test_30_articles' for stored results")
    print(f"📊 Check {results_file} for detailed JSON results")
    print(f"📄 Check {log_filename} for detailed logs")
    print("=" * 60)

    logging.info("=" * 60)
    logging.info("🎯 TEST COMPLETED!")
    logging.info(f"🔍 Firebase collection: test_30_articles")
    logging.info(f"📊 JSON results: {results_file}")
    logging.info(f"📄 Log file: {log_filename}")
    logging.info("=" * 60)

    return stats['analyzed'] > 0


if __name__ == "__main__":
    print("🧪 30 Articles Test Script with Optimized Prompt")
    print("This will test 30 articles with the token-optimized prompt")
    print("Make sure you have sufficient Gemini API quota (30 requests needed)")

    input("\nPress Enter to start the test...")

    success = test_30_articles()

    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n⚠️ Test encountered issues. Check logs for details.")
