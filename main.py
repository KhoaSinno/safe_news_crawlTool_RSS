"""
Safe News Crawler - Enhanced Pipeline (Phase 1)
Kiến trúc lọc đa tầng:
- Tầng 1: Fast Rule Filter (0ms, 0đ API) loại bỏ án mạng, tử vong, bạo lực
- Tầng 2: Trafilatura bóc tách text bài báo sạch từ URL
- Tầng 3: Gemini 2.5 Flash phân tích sắc thái và tóm tắt
- Firebase Firestore Storage
"""

import schedule
import time
import logging
from datetime import datetime
import json
import os
import sys
from dotenv import load_dotenv

from utils.rss_crawler import fetch_rss
from utils.news_analyzer import NewsAnalyzer
from utils.rule_filter import RuleFilter
from utils.firebase_handler import store_to_firebase

# Load environment variables
load_dotenv(override=True)

# Setup logging với UTF-8 và immediate flush
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True
)

for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.INFO)
        handler.stream.reconfigure(line_buffering=True)

# Cấu hình API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check .env file.")

CRAWL_STATE_FILE = "crawl_state.json"

# Khởi tạo các module
rule_filter = RuleFilter()
news_analyzer = NewsAnalyzer(GEMINI_API_KEY)

# Danh sách nguồn RSS
RSS_FEEDS = [
    {"url": "https://vnexpress.net/rss/tin-moi-nhat.rss", "category": "tin-moi-nhat"},
    # {"url": "https://vnexpress.net/rss/giao-duc.rss", "category": "giao-duc"},
    # {"url": "https://vnexpress.net/rss/suc-khoe.rss", "category": "suc-khoe"},
    # {"url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss", "category": "khoa-hoc-cong-nghe"},
]


def load_crawl_state():
    """Load trạng thái crawl từ file"""
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


def is_new_article(link, processed_links, max_history=2000):
    """Kiểm tra bài báo có mới không dựa trên link"""
    if len(processed_links) > max_history:
        processed_links[:] = processed_links[-max_history:]
    return link not in processed_links


def crawl_and_analyze(use_test_collection=False, save_logs=False, max_articles_per_feed=None):
    """
    Crawl RSS feeds và phân tích qua kiến trúc 3 tầng tối ưu
    Args:
        use_test_collection: True để lưu vào collection positive_news_test
        save_logs: True để lưu detailed logs vào logs_prod/
        max_articles_per_feed: Giới hạn số bài xử lý mỗi feed (dùng khi test)
    """
    load_dotenv(override=True)
    global GEMINI_API_KEY, news_analyzer, rule_filter
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    news_analyzer = NewsAnalyzer(GEMINI_API_KEY)
    rule_filter = RuleFilter()

    logging.info("🚀 Starting news crawl and multi-stage analysis pipeline...")
    collection_name = 'positive_news_test' if use_test_collection else 'positive_news'

    crawl_state = load_crawl_state()
    processed_links = crawl_state.get("processed_links", [])

    total_crawled = 0
    total_filtered_by_rule = 0
    total_analyzed = 0
    total_stored = 0
    total_prompt_tokens = 0
    total_candidate_tokens = 0
    total_tokens = 0
    total_llm_time = 0.0
    total_extract_time = 0.0
    new_processed_links = []

    detailed_logs = {
        "total": 0,
        "filtered_by_rule": 0,
        "analyzed_by_ai": 0,
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "toxic": 0,
        "stored": 0,
        "filtered_by_ai": 0,
        "errors": 0,
        "metrics": {
            "total_prompt_tokens": 0,
            "total_candidate_tokens": 0,
            "total_tokens": 0,
            "total_llm_time": 0.0,
            "total_extract_time": 0.0
        },
        "results": [],
        "timestamp": datetime.now().isoformat(),
        "collection": collection_name
    } if save_logs else None

    for rss_feed in RSS_FEEDS:
        rss_url = rss_feed["url"]
        category = rss_feed["category"]

        logging.info(f"📡 Crawling category [{category}]: {rss_url}")

        try:
            entries = fetch_rss(rss_url)
            if not entries:
                logging.warning(f"⚠️ No entries found for {category}")
                continue

            if max_articles_per_feed:
                entries = entries[:max_articles_per_feed]

            logging.info(f"📊 Found {len(entries)} entries for {category}")

            for entry in entries:
                link = entry.get('link', '')
                title = entry.get('title', 'No title')
                summary = entry.get('summary', '')

                total_crawled += 1

                # 0. Bỏ qua nếu bài đã xử lý
                if not is_new_article(link, processed_links):
                    continue

                if save_logs:
                    detailed_logs["total"] += 1

                # =========================================================================
                # 🎯 TẦNG 1: Fast Rule Filter (0ms, 0 Token Cost)
                # =========================================================================
                is_blocked_by_rule, block_reason = rule_filter.check_article(title, summary)
                if is_blocked_by_rule:
                    total_filtered_by_rule += 1
                    new_processed_links.append(link)

                    if save_logs:
                        detailed_logs["filtered_by_rule"] += 1
                        detailed_logs["results"].append({
                            "index": detailed_logs["total"],
                            "title": title,
                            "link": link,
                            "source_category": category,
                            "status": "FILTERED_BY_FAST_RULE",
                            "reason": block_reason
                        })

                    logging.info(f"⚡ [FAST-RULE-FILTERED] {title[:55]}... ({block_reason})")
                    continue

                # =========================================================================
                # 🎯 TẦNG 2 & 3: Trafilatura Extraction + Gemini 2.5 Flash Direct
                # =========================================================================
                rss_data = {
                    "title": title,
                    "link": link,
                    "category": category,
                    "summary": summary,
                    "image_url": entry.get('image_url', ''),
                    "published": entry.get('published', '')
                }

                try:
                    result = news_analyzer.analyze_and_transform(rss_data)
                    total_analyzed += 1
                    new_processed_links.append(link)

                    # Thu thập metrics
                    if result and '_metrics' in result:
                        m = result['_metrics']
                        total_prompt_tokens += m.get('prompt_tokens', 0)
                        total_candidate_tokens += m.get('candidates_tokens', 0)
                        total_tokens += m.get('total_tokens', 0)
                        total_llm_time += m.get('llm_time', 0.0)
                        total_extract_time += m.get('extract_time', 0.0)

                    if save_logs:
                        detailed_logs["analyzed_by_ai"] += 1
                        log_entry = {
                            "index": detailed_logs["total"],
                            "title": title,
                            "link": link,
                            "source_category": category,
                            "metrics": result.get('_metrics', {}) if result else {}
                        }

                    if result:
                        sentiment = result.get('sentiment', 0)
                        is_toxic = result.get('is_toxic', False)

                        if save_logs:
                            if sentiment == 1:
                                detailed_logs["positive"] += 1
                            elif sentiment == -1:
                                detailed_logs["negative"] += 1
                            else:
                                detailed_logs["neutral"] += 1

                            if is_toxic:
                                detailed_logs["toxic"] += 1

                            log_entry.update({
                                "sentiment": sentiment,
                                "is_toxic": is_toxic,
                                "description": result.get('description', '')[:200]
                            })

                        # Bộ lọc Gateway: Chỉ lưu POSITIVE/NEUTRAL và KHÔNG độc hại
                        should_store = (sentiment >= 0) and (not is_toxic)

                        if should_store:
                            if store_to_firebase(result, collection_name=collection_name):
                                total_stored += 1
                                if save_logs:
                                    detailed_logs["stored"] += 1
                                    log_entry["status"] = "STORED"
                                logging.info(f"✅ Stored safe article: {title[:50]}...")
                            else:
                                if save_logs:
                                    log_entry["status"] = "STORAGE_FAILED"
                                logging.warning(f"⚠️ Failed to store: {title[:50]}...")
                        else:
                            if save_logs:
                                detailed_logs["filtered_by_ai"] += 1
                                log_entry["status"] = "FILTERED_BY_AI"
                            logging.info(f"⚠️ AI Filtered: {title[:50]}... (sentiment: {sentiment}, toxic: {is_toxic})")

                    if save_logs:
                        detailed_logs["results"].append(log_entry)

                except Exception as e:
                    logging.error(f"❌ Error analyzing article '{title[:40]}': {e}")
                    if save_logs:
                        detailed_logs["errors"] += 1
                        detailed_logs["results"].append({
                            "index": detailed_logs["total"],
                            "title": title,
                            "link": link,
                            "status": "ERROR",
                            "error": str(e)
                        })

        except Exception as e:
            logging.error(f"❌ Error crawling category {category}: {e}")

    # Cập nhật metrics tổng vào logs
    if save_logs:
        detailed_logs["metrics"] = {
            "total_prompt_tokens": total_prompt_tokens,
            "total_candidate_tokens": total_candidate_tokens,
            "total_tokens": total_tokens,
            "total_llm_time": round(total_llm_time, 2),
            "total_extract_time": round(total_extract_time, 2),
            "avg_tokens_per_article": round(total_tokens / max(total_analyzed, 1), 1),
            "avg_latency_per_article": round((total_llm_time + total_extract_time) / max(total_analyzed, 1), 2)
        }

    # Cập nhật trạng thái crawl
    crawl_state["processed_links"].extend(new_processed_links)
    crawl_state["last_crawl"] = datetime.now().isoformat()
    save_crawl_state(crawl_state)

    # Thống kê tổng kết chi tiết
    avg_tokens = total_tokens / max(total_analyzed, 1)
    avg_extract = total_extract_time / max(total_analyzed, 1)
    avg_llm = total_llm_time / max(total_analyzed, 1)
    avg_total_lat = (total_extract_time + total_llm_time) / max(total_analyzed, 1)

    logging.info("=" * 65)
    logging.info("🏁 CRAWL & PIPELINE SUMMARY REPORT:")
    logging.info(f"   📡 Total Crawled:            {total_crawled} articles")
    logging.info(f"   ⚡ Filtered by Fast Rule:    {total_filtered_by_rule} articles (Saved ~{int(total_filtered_by_rule * avg_tokens)} tokens & {total_filtered_by_rule} API calls)")
    logging.info(f"   🤖 Analyzed by Gemini:       {total_analyzed} articles")
    logging.info(f"   💾 Stored to Firebase:       {total_stored} articles")
    if total_crawled > 0:
        api_savings = (total_filtered_by_rule / total_crawled) * 100
        logging.info(f"   💰 API Call Reduction:       {api_savings:.1f}%")
    logging.info(f"   ⏱️ Latency Metrics:")
    logging.info(f"      - Avg Trafilatura Extract: {avg_extract:.2f}s")
    logging.info(f"      - Avg Gemini LLM Time:     {avg_llm:.2f}s")
    logging.info(f"      - Avg Total Latency:       {avg_total_lat:.2f}s / article")
    logging.info(f"   🪙 Token Consumption:")
    logging.info(f"      - Prompt Tokens:           {total_prompt_tokens}")
    logging.info(f"      - Candidate Tokens:        {total_candidate_tokens}")
    logging.info(f"      - Total Tokens:            {total_tokens} (~{avg_tokens:.0f} tokens / article)")
    logging.info(f"   🔥 Collection:               {collection_name}")
    logging.info("=" * 65)

    # Lưu log chi tiết nếu bật
    if save_logs:
        try:
            os.makedirs("logs_prod", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"logs_prod/crawl_result_{timestamp}.json"
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(detailed_logs, f, ensure_ascii=False, indent=2)
            logging.info(f"📝 Detailed logs saved to: {log_filename}")
        except Exception as e:
            logging.error(f"❌ Failed to save detailed logs: {e}")


def run_test_crawl(save_logs=True, max_articles=30):
    """Chạy test crawl với collection positive_news_test"""
    logging.info(f"🧪 Running TEST crawl (max {max_articles} articles)...")
    crawl_and_analyze(use_test_collection=True, save_logs=save_logs, max_articles_per_feed=max_articles)


def run_production_crawl(save_logs=True):
    """Chạy production crawl vào collection positive_news"""
    logging.info("🚀 Running PRODUCTION crawl...")
    crawl_and_analyze(use_test_collection=False, save_logs=save_logs)


def schedule_crawls(save_logs=True):
    """Lập lịch chạy định kỳ mỗi 15 phút"""
    schedule.every(15).minutes.do(run_production_crawl, save_logs=save_logs)
    logging.info("⏰ Scheduled crawler: Running every 15 minutes")


if __name__ == "__main__":
    save_logs = '--save-logs' in sys.argv
    if save_logs:
        sys.argv.remove('--save-logs')

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "test":
            run_test_crawl(save_logs=True, max_articles=30)
        elif command == "production":
            run_production_crawl(save_logs=True)
        elif command == "schedule":
            schedule_crawls(save_logs=True)
            run_production_crawl(save_logs=True)
            while True:
                schedule.run_pending()
                time.sleep(60)
        else:
            print("Usage: python main.py [test|production|schedule] [--save-logs]")
    else:
        print("🚀 Safe News Crawler - Enhanced Phase 1")
        print("Commands:")
        print("  python main.py test        - Run test crawl on 30 articles (saves to positive_news_test)")
        print("  python main.py production  - Run production crawl (saves to positive_news)")
        print("  python main.py schedule    - Run periodic scheduled crawler (every 15 min)")
