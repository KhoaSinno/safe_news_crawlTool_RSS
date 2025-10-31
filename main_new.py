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

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_crawler.log'),
        logging.StreamHandler()
    ]
)

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
    {"url": "https://vnexpress.net/rss/tin-moi-nhat.rss", "category": "tin-moi-nhat"},
    # {"url": "https://vnexpress.net/rss/tin-noi-bat.rss", "category": "tin-noi-bat"},
    # {"url": "https://vnexpress.net/rss/tin-xem-nhieu.rss", "category": "tin-xem-nhieu"},

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


def crawl_and_analyze(use_test_collection=False):
    """
    Crawl RSS feeds và phân tích với NewsAnalyzer mới
    Args:
        use_test_collection: True để lưu vào test collection
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

                    if result:
                        # Lưu vào Firebase
                        if store_to_firebase(result, collection_name=collection_name):
                            total_stored += 1
                            category_stored += 1
                            logging.info(
                                f"✅ Stored positive article: {title[:50]}...")
                        else:
                            logging.warning(
                                f"⚠️ Failed to store: {title[:50]}...")
                    else:
                        logging.info(
                            f"❌ Article filtered out: {title[:50]}...")

                    # Thêm vào danh sách đã xử lý
                    new_processed_links.append(link)

                    # Rate limiting - đợi 2 giây giữa các bài để tránh spam API
                    time.sleep(2)

                except Exception as e:
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


def run_test_crawl():
    """Chạy test crawl với collection test"""
    logging.info("🧪 Running TEST crawl...")
    crawl_and_analyze(use_test_collection=True)


def run_production_crawl():
    """Chạy production crawl"""
    logging.info("🚀 Running PRODUCTION crawl...")
    crawl_and_analyze(use_test_collection=False)


def schedule_crawls():
    """Lập lịch crawl tự động"""
    # Test crawl - mỗi 30 phút (OPTIONAL)
    # schedule.every(30).minutes.do(run_test_crawl)

    # Production crawl - mỗi 1 giờ
    schedule.every(1).hours.do(run_production_crawl)

    logging.info("⏰ Scheduled crawls:")
    # logging.info("   🧪 Test crawl: Every 30 minutes")
    logging.info("   🚀 Production crawl: Every 1 hour")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            # Chạy test ngay
            run_test_crawl()
        elif command == "production":
            # Chạy production ngay
            run_production_crawl()
        elif command == "schedule":
            print("GEMINI_API_KEY:", GEMINI_API_KEY)

            # Chạy scheduled mode
            schedule_crawls()

            logging.info("🚀 Starting scheduled crawler...")
            logging.info("Press Ctrl+C to stop")

            try:
                # Chạy production crawl ngay lập tức
                run_production_crawl()

                # Sau đó chạy theo schedule
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check mỗi phút

            except KeyboardInterrupt:
                logging.info("⏹️ Crawler stopped by user")
        else:
            print("Usage: python main_new.py [test|production|schedule]")
    else:
        print("🚀 Safe News Crawler - New Implementation")
        print("Commands:")
        print("  python main_new.py test        - Run test crawl (saves to positive_news_test)")
        print("  python main_new.py production  - Run production crawl (saves to positive_news)")
        print("  python main_new.py schedule    - Run scheduled crawler")
