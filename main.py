"""
Safe News Crawler
Sử dụng NewsAnalyzer mới với Firebase integration tối ưu
Features:
- Simple title + URL analysis with Gemini
- Transform to Firebase schema
- Auto crawl với rate limiting
- Test collection support
"""

import schedule
import time
import logging
from datetime import datetime
from utils.rss_crawler import fetch_rss
from utils.news_analyzer import NewsAnalyzer
from utils.firebase_handler import store_to_firebase
import json
import os
from dotenv import load_dotenv

# Load environment variables - FORCE OVERRIDE system env
load_dotenv(override=True)

# Setup logging with UTF-8 and immediate flush for real-time tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True  # Force reconfigure if already configured
)

# Ensure immediate flush to file (real-time logging)
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.INFO)
        # Force immediate write without buffering
        handler.stream.reconfigure(line_buffering=True)

# Cấu hình
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. Please check your .env file.")

CRAWL_STATE_FILE = "crawl_state.json"

# Khởi tạo News Analyzer
news_analyzer = NewsAnalyzer(GEMINI_API_KEY)

# RSS feeds to crawl - ưu tiên các category tích cực
RSS_FEEDS = [
    # {"url": "https://vnexpress.net/rss/tin-moi-nhat.rss", "category": "tin-moi-nhat"},
    # {"url": "https://vnexpress.net/rss/tin-noi-bat.rss", "category": "tin-noi-bat"},
    {"url": "https://vnexpress.net/rss/tin-xem-nhieu.rss", "category": "tin-xem-nhieu"},

    # {"url": "https://vnexpress.net/rss/giao-duc.rss", "category": "giao-duc"},
    # {"url": "https://vnexpress.net/rss/suc-khoe.rss", "category": "suc-khoe"},
    # {"url": "https://vnexpress.net/rss/gia-dinh.rss", "category": "gia-dinh"},
    # {"url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss",
    #     "category": "khoa-hoc-cong-nghe"},
    # {"url": "https://vnexpress.net/rss/startup.rss", "category": "startup"},
    # {"url": "https://vnexpress.net/rss/du-lich.rss", "category": "du-lich"},
    # {"url": "https://vnexpress.net/rss/giai-tri.rss", "category": "giai-tri"},
    # {"url": "https://vnexpress.net/rss/the-thao.rss", "category": "the-thao"},
]


def load_crawl_state():
    """Load trạng thái crawl từ file để track bài đã xử lý"""
    if os.path.exists(CRAWL_STATE_FILE):
        try:
            with open(CRAWL_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading crawl state: {e}")

    return {"last_crawl": None, "processed_links": []}


def save_crawl_state(state):
    """Lưu trạng thái crawl"""
    try:
        with open(CRAWL_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving crawl state: {e}")


def is_new_article(link, processed_links, max_history=1000):
    """Kiểm tra bài báo có mới không dựa trên link"""
    # Giữ chỉ max_history links gần nhất
    if len(processed_links) > max_history:
        processed_links[:] = processed_links[-max_history:]

    return link not in processed_links


def crawl_and_analyze(use_test_collection=False, save_logs=False):
    """
    Crawl RSS feeds và phân tích với NewsAnalyzer mới
    Args:
        use_test_collection: True để lưu vào test collection
        save_logs: True để lưu detailed logs vào logs_prod/
    """
    # Reload .env mỗi lần crawl
    load_dotenv(override=True)
    global GEMINI_API_KEY, news_analyzer
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    news_analyzer = NewsAnalyzer(GEMINI_API_KEY)

    logging.info("🚀 Starting news crawl and analysis...")

    collection_name = 'positive_news_test' if use_test_collection else 'positive_news'

    # Load trạng thái crawl
    crawl_state = load_crawl_state()
    processed_links = crawl_state.get("processed_links", [])

    total_crawled = 0
    total_analyzed = 0
    total_stored = 0
    new_processed_links = []

    # Detailed logs for tracking - Always create in schedule mode
    detailed_logs = {
        "total": 0,
        "analyzed": 0,
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "toxic": 0,
        "stored": 0,
        "filtered": 0,  # Articles analyzed but filtered (negative/toxic)
        "errors": 0,
        "categories": {},
        "results": [],
        "timestamp": datetime.now().isoformat(),
        "collection": collection_name
    } if save_logs else None

    for rss_feed in RSS_FEEDS:
        rss_url = rss_feed["url"]
        category = rss_feed["category"]

        logging.info(f"📡 Crawling {category}: {rss_url}")

        try:
            # Fetch RSS entries
            entries = fetch_rss(rss_url)

            if not entries:
                logging.warning(f"⚠️ No entries found for {category}")
                continue

            logging.info(f"📊 Found {len(entries)} entries for {category}")

            # Xử lý từng entry
            category_analyzed = 0
            category_stored = 0

            for entry in entries:
                link = entry.get('link', '')
                title = entry.get('title', 'No title')

                total_crawled += 1

                # Skip nếu đã xử lý
                if not is_new_article(link, processed_links):
                    continue

                # Track total articles if logging
                if save_logs:
                    detailed_logs["total"] += 1

                # Chuẩn bị dữ liệu RSS
                rss_data = {
                    "title": title,
                    "link": link,
                    "category": category,
                    "summary": entry.get('summary', ''),
                    "image_url": entry.get('image_url', ''),
                    "published": entry.get('published', '')
                }

                logging.info(f"🔍 Analyzing: {title[:60]}...")

                try:
                    # Phân tích với NewsAnalyzer
                    result = news_analyzer.analyze_and_transform(rss_data)
                    total_analyzed += 1
                    category_analyzed += 1

                    # Log detailed analysis result
                    if save_logs:
                        detailed_logs["analyzed"] += 1

                        log_entry = {
                            "index": detailed_logs["total"],
                            "title": title,
                            "link": link,
                            "source_category": category
                        }

                    if result:
                        # Track sentiment and toxicity stats
                        if save_logs:
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
                                detailed_logs["categories"].get(
                                    result_category, 0) + 1

                            # Add to log entry
                            log_entry.update({
                                "category": result_category,
                                "sentiment": sentiment,
                                "is_toxic": is_toxic,
                                "description": result.get('description', '')[:200]
                            })

                        # ⚠️ CRITICAL: Chỉ lưu bài POSITIVE/NEUTRAL và SAFE vào Firebase
                        sentiment = result.get('sentiment', 0)
                        is_toxic = result.get('is_toxic', False)

                        # Check if article should be stored
                        should_store = sentiment >= 0 and not is_toxic

                        if should_store:
                            # Lưu vào Firebase
                            if store_to_firebase(result, collection_name=collection_name):
                                total_stored += 1
                                category_stored += 1
                                if save_logs:
                                    detailed_logs["stored"] += 1
                                    log_entry["status"] = "STORED"
                                logging.info(
                                    f"✅ Stored positive article: {title[:50]}...")
                            else:
                                if save_logs:
                                    log_entry["status"] = "STORAGE_FAILED"
                                logging.warning(
                                    f"⚠️ Failed to store: {title[:50]}...")
                        else:
                            # Article filtered out due to negative sentiment or toxic content
                            if save_logs:
                                log_entry["status"] = "FILTERED_OUT"
                                detailed_logs["filtered"] += 1
                            sentiment_label = "POSITIVE" if sentiment == 1 else (
                                "NEUTRAL" if sentiment == 0 else "NEGATIVE")
                            toxic_label = "TOXIC" if is_toxic else "SAFE"
                            logging.info(
                                f"⚠️ Article filtered out: {title[:50]}... ({sentiment_label}, {toxic_label})")
                    else:
                        if save_logs:
                            log_entry["status"] = "FILTERED_OUT"
                        logging.info(
                            f"❌ Article filtered out: {title[:50]}...")

                    # Add log entry to results
                    if save_logs:
                        detailed_logs["results"].append(log_entry)

                    # Thêm vào danh sách đã xử lý
                    new_processed_links.append(link)

                    # Rate limiting - DISABLED (có 10k RPM rồi)
                    # time.sleep(2)

                except Exception as e:
                    if save_logs:
                        detailed_logs["errors"] += 1
                        detailed_logs["results"].append({
                            "index": detailed_logs["total"],
                            "title": title,
                            "link": link,
                            "source_category": category,
                            "status": "ERROR",
                            "error": str(e)
                        })
                    logging.error(
                        f"❌ Error analyzing article: {title[:50]}... Error: {e}")
                    new_processed_links.append(link)  # Vẫn mark là đã xử lý

            logging.info(
                f"📊 {category} summary: {category_analyzed} analyzed, {category_stored} stored")

        except Exception as e:
            logging.error(f"❌ Error crawling {category}: {e}")

    # Cập nhật trạng thái crawl
    crawl_state["processed_links"].extend(new_processed_links)
    crawl_state["last_crawl"] = datetime.now().isoformat()
    save_crawl_state(crawl_state)

    # Summary
    logging.info("=" * 50)
    logging.info(f"🏁 CRAWL SUMMARY:")
    logging.info(f"   📡 Total crawled: {total_crawled}")
    logging.info(f"   🔍 Total analyzed: {total_analyzed}")
    logging.info(f"   💾 Total stored: {total_stored}")
    logging.info(
        f"   📈 Success rate: {(total_stored/max(total_analyzed, 1)*100):.1f}%")
    logging.info(f"   🔥 Collection: {collection_name}")
    logging.info("=" * 50)

    # Save detailed logs to file - Always save in schedule mode for tracking
    if save_logs:
        try:
            # Create logs_prod directory if not exists
            os.makedirs("logs_prod", exist_ok=True)

            # Generate unique timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"logs_prod/crawl_result_{timestamp}.json"

            # Save to JSON file
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(detailed_logs, f, ensure_ascii=False, indent=2)

            if detailed_logs["total"] > 0:
                logging.info(f"📝 Detailed logs saved to: {log_filename}")
            else:
                logging.info(
                    f"📝 Crawl log saved (no new articles): {log_filename}")
        except Exception as e:
            logging.error(f"❌ Failed to save detailed logs: {e}")


def run_test_crawl(save_logs=False):
    """Chạy test crawl với collection test"""
    logging.info("🧪 Running TEST crawl...")
    crawl_and_analyze(use_test_collection=True, save_logs=save_logs)


def run_production_crawl(save_logs=False):
    """Chạy production crawl"""
    logging.info("🚀 Running PRODUCTION crawl...")
    crawl_and_analyze(use_test_collection=False, save_logs=save_logs)


def schedule_crawls(save_logs=False):
    """Lập lịch crawl tự động"""
    # Test crawl - mỗi 30 phút (OPTIONAL)
    # schedule.every(30).minutes.do(run_test_crawl, save_logs=save_logs)

    # Production crawl - mỗi 1 giờ
    # schedule.every(1).hours.do(run_production_crawl, save_logs=save_logs)

    # Production crawl - mỗi 15 phút
    schedule.every(15).minutes.do(run_production_crawl, save_logs=save_logs)

    logging.info("⏰ Scheduled crawls:")
    # logging.info("   🧪 Test crawl: Every 30 minutes")
    logging.info("   🚀 Production crawl: Every 15 minutes")
    if save_logs:
        logging.info("   📝 Detailed logging: ENABLED")


if __name__ == "__main__":
    import sys

    # Check for --save-logs flag
    save_logs = '--save-logs' in sys.argv
    if save_logs:
        sys.argv.remove('--save-logs')

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            # Chạy test ngay
            run_test_crawl(save_logs=save_logs)
        elif command == "production":
            # Chạy production ngay
            run_production_crawl(save_logs=save_logs)
        elif command == "schedule":
            # print("GEMINI_API_KEY:", GEMINI_API_KEY)

            # Chạy scheduled mode - Default "on": save_logs cho production
            # User có thể tắt bằng --no-logs nếu cần
            if '--no-logs' not in sys.argv and not save_logs:
                save_logs = True
                logging.info(
                    "📝 Auto-enabled detailed logging for schedule mode")

            schedule_crawls(save_logs=save_logs)

            logging.info("🚀 Starting scheduled crawler...")
            logging.info("Press Ctrl+C to stop")

            try:
                # Chạy production crawl ngay lập tức
                run_production_crawl(save_logs=save_logs)

                # Sau đó chạy theo schedule
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check mỗi phút

            except KeyboardInterrupt:
                logging.info("⏹️ Crawler stopped by user")
        else:
            print(
                "Usage: python main.py [test|production|schedule] [--save-logs]")
    else:
        print("🚀 Safe News Crawler - New Implementation")
        print("Commands:")
        print(
            "  python main.py test [--save-logs]       - Run test crawl (saves to positive_news_test)")
        print(
            "  python main.py production [--save-logs] - Run production crawl (saves to positive_news)")
        print(
            "  python main.py schedule [--save-logs]   - Run scheduled crawler")
        print("\nOptions:")
        print(
            "  --save-logs  - Save detailed analysis logs to logs_prod/crawl_result_[timestamp].json")
