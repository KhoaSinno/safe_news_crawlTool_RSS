# Safe News Crawler - AI Coding Agent Instructions

## Project Overview

**Safe News Crawler** is an automated Vietnamese news filtering system that crawls VNExpress RSS feeds, uses Google Gemini 2.0 Flash API for sentiment analysis, and stores only positive, family-friendly articles to Firebase Firestore.

**Architecture**: `RSS Feeds → Parse → Cache Check → Gemini AI Analysis → Filter → Firebase Storage`

## Core Components

### 1. **utils/rss_crawler.py** - RSS Feed Parser

- Uses `feedparser` to extract articles from VNExpress RSS feeds
- Cleans HTML from descriptions using BeautifulSoup
- Extracts: title, link, published date, description, image_url
- Returns list of article dictionaries

### 2. **utils/news_analyzer.py** - AI Analysis Engine

- **Key Class**: `NewsAnalyzer` - Integrates with Gemini 2.0 Flash API
- **Main Method**: `analyze_and_transform(rss_data)` - Sends title + URL to Gemini, receives structured analysis
- **Critical Feature**: Gemini reads FULL article content from URL (not just summary)
- **Rate Limiting**: Built-in 2-second delay between API calls via `_wait_for_rate_limit()`
- **In-memory Cache**: Uses MD5 hash of `title|url` to avoid duplicate API calls
- **Response Validation**: Requires `category`, `description`, `is_toxic` (bool), `sentiment` (1/0/-1)

**Prompt Engineering Philosophy**:

- Send minimal data (title + URL) to Gemini
- Let Gemini fetch and read full article content
- Request structured JSON response with strict schema
- Focus on Vietnamese news patterns and cultural context

### 3. **utils/firebase_handler.py** - Firebase Integration

- **Primary Function**: `store_to_firebase(firebase_data, collection_name)`
- **Duplicate Detection**: MD5 hash of `title|link` used as document ID
- **Schema** (8 required fields):
  ```python
  {
    'title': str,
    'category': str,  # from RSS feed
    'link': str,
    'description': str,  # from Gemini analysis
    'published': str,
    'image_url': str,
    'sentiment': int,  # 1=positive, 0=neutral, -1=negative
    'is_toxic': bool
  }
  ```
- **Collections**: `positive_news_test` (development), `positive_news` (production)
- **Legacy Function**: `store_news()` exists for backward compatibility but is not used

### 4. **main_new.py** - Application Orchestrator

- **Entry Points**:
  - `python main_new.py test` - One-time test crawl to test collection
  - `python main_new.py production` - One-time production crawl
  - `python main_new.py schedule` - Automated hourly crawls
- **State Management**: `crawl_state.json` tracks processed article links (max 1000 history)
- **Rate Limiting**: 2-second sleep between articles
- **Environment Reload**: Re-reads `.env` on each crawl for dynamic API key updates

## Critical Workflows

### Development Workflow

```bash
# 1. Setup environment
pip install -r requirements.txt

# 2. Configure credentials
# - Create .env with GEMINI_API_KEY=your_key
# - Place serviceAccountKey.json in project root

# 3. Test analysis (safe)
python main_new.py test

# 4. Check Firebase test collection before production
# 5. Deploy to production
python main_new.py schedule
```

### Testing Strategy

- **Test Scripts**: `test_30_articles.py` - Tests 30 articles with detailed logging
- **Log Files**: All tests create timestamped log files `test_30_articles_YYYYMMDD_HHMMSS.log`
- **Validation**: Manual review of stored articles in Firebase test collection
- **JSON Results**: Test results stored in `test_results_30_*.json` for analysis

## Project-Specific Conventions

### 1. **Sentiment Values** (CRITICAL - Don't confuse!)

- `sentiment = 1`: POSITIVE (store in Firebase)
- `sentiment = 0`: NEUTRAL (store if educational/informative)
- `sentiment = -1`: NEGATIVE (filter out)
- `is_toxic = true`: TOXIC content (filter out regardless of sentiment)

### 2. **Only Store Safe & Positive Articles**

- Filter logic in `main_new.py` line ~164: Only stores if `sentiment >= 0` AND `not is_toxic`
- Both test and production collections follow this rule
- Duplicate check happens in `firebase_handler.py` before storage

### 3. **Caching Strategy**

- In-memory cache in `NewsAnalyzer` (per session)
- Firebase deduplication via MD5 document IDs (persistent)
- `crawl_state.json` for link tracking (prevents re-analysis within 1000 articles)

### 4. **Error Handling Pattern**

```python
try:
    result = analyzer.analyze_and_transform(rss_data)
    if result:  # Can be None if analysis fails
        store_to_firebase(result, collection_name)
except Exception as e:
    logging.error(f"Error: {e}")
    # Mark as processed to avoid infinite retry
    new_processed_links.append(link)
```

### 5. **Vietnamese Content Processing**

- All logs use `ensure_ascii=False` for Vietnamese characters
- Log files use UTF-8 encoding
- Article titles truncated to 50 chars in logs for readability: `title[:50]...`

## Integration Points

### External Dependencies

1. **Google Gemini API**

   - Model: `gemini-2.0-flash-exp`
   - Config: `temperature=0.1`, `max_output_tokens=200`, `top_p=0.8`, `top_k=10`
   - Rate limit: Free tier ~10-15 RPM (handled by 2s delay)
   - Unique capability: Can fetch and read URL content directly

2. **Firebase Firestore**

   - Initialization: `firebase_admin.initialize_app(cred)` in `firebase_handler.py`
   - Single app instance (don't reinitialize)
   - Collections: `positive_news_test`, `positive_news`

3. **VNExpress RSS Feeds**
   - 18 category feeds defined in `main_new.py` (most commented out)
   - Only `tin-moi-nhat` (latest news) enabled by default
   - Feeds return 10-20 articles per fetch

### Data Flow

```
RSS Feed → feedparser.parse() →
  {title, link, summary, image_url, published} →
NewsAnalyzer.analyze_and_transform() →
  [Cache Check] → [Gemini API Call] → [JSON Parse] → [Validate] →
  {category, description, is_toxic, sentiment, ...} →
store_to_firebase() →
  [Duplicate Check] → [Firebase Document Write]
```

## Common Pitfalls & Solutions

### 1. **Gemini API Returns Non-JSON**

- **Cause**: Occasionally returns markdown-wrapped JSON or explanatory text
- **Solution**: `_parse_json_response()` uses regex to extract JSON from markdown blocks
- **Fallback**: If parse fails, returns `None` and article is marked processed

### 2. **Firebase Duplicate Errors**

- **Cause**: MD5 collision or race condition
- **Solution**: `is_article_exists_in_collection()` checks before write
- **Log Pattern**: "Article already exists" (info level, not error)

### 3. **Rate Limit Exceeded**

- **Symptom**: Gemini API 429 errors
- **Solution**: Increase `min_call_interval` in `NewsAnalyzer.__init__()` (default 2.0s)
- **Alternative**: Enable more in-memory cache hits by keeping analyzer instance alive

### 4. **State File Corruption**

- **File**: `crawl_state.json`
- **Recovery**: Delete file (will be recreated with empty state)
- **Impact**: May re-process recent articles (Firebase dedup will catch)

## Key Files for Reference

- **README.md**: User-facing documentation with setup instructions and system overview
- **COMPLETE_IMPLEMENTATION_GUIDE.md**: Deep dive into prompt engineering and Gemini integration
- **IMPROVEMENT_COMPLETION_REPORT.md**: Historical improvements and performance metrics
- **requirements.txt**: Minimal dependencies (6 packages)

## Command Reference

```bash
# Development
python main_new.py test              # Test run (positive_news_test)
python test_30_articles.py           # Detailed test with logging

# Production
python main_new.py production        # Single production run
python main_new.py schedule          # Continuous hourly crawling

# Debugging
tail -f news_crawler.log             # Watch live logs
cat crawl_state.json | jq            # Check crawl state
```

## Code Modification Guidelines

### When Adding New RSS Feeds

1. Add to `RSS_FEEDS` list in `main_new.py`
2. Ensure category name matches Firebase schema expectations
3. Test with single feed first before enabling all

### When Modifying Gemini Prompt

1. Edit `_create_firebase_prompt()` in `news_analyzer.py`
2. Keep JSON response schema stable (8 fields)
3. Test with `test_30_articles.py` before production
4. Monitor token usage (current: ~180 tokens per request)

### When Changing Firebase Schema

1. Update `_transform_to_firebase()` in `news_analyzer.py`
2. Update `store_to_firebase()` validation in `firebase_handler.py`
3. Coordinate schema changes with frontend team
4. Test with new collection first

### When Debugging Analysis Issues

1. Check `news_crawler.log` for Gemini API errors
2. Review test JSON results in `test_results_30_*.json`
3. Manually verify articles in Firebase test collection
4. Look for patterns in filtered-out articles (logs show sentiment + toxic status)

---

**Last Updated**: 2025-10-31  
**Python Version**: 3.8+  
**Primary Contact**: Check `serviceAccountKey.json` for project owner
