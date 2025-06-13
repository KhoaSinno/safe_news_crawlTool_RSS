import schedule
import time
from utils.rss_crawler import fetch_rss
from utils.news_filter import analyze_sentiment, detect_toxicity
from utils.firebase_handler import store_news

print("Starting safe_news program...")


def job():
    print("Starting RSS crawl at", time.ctime())
    rss_feeds = [
        {"url": "https://vnexpress.net/rss/tin-moi-nhat.rss",
            "category": "tin-moi-nhat"},
        {"url": "https://vnexpress.net/rss/tin-xem-nhieu.rss",
            "category": "tin-xem-nhieu"},
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
    try:
        for feed in rss_feeds:
            entries = fetch_rss(feed['url'])
            print(
                f"==================> Fetched {len(entries)} articles with category '{feed['category']}'")
            for entry in entries:
                entry['category'] = feed['category']
                text = entry['title'] + ' ' + entry['description']
                sentiment = analyze_sentiment(text)
                is_toxic = detect_toxicity(text)

                # Print
                print(
                    f"Title: {entry['title']}, Category: {entry['category']} , Sentiment: {sentiment}, Toxic: {is_toxic}")

                # Save to Firebase
                store_news(entry, sentiment, is_toxic)

                print("============================================\n")

    except Exception as e:
        print(f"Error in job: {e}")


print("Scheduling job every hour...")
schedule.every().hour.do(job)
job()  # Chạy lần đầu ngay lập tức

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        print("Program stopped by user")
        break
