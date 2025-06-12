import schedule
import time
from utils.rss_crawler import fetch_rss
from utils.news_filter import analyze_sentiment, detect_toxicity
from utils.firebase_handler import store_news

print("Starting safe_news program...")

def job():
    print("Starting RSS crawl at", time.ctime())
    rss_url = "https://vnexpress.net/rss/doi-song.rss"
    try:
        entries = fetch_rss(rss_url)
        print(f"Fetched {len(entries)} articles")
        for entry in entries:
            text = entry.description or entry.title
            sentiment = analyze_sentiment(text)
            is_toxic = detect_toxicity(text)
            print(f"Title: {entry.title}, Sentiment: {sentiment}, Toxic: {is_toxic}")
            store_news(entry, sentiment, is_toxic)
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