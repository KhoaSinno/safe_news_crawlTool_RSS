"""
Safe News Crawler - Main Application
Tối ưu hóa crawl tin tức, phân tích cảm xúc, lưu tin tích cực vào Firebase
Features:
- Auto crawl theo schedule
- Smart duplicate detection  
- Rate limiting & caching
- Firebase integration
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from utils.rss_crawler import fetch_rss
from utils.gemini_filter import GeminiNewsFilter
from utils.firebase_handler import store_news
import json
import os

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
GEMINI_API_KEY = "AIzaSyCZbOdmDcqzmzJceMKWCznm-mlp8HBrsbk"
CRAWL_STATE_FILE = "crawl_state.json"

# Khởi tạo Gemini filter
news_analyzer = GeminiNewsFilter(GEMINI_API_KEY)

# RSS feeds to crawl
RSS_FEEDS = [
    {"url": "https://vnexpress.net/rss/tin-moi-nhat.rss", "category": "tin-moi-nhat"},
    {"url": "https://vnexpress.net/rss/tin-xem-nhieu.rss", "category": "tin-xem-nhieu"},
    {"url": "https://vnexpress.net/rss/the-gioi.rss", "category": "the-gioi"},
    {"url": "https://vnexpress.net/rss/thoi-su.rss", "category": "thoi-su"},
    {"url": "https://vnexpress.net/rss/kinh-doanh.rss", "category": "kinh-doanh"},
    {"url": "https://vnexpress.net/rss/startup.rss", "category": "startup"},
    {"url": "https://vnexpress.net/rss/giai-tri.rss", "category": "giai-tri"},
    {"url": "https://vnexpress.net/rss/the-thao.rss", "category": "the-thao"},
    {"url": "https://vnexpress.net/rss/phap-luat.rss", "category": "phap-luat"},
    {"url": "https://vnexpress.net/rss/giao-duc.rss", "category": "giao-duc"},
    {"url": "https://vnexpress.net/rss/suc-khoe.rss", "category": "suc-khoe"},
    {"url": "https://vnexpress.net/rss/gia-dinh.rss", "category": "gia-dinh"},
    {"url": "https://vnexpress.net/rss/du-lich.rss", "category": "du-lich"},
    {"url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss",
        "category": "khoa-hoc-cong-nghe"},
    {"url": "https://vnexpress.net/rss/oto-xe-may.rss", "category": "oto-xe-may"},
    {"url": "https://vnexpress.net/rss/y-kien.rss", "category": "y-kien"},
    {"url": "https://vnexpress.net/rss/tam-su.rss", "category": "tam-su"},
    {"url": "https://vnexpress.net/rss/cuoi.rss", "category": "cuoi"}
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
    """
    Kiểm tra bài báo có mới không dựa trên link
    Giới hạn history để tránh file quá lớn
    """
    # Giữ chỉ max_history links gần nhất
    if len(processed_links) > max_history:
        processed_links[:] = processed_links[-max_history:]

    return link not in processed_links


def crawl_and_analyze():
    """
    Main function để crawl và phân tích tin tức
    """
    start_time = datetime.now()
    logging.info("🚀 Bắt đầu crawl tin tức...")

    # Load trạng thái trước đó
    crawl_state = load_crawl_state()
    processed_links = crawl_state.get("processed_links", [])

    total_articles = 0
    new_articles = 0
    positive_articles = 0
    skipped_articles = 0

    try:
        for feed in RSS_FEEDS:
            logging.info(f"📡 Đang xử lý feed: {feed['category']}")

            try:
                entries = fetch_rss(feed['url'])
                logging.info(
                    f"Fetched {len(entries)} articles from {feed['category']}")

                for entry in entries:
                    total_articles += 1
                    entry['category'] = feed['category']

                    title = entry.get('title', '')
                    description = entry.get('description', '')
                    link = entry.get('link', '')

                    # Kiểm tra bài có mới không
                    if not is_new_article(link, processed_links):
                        skipped_articles += 1
                        continue

                    new_articles += 1
                    logging.info(f"📰 Đang phân tích bài mới: {title[:50]}...")

                    try:
                        # Phân tích bằng Gemini
                        analysis_result = news_analyzer.analyze_news(
                            title, description)
                        sentiment = analysis_result['sentiment']
                        is_toxic = analysis_result['toxicity']
                        confidence = analysis_result['confidence']

                        logging.info(
                            f"📊 Kết quả: {sentiment} (confidence: {confidence:.2f}, toxic: {is_toxic})")

                        # Lưu tin tích cực vào Firebase
                        if store_news(entry, sentiment, is_toxic):
                            positive_articles += 1
                            logging.info(f"✅ Đã lưu tin tích cực: {title}")

                        # Thêm vào danh sách đã xử lý
                        processed_links.append(link)

                    except Exception as e:
                        logging.error(
                            f"Lỗi phân tích bài '{title[:30]}...': {e}")

                    # Rate limiting
                    time.sleep(0.5)

            except Exception as e:
                logging.error(f"Lỗi xử lý feed {feed['category']}: {e}")

        # Lưu trạng thái
        crawl_state["last_crawl"] = datetime.now().isoformat()
        crawl_state["processed_links"] = processed_links
        save_crawl_state(crawl_state)

        # Thống kê
        stats = news_analyzer.get_stats()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        summary = f"""
📊 THỐNG KÊ CRAWL:
- Tổng số bài: {total_articles}
- Bài mới: {new_articles}  
- Bài đã tồn tại (bỏ qua): {skipped_articles}
- Bài tích cực được lưu: {positive_articles}
- Tỷ lệ tích cực: {positive_articles/new_articles*100 if new_articles > 0 else 0:.1f}%
- API calls đã dùng: {stats['requests_used']}
- API calls còn lại: {stats['requests_remaining']}
- Thời gian thực hiện: {duration:.1f}s
- Thời gian: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        print(summary)
        logging.info(summary)

    except Exception as e:
        error_msg = f"❌ Lỗi trong quá trình crawl: {e}"
        print(error_msg)
        logging.error(error_msg)


def test_api():
    """Test API trước khi bắt đầu crawl"""
    print("🤖 Safe News Crawler với Gemini 2.0 Flash API")
    print("=" * 50)

    try:
        test_result = news_analyzer.analyze_news(
            "Test bài viết",
            "Đây là bài test để kiểm tra API hoạt động"
        )
        print(f"✅ API test thành công: {test_result}")
        return True
    except Exception as e:
        print(f"❌ API test thất bại: {e}")
        return False


def main():
    """
    Main function để chạy crawler theo schedule
    """
    if not test_api():
        exit(1)

    print("⏰ Lập lịch chạy mỗi giờ...")
    print("📝 Logs được ghi vào news_crawler.log")
    print("💾 Trạng thái crawl được lưu vào crawl_state.json")
    print("Nhấn Ctrl+C để dừng")

    # Lập lịch chạy mỗi giờ
    schedule.every().hour.do(crawl_and_analyze)

    # Chạy job ngay lần đầu
    crawl_and_analyze()

    # Vòng lặp chính
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check mỗi phút
        except KeyboardInterrupt:
            print("\n👋 Program stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
