# 🔧 Quick Reference & Debug Guide

## 🚀 Chạy nhanh

```bash
# Test từng component
python utils/gemini_filter.py        # Test AI analysis
python -c "from utils.firebase_handler import store_news; print('Firebase OK')"
python -c "from utils.rss_crawler import fetch_rss; print(len(fetch_rss('https://vnexpress.net/rss/tin-moi-nhat.rss')))"

# Chạy full system
python main.py
```

## 🐛 Common Issues & Solutions

### 1. Firebase Error

```
firebase_admin.exceptions.InvalidArgumentError: Failed to initialize app
```

**Fix:** Check `serviceAccountKey.json` exists and valid

### 2. Gemini API Error  

```
requests.exceptions.HTTPError: 429 Client Error
```

**Fix:** Rate limit hit, wait 1 minute or check API key

### 3. Cache Database Locked

```
sqlite3.OperationalError: database is locked
```

**Fix:** Close other processes or delete `analysis_cache.db`

## 📊 Monitor Performance

```python
# Check cache hit rate
import sqlite3
conn = sqlite3.connect('analysis_cache.db')
count = conn.execute("SELECT COUNT(*) FROM analysis_cache").fetchone()[0]
print(f"Cache entries: {count}")

# Check API usage
from utils.gemini_filter import GeminiNewsFilter
filter = GeminiNewsFilter('your-key')
print(filter.get_stats())
```

## 🔍 Debug Code Flow

```python
# Trace một bài báo qua hệ thống
title = "Test news title"
content = "Test content"

# 1. Check cache
from utils.gemini_filter import ResultCache
cache = ResultCache()
cached = cache.get_cached_result(f"{title}. {content}")
print(f"Cached: {cached}")

# 2. AI analysis
from utils.gemini_filter import GeminiNewsFilter
analyzer = GeminiNewsFilter('your-api-key')
result = analyzer.analyze_news(title, content)
print(f"Analysis: {result}")

# 3. Firebase save
from utils.firebase_handler import store_news
entry = {'title': title, 'link': 'test-link', 'category': 'test'}
saved = store_news(entry, result['sentiment'], result['toxicity'])
print(f"Saved: {saved}")
```
