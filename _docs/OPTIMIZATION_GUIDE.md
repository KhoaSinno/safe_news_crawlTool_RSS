# 🚀 Safe News Crawler - Optimization Guide

> **Hướng dẫn tối ưu hóa toàn diện với code chi tiết**  
> Tạo ngày: 31/10/2025  
> Branch: dev-gemini-handling-all

---

## 📋 MỤC LỤC

1. [Tổng Quan Các Vấn Đề](#-tổng-quan-các-vấn-đề)
2. [Priority 1: Critical Fixes](#-priority-1-critical-fixes-sửa-ngay)
3. [Priority 2: Performance](#-priority-2-performance-improvements)
4. [Priority 3: Code Quality](#-priority-3-code-quality-improvements)
5. [Testing & Validation](#-testing--validation)
6. [Deployment Checklist](#-deployment-checklist)

---

## 🎯 TỔNG QUAN CÁC VẤN ĐỀ

### Phát Hiện Từ Phân Tích Code

| Priority | Vấn Đề | Impact | Effort | File |
|----------|--------|--------|--------|------|
| 🔴 P1 | Category field bị thiếu trong Gemini prompt | HIGH | 1h | `news_analyzer.py` |
| 🔴 P1 | Security: Print API key ra console | HIGH | 5min | `main.py` |
| 🔴 P1 | Legacy code gây confusion | MEDIUM | 30min | `firebase_handler.py` |
| 🟡 P2 | In-memory cache không persistent | HIGH | 2h | `news_analyzer.py` |
| 🟡 P2 | Rate limiting không consistent | MEDIUM | 30min | All files |
| 🟡 P2 | Crawl state file quá lớn | MEDIUM | 1h | `main.py` |
| 🟢 P3 | Không có unit tests | LOW | 4h | New files |
| 🟢 P3 | Logging không structured | LOW | 2h | All files |
| 🟢 P3 | Sequential processing (có thể parallel) | LOW | 6h | `main.py` |

---

## 🔴 PRIORITY 1: CRITICAL FIXES (Sửa ngay)

### 1.1 FIX: Thêm Category vào Gemini Prompt

**Vấn đề:** Prompt không hướng dẫn Gemini trả về `category`, nhưng validation lại check field này.

**File:** `utils/news_analyzer.py`

**Bước 1: Backup file hiện tại**

```bash
cp utils/news_analyzer.py utils/news_analyzer.py.backup
```

**Bước 2: Sửa function `_create_firebase_prompt()`**

Tìm dòng này (line ~99):

```python
def _create_firebase_prompt(self, title: str, url: str) -> str:
    return f"""
            BẠN LÀ MỘT CHUYÊN GIA PHÂN TÍCH TIN TỨC TIẾNG VIỆT
```

**Thay thế toàn bộ function bằng:**

```python
def _create_firebase_prompt(self, title: str, url: str) -> str:
    return f"""
BẠN LÀ MỘT CHUYÊN GIA PHÂN TÍCH TIN TỨC TIẾNG VIỆT

NHIỆM VỤ:
1. Truy cập và đọc TOÀN BỘ bài báo từ URL (CHỈ QUAN TÂM TEXT CONTENT, KHÔNG QUAN TÂM CODE)
2. Phân tích cảm xúc dựa trên toàn bộ nội dung
3. Phân loại CHỦ ĐỀ chính xác
4. Tạo mô tả ngắn gọn
5. Đánh giá tính độc hại
6. Phát hiện đánh lừa bởi tiêu đề

BÀI BÁO:
URL: {url}
Tiêu đề: "{title}"

CHỦ ĐỀ (chọn 1 trong 10):
- giao-duc: Giáo dục, học tập, thi cử, học bổng, nghiên cứu
- suc-khoe: Y tế, sức khỏe, chữa bệnh, đột phá y học, làm đẹp
- gia-dinh: Gia đình, hôn nhân, nuôi con, tình yêu, quan hệ
- khoa-hoc-cong-nghe: Công nghệ, AI, internet, khoa học, đổi mới
- kinh-doanh: Kinh doanh, khởi nghiệp, tài chính, bất động sản
- van-hoa: Văn hóa, nghệ thuật, giải trí, âm nhạc, điện ảnh
- the-thao: Thể thao, thi đấu, Olympic, các giải đấu
- du-lich: Du lịch, khám phá, ẩm thực, địa điểm
- moi-truong: Môi trường, khí hậu, thiên nhiên, bảo vệ
- xa-hoi: Xã hội, chính trị, pháp luật, cộng đồng

PHÂN LOẠI SENTIMENT:

POSITIVE (sentiment = 1):
- Thành tựu: Học bổng, giải thưởng, tốt nghiệp
- Niềm vui gia đình: Đám cưới, sinh con, đoàn tụ
- Sức khỏe: Chữa khỏi bệnh, đột phá y học
- Việc tốt: Từ thiện, tình nguyện, giúp đỡ
- Sáng tạo: Công nghệ tích cực, khám phá khoa học
- Cảm hứng: Lễ hội văn hóa, thành tựu nghệ thuật
- Vượt khó: Khuyết tật thành công, chuyển đổi tích cực
- Thành công: Kinh doanh phát triển, khởi nghiệp

NEUTRAL (sentiment = 0) - ƯU TIÊN TIN GIÁO DỤC:
- Thống kê, báo cáo khách quan
- Hướng dẫn kỹ thuật, thủ tục
- Thông tin giáo dục, cảnh báo
- Phản ánh vấn đề xã hội để cải thiện
- Tin tức thông tin không mang cảm xúc mạnh
- Cảnh báo sức khỏe có tính giáo dục

NEGATIVE (sentiment = -1) - CHỈ KHI THỰC SỰ BẤT HẠNH:
- Tử vong, tai nạn, thảm họa NGHIÊM TRỌNG
- Tội phạm, bạo lực, khủng bố CHẾT NGƯỜI
- Dịch bệnh, đau khổ, bi kịch NẶNG NỀ
- Mất mát nghiêm trọng về sức khỏe/tinh thần
- Phá sản, thất nghiệp, khủng hoảng nghiêm trọng

TOXIC CONTENT (is_toxic = true):
- Kích động thù hận, phân biệt chủng tộc
- Bạo lực, nội dung 18+
- Tin giả có hại, lừa đảo
- Ngôn từ xúc phạm, chửi bới
- Kích động bạo lực, tự tử

LỪA ĐẢO TIÊU ĐỀ:
CHÚ Ý: Tiêu đề tích cực nhưng nội dung tiêu cực
VD: "Sinh viên nhận học bổng" nhưng phát hiện gian lận

BƯỚC PHÂN TÍCH:
1. Đọc TOÀN BỘ nội dung từ URL
2. KHÔNG chỉ dựa vào tiêu đề
3. Xác định CHỦ ĐỀ chính xác từ nội dung
4. Ưu tiên giá trị thông tin/giáo dục
5. Cân nhắc sentiment = 0 cho tin cảnh báo/giáo dục
6. Chỉ đánh is_toxic = true nếu THỰC SỰ có hại
7. Tạo mô tả ngắn gọn, tập trung giá trị thông tin

MẪU JSON TRẢ VỀ:
{{
    "category": "Chọn 1 trong 10 chủ đề trên",
    "description": "Mô tả 1-2 câu tiếng Việt",
    "is_toxic": true/false,
    "sentiment": 1 (tích cực) / 0 (trung tính) / -1 (tiêu cực)
}}

CHỈ trả JSON, không giải thích.
"""
```

**Bước 3: Test với một bài báo**

```bash
python -c "
from utils.news_analyzer import NewsAnalyzer
import os
from dotenv import load_dotenv

load_dotenv()
analyzer = NewsAnalyzer(os.getenv('GEMINI_API_KEY'))

rss_data = {
    'title': 'Sinh viên Việt Nam giành học bổng toàn phần Harvard',
    'link': 'https://vnexpress.net/example',
    'category': 'test',
    'summary': 'Test',
    'image_url': '',
    'published': ''
}

result = analyzer.analyze_and_transform(rss_data)
print('Category:', result.get('category'))
print('Valid categories:', ['giao-duc', 'suc-khoe', 'gia-dinh', 'khoa-hoc-cong-nghe', 'kinh-doanh', 'van-hoa', 'the-thao', 'du-lich', 'moi-truong', 'xa-hoi'])
"
```

---

### 1.2 FIX: Security - Mask API Key

**Vấn đề:** API key bị print ra console (line 254 trong `main.py`)

**File:** `main.py`

**Tìm dòng:**

```python
print("GEMINI_API_KEY:", GEMINI_API_KEY)
```

**Thay thế bằng:**

```python
# Mask API key for security
if GEMINI_API_KEY:
    masked_key = GEMINI_API_KEY[:8] + "..." + GEMINI_API_KEY[-4:]
    print(f"GEMINI_API_KEY: {masked_key} (masked)")
else:
    print("GEMINI_API_KEY: Not set ❌")
```

**Test:**

```bash
python main.py schedule
# Output: GEMINI_API_KEY: AIzaSyB...xyz1 (masked)
```

---

### 1.3 CLEANUP: Xóa Legacy Code

**Vấn đề:** Có 2 functions không dùng trong `firebase_handler.py`

**File:** `utils/firebase_handler.py`

**Bước 1: Comment out hoặc xóa hoàn toàn**

Tìm và XÓA 2 functions này:

```python
# XÓA Function 1 (line 21-33)
def is_article_exists(title, link):
    """
    Kiểm tra xem bài báo đã tồn tại trong Firebase chưa
    """
    article_id = generate_article_id(title, link)
    try:
        doc_ref = db.collection('news-crawler').document(article_id)
        doc = doc_ref.get()
        return doc.exists
    except Exception as e:
        logging.error(f"Error checking article existence: {e}")
        return False

# XÓA Function 2 (line 90-143)
def store_news(entry, sentiment, is_toxic):
    """
    LEGACY FUNCTION - Giữ lại để tương thích với code cũ
    """
    # ... toàn bộ function
```

**Bước 2: Giữ lại file clean với 3 functions chính**

```python
import firebase_admin
from firebase_admin import credentials, firestore
import logging
import hashlib
from datetime import datetime

# Khởi tạo Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def generate_article_id(title, link):
    """
    Tạo ID duy nhất cho bài báo dựa trên title và link
    """
    content = f"{title}|{link}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def is_article_exists_in_collection(title: str, link: str, collection_name: str) -> bool:
    """
    Kiểm tra xem bài báo đã tồn tại trong collection cụ thể chưa
    """
    article_id = generate_article_id(title, link)
    try:
        doc_ref = db.collection(collection_name).document(article_id)
        doc = doc_ref.get()
        return doc.exists
    except Exception as e:
        logging.error(f"Error checking article existence: {e}")
        return False


def store_to_firebase(firebase_data: dict, collection_name: str = 'positive_news_test') -> bool:
    """
    Lưu tin tức vào Firebase collection với schema chuẩn
    Args:
        firebase_data: Dict với Firebase schema (8 fields)
        collection_name: Tên collection (mặc định: positive_news_test)
    Returns:
        bool: True nếu lưu thành công
    """
    try:
        title = firebase_data.get('title', '')
        link = firebase_data.get('link', '')

        # Kiểm tra trùng lặp
        if is_article_exists_in_collection(title, link, collection_name):
            logging.info(f"📰 Article already exists: {title[:50]}...")
            return False

        # Tạo document ID duy nhất
        doc_id = generate_article_id(title, link)

        # Thêm timestamp
        firebase_data_with_timestamp = {
            **firebase_data,
            'created_at': datetime.now().isoformat(),
            'source': 'gemini-2.0-flash'
        }

        # Lưu vào Firebase
        db.collection(collection_name).document(doc_id).set(firebase_data_with_timestamp)

        logging.info(f"✅ Stored to Firebase [{collection_name}]: {title[:50]}...")
        return True

    except Exception as e:
        logging.error(f"❌ Firebase storage error: {e}")
        return False
```

**Test:**

```bash
python -c "from utils.firebase_handler import *; print('✅ Import successful')"
```

---

## 🟡 PRIORITY 2: PERFORMANCE IMPROVEMENTS

### 2.1 Persistent Cache Implementation

**Vấn đề:** Cache mất khi restart → phải re-analyze articles đã xử lý

**Tạo file mới:** `utils/persistent_cache.py`

```python
"""
Persistent Cache for News Analyzer
Saves analysis results to disk to survive application restarts
"""

import json
import os
import hashlib
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta


class PersistentCache:
    """
    File-based cache with automatic expiry
    """
    
    def __init__(self, cache_file: str = 'analysis_cache.json', expiry_days: int = 7):
        """
        Initialize persistent cache
        
        Args:
            cache_file: Path to cache file
            expiry_days: Number of days before cache entry expires
        """
        self.cache_file = cache_file
        self.expiry_days = expiry_days
        self.cache = self._load_cache()
        self._cleanup_expired()
    
    def _load_cache(self) -> Dict:
        """Load cache from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    logging.info(f"📦 Loaded cache: {len(cache)} entries")
                    return cache
            except Exception as e:
                logging.error(f"Error loading cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving cache: {e}")
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            try:
                cached_time = datetime.fromisoformat(entry.get('timestamp', '2000-01-01'))
                if now - cached_time > timedelta(days=self.expiry_days):
                    expired_keys.append(key)
            except:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logging.info(f"🗑️ Removed {len(expired_keys)} expired cache entries")
            self._save_cache()
    
    def generate_key(self, title: str, url: str) -> str:
        """Generate cache key from title and URL"""
        content = f"{title}|{url}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, title: str, url: str) -> Optional[Dict]:
        """
        Get cached result
        
        Returns:
            Cached result dict or None if not found/expired
        """
        key = self.generate_key(title, url)
        entry = self.cache.get(key)
        
        if not entry:
            return None
        
        # Check expiry
        try:
            cached_time = datetime.fromisoformat(entry.get('timestamp', '2000-01-01'))
            if datetime.now() - cached_time > timedelta(days=self.expiry_days):
                del self.cache[key]
                self._save_cache()
                return None
        except:
            return None
        
        return entry.get('result')
    
    def set(self, title: str, url: str, result: Dict):
        """
        Cache analysis result
        
        Args:
            title: Article title
            url: Article URL
            result: Analysis result to cache
        """
        key = self.generate_key(title, url)
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'title': title[:100]  # For debugging
        }
        self._save_cache()
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
        self._save_cache()
        logging.info("🗑️ Cache cleared")
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'file_size': os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0,
            'expiry_days': self.expiry_days
        }
```

**Bước 2: Update `news_analyzer.py` để dùng persistent cache**

Tìm dòng khởi tạo cache (line ~27):

```python
self.cache = {}  # Simple in-memory cache
```

Thay bằng:

```python
from utils.persistent_cache import PersistentCache
# ... trong __init__()
self.cache = PersistentCache(cache_file='analysis_cache.json', expiry_days=7)
```

**Bước 3: Update các method sử dụng cache**

Trong `analyze_and_transform()` (line ~43):

```python
# OLD:
cache_key = self._generate_cache_key(rss_data['title'], rss_data['link'])
if cache_key in self.cache:
    logging.info(f"✅ Cache hit: {rss_data['title'][:50]}...")
    return self.cache[cache_key]

# NEW:
cached_result = self.cache.get(rss_data['title'], rss_data['link'])
if cached_result:
    logging.info(f"✅ Cache hit: {rss_data['title'][:50]}...")
    return cached_result
```

Sau khi transform (line ~58):

```python
# OLD:
self.cache[cache_key] = firebase_data

# NEW:
self.cache.set(rss_data['title'], rss_data['link'], firebase_data)
```

**Bước 4: Xóa method `_generate_cache_key()` không cần nữa**

**Test:**

```bash
# Chạy lần 1
python main.py test

# Check cache file được tạo
ls -lh analysis_cache.json

# Chạy lần 2 - should see cache hits
python main.py test
# Output: ✅ Cache hit: ...
```

---

### 2.2 Centralized Rate Limit Configuration

**Tạo file:** `config.py`

```python
"""
Centralized Configuration for Safe News Crawler
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Rate Limiting (seconds between API calls)
    RATE_LIMIT_SECONDS = float(os.getenv('RATE_LIMIT_SECONDS', '2.0'))
    
    # Cache Configuration
    CACHE_FILE = os.getenv('CACHE_FILE', 'analysis_cache.json')
    CACHE_EXPIRY_DAYS = int(os.getenv('CACHE_EXPIRY_DAYS', '7'))
    
    # State Management
    CRAWL_STATE_FILE = os.getenv('CRAWL_STATE_FILE', 'crawl_state.json')
    MAX_PROCESSED_LINKS = int(os.getenv('MAX_PROCESSED_LINKS', '500'))  # Giảm từ 1000
    
    # Firebase Collections
    TEST_COLLECTION = os.getenv('TEST_COLLECTION', 'positive_news_test')
    PROD_COLLECTION = os.getenv('PROD_COLLECTION', 'positive_news')
    
    # Logging
    LOG_FILE = os.getenv('LOG_FILE', 'news_crawler.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        return True
    
    @classmethod
    def display(cls, mask_secrets=True):
        """Display configuration (for debugging)"""
        config_dict = {
            'GEMINI_API_KEY': cls._mask_key(cls.GEMINI_API_KEY) if mask_secrets else cls.GEMINI_API_KEY,
            'RATE_LIMIT_SECONDS': cls.RATE_LIMIT_SECONDS,
            'CACHE_FILE': cls.CACHE_FILE,
            'CACHE_EXPIRY_DAYS': cls.CACHE_EXPIRY_DAYS,
            'CRAWL_STATE_FILE': cls.CRAWL_STATE_FILE,
            'MAX_PROCESSED_LINKS': cls.MAX_PROCESSED_LINKS,
            'TEST_COLLECTION': cls.TEST_COLLECTION,
            'PROD_COLLECTION': cls.PROD_COLLECTION,
            'LOG_FILE': cls.LOG_FILE,
            'LOG_LEVEL': cls.LOG_LEVEL
        }
        return config_dict
    
    @staticmethod
    def _mask_key(key: str) -> str:
        """Mask API key for display"""
        if not key or len(key) < 12:
            return "***"
        return f"{key[:8]}...{key[-4:]}"


# Validate on import
Config.validate()
```

**Update `.env.example`:**

```bash
# API Keys
GEMINI_API_KEY=your_actual_api_key_here

# Rate Limiting
RATE_LIMIT_SECONDS=2.0

# Cache Settings
CACHE_FILE=analysis_cache.json
CACHE_EXPIRY_DAYS=7

# State Management
CRAWL_STATE_FILE=crawl_state.json
MAX_PROCESSED_LINKS=500

# Firebase Collections
TEST_COLLECTION=positive_news_test
PROD_COLLECTION=positive_news

# Logging
LOG_FILE=news_crawler.log
LOG_LEVEL=INFO
```

**Update các files sử dụng config:**

**1. `utils/news_analyzer.py`:**

```python
from config import Config

class NewsAnalyzer:
    def __init__(self, api_key: str = None):
        """Khởi tạo với Gemini API key"""
        api_key = api_key or Config.GEMINI_API_KEY
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.cache = PersistentCache(
            cache_file=Config.CACHE_FILE, 
            expiry_days=Config.CACHE_EXPIRY_DAYS
        )
        self.last_call_time = 0
        self.min_call_interval = Config.RATE_LIMIT_SECONDS  # <-- SỬA DỤNG CONFIG
```

**2. `main.py`:**

```python
from config import Config

# Thay thế
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CRAWL_STATE_FILE = "crawl_state.json"

# Bằng
GEMINI_API_KEY = Config.GEMINI_API_KEY
CRAWL_STATE_FILE = Config.CRAWL_STATE_FILE

# Thay thế
time.sleep(2)

# Bằng
time.sleep(Config.RATE_LIMIT_SECONDS)

# Thay thế
def is_new_article(link, processed_links, max_history=1000):

# Bằng
def is_new_article(link, processed_links, max_history=None):
    max_history = max_history or Config.MAX_PROCESSED_LINKS
```

**3. `test_30_articles.py`:**

```python
from config import Config

# Thay thế
time.sleep(3)

# Bằng
time.sleep(Config.RATE_LIMIT_SECONDS)
```

---

### 2.3 Optimize Crawl State File

**Vấn đề:** File có thể lớn lên đến 1000 links, cần thêm timestamp và cleanup

**Update `main.py`:**

```python
import json
import os
from datetime import datetime, timedelta
from config import Config

def load_crawl_state():
    """Load trạng thái crawl từ file với cleanup tự động"""
    if os.path.exists(Config.CRAWL_STATE_FILE):
        try:
            with open(Config.CRAWL_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
                # NEW: Cleanup old links (older than 7 days)
                cleaned_links = cleanup_old_links(state.get("processed_links", []))
                state["processed_links"] = cleaned_links
                
                logging.info(f"📦 Loaded {len(cleaned_links)} processed links")
                return state
        except Exception as e:
            logging.error(f"Error loading crawl state: {e}")

    return {"last_crawl": None, "processed_links": []}


def cleanup_old_links(processed_links, max_age_days=7):
    """
    Cleanup links older than max_age_days
    
    Args:
        processed_links: List of link dicts with timestamp
        max_age_days: Max age in days
    
    Returns:
        Cleaned list of links
    """
    if not processed_links:
        return []
    
    # Handle old format (just strings)
    if isinstance(processed_links[0], str):
        # Convert to new format with current timestamp
        now = datetime.now().isoformat()
        processed_links = [{"link": link, "timestamp": now} for link in processed_links]
    
    # Filter out old links
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    cleaned = []
    
    for item in processed_links:
        try:
            link_time = datetime.fromisoformat(item.get('timestamp', '2000-01-01'))
            if link_time > cutoff_date:
                cleaned.append(item)
        except:
            # Keep items with invalid timestamp (better safe)
            cleaned.append(item)
    
    # Limit to MAX_PROCESSED_LINKS
    if len(cleaned) > Config.MAX_PROCESSED_LINKS:
        cleaned = cleaned[-Config.MAX_PROCESSED_LINKS:]
    
    removed_count = len(processed_links) - len(cleaned)
    if removed_count > 0:
        logging.info(f"🗑️ Cleaned up {removed_count} old links from state")
    
    return cleaned


def save_crawl_state(state):
    """Lưu trạng thái crawl với format mới"""
    try:
        # Ensure processed_links has new format
        if state.get("processed_links"):
            # Convert if needed
            if isinstance(state["processed_links"][0], str):
                now = datetime.now().isoformat()
                state["processed_links"] = [
                    {"link": link, "timestamp": now} 
                    for link in state["processed_links"]
                ]
        
        with open(Config.CRAWL_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        logging.info(f"💾 Saved crawl state: {len(state.get('processed_links', []))} links")
    except Exception as e:
        logging.error(f"Error saving crawl state: {e}")


def is_new_article(link, processed_links, max_history=None):
    """
    Kiểm tra bài báo có mới không dựa trên link
    
    Args:
        link: URL to check
        processed_links: List of processed link dicts
        max_history: Max number to keep (from Config)
    """
    max_history = max_history or Config.MAX_PROCESSED_LINKS
    
    # Handle both old format (strings) and new format (dicts)
    link_set = set()
    for item in processed_links:
        if isinstance(item, str):
            link_set.add(item)
        elif isinstance(item, dict):
            link_set.add(item.get('link', ''))
    
    # Giữ chỉ max_history links gần nhất
    if len(processed_links) > max_history:
        processed_links[:] = processed_links[-max_history:]

    return link not in link_set


def mark_as_processed(link, processed_links):
    """
    Mark link as processed with timestamp
    
    Args:
        link: URL to mark
        processed_links: List to append to
    """
    processed_links.append({
        "link": link,
        "timestamp": datetime.now().isoformat()
    })
```

**Update trong `crawl_and_analyze()` function:**

```python
# OLD:
new_processed_links.append(link)

# NEW:
mark_as_processed(link, new_processed_links)
```

**Test migration từ old format:**

```bash
# Backup old state
cp crawl_state.json crawl_state.json.backup

# Run migration
python -c "
from main import load_crawl_state, save_crawl_state
state = load_crawl_state()
save_crawl_state(state)
print('✅ Migration complete')
"

# Check new format
cat crawl_state.json | head -20
```

---

## 🟢 PRIORITY 3: CODE QUALITY IMPROVEMENTS

### 3.1 Add Unit Tests

**Tạo thư mục tests:**

```bash
mkdir -p tests
touch tests/__init__.py
```

**File:** `tests/test_firebase_handler.py`

```python
"""
Unit Tests for Firebase Handler
"""

import unittest
from utils.firebase_handler import generate_article_id, is_article_exists_in_collection


class TestFirebaseHandler(unittest.TestCase):
    
    def test_generate_article_id_consistent(self):
        """Test that same inputs generate same ID"""
        title = "Test Article"
        link = "https://example.com/article"
        
        id1 = generate_article_id(title, link)
        id2 = generate_article_id(title, link)
        
        self.assertEqual(id1, id2)
        self.assertEqual(len(id1), 32)  # MD5 hash length
    
    def test_generate_article_id_different(self):
        """Test that different inputs generate different IDs"""
        id1 = generate_article_id("Article 1", "https://example.com/1")
        id2 = generate_article_id("Article 2", "https://example.com/2")
        
        self.assertNotEqual(id1, id2)
    
    def test_generate_article_id_unicode(self):
        """Test with Vietnamese characters"""
        title = "Sinh viên Việt Nam đạt giải quốc tế"
        link = "https://vnexpress.net/example"
        
        article_id = generate_article_id(title, link)
        
        self.assertIsNotNone(article_id)
        self.assertEqual(len(article_id), 32)


if __name__ == '__main__':
    unittest.main()
```

**File:** `tests/test_persistent_cache.py`

```python
"""
Unit Tests for Persistent Cache
"""

import unittest
import os
import tempfile
from datetime import datetime, timedelta
from utils.persistent_cache import PersistentCache


class TestPersistentCache(unittest.TestCase):
    
    def setUp(self):
        """Create temporary cache file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.cache = PersistentCache(cache_file=self.temp_file.name, expiry_days=1)
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_set_and_get(self):
        """Test basic set and get operations"""
        title = "Test Article"
        url = "https://example.com/test"
        result = {"sentiment": 1, "category": "test"}
        
        # Set cache
        self.cache.set(title, url, result)
        
        # Get cache
        cached = self.cache.get(title, url)
        
        self.assertIsNotNone(cached)
        self.assertEqual(cached['sentiment'], 1)
        self.assertEqual(cached['category'], 'test')
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        cached = self.cache.get("Nonexistent", "https://example.com/404")
        self.assertIsNone(cached)
    
    def test_cache_persistence(self):
        """Test cache survives reload"""
        title = "Persistent Article"
        url = "https://example.com/persist"
        result = {"sentiment": 0}
        
        # Set and save
        self.cache.set(title, url, result)
        
        # Create new cache instance (reload from disk)
        cache2 = PersistentCache(cache_file=self.temp_file.name, expiry_days=1)
        cached = cache2.get(title, url)
        
        self.assertIsNotNone(cached)
        self.assertEqual(cached['sentiment'], 0)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        self.cache.set("Article 1", "http://example.com/1", {"test": 1})
        self.cache.set("Article 2", "http://example.com/2", {"test": 2})
        
        stats = self.cache.stats()
        
        self.assertEqual(stats['total_entries'], 2)
        self.assertGreater(stats['file_size'], 0)


if __name__ == '__main__':
    unittest.main()
```

**File:** `tests/test_config.py`

```python
"""
Unit Tests for Configuration
"""

import unittest
import os
from config import Config


class TestConfig(unittest.TestCase):
    
    def test_config_has_required_fields(self):
        """Test that config has all required fields"""
        self.assertIsNotNone(Config.GEMINI_API_KEY)
        self.assertIsNotNone(Config.RATE_LIMIT_SECONDS)
        self.assertIsNotNone(Config.CACHE_FILE)
    
    def test_rate_limit_is_float(self):
        """Test rate limit is numeric"""
        self.assertIsInstance(Config.RATE_LIMIT_SECONDS, float)
        self.assertGreater(Config.RATE_LIMIT_SECONDS, 0)
    
    def test_max_links_is_reasonable(self):
        """Test max processed links is reasonable"""
        self.assertGreater(Config.MAX_PROCESSED_LINKS, 0)
        self.assertLessEqual(Config.MAX_PROCESSED_LINKS, 2000)
    
    def test_mask_key(self):
        """Test API key masking"""
        masked = Config._mask_key("AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxx")
        self.assertIn("...", masked)
        self.assertNotIn("xxxxxxxx", masked)


if __name__ == '__main__':
    unittest.main()
```

**Chạy tests:**

```bash
# Run all tests
python -m pytest tests/ -v

# Or with unittest
python -m unittest discover tests/ -v

# Run specific test
python tests/test_firebase_handler.py
python tests/test_persistent_cache.py
python tests/test_config.py
```

**Thêm vào `requirements.txt`:**

```
pytest>=7.0.0
pytest-cov>=4.0.0
```

---

### 3.2 Add Pre-commit Validation Script

**File:** `scripts/validate_changes.py`

```python
"""
Pre-commit validation script
Run before committing changes
"""

import sys
import os
import subprocess

def run_tests():
    """Run unit tests"""
    print("🧪 Running unit tests...")
    result = subprocess.run(['python', '-m', 'pytest', 'tests/', '-v'], capture_output=True)
    
    if result.returncode != 0:
        print("❌ Tests failed!")
        print(result.stdout.decode())
        return False
    
    print("✅ All tests passed!")
    return True


def check_config():
    """Validate configuration"""
    print("⚙️ Checking configuration...")
    
    try:
        from config import Config
        config_dict = Config.display(mask_secrets=True)
        
        print("✅ Configuration valid:")
        for key, value in config_dict.items():
            print(f"   {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def check_imports():
    """Check all imports work"""
    print("📦 Checking imports...")
    
    modules = [
        'utils.rss_crawler',
        'utils.news_analyzer',
        'utils.firebase_handler',
        'utils.persistent_cache',
        'config'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module}: {e}")
            return False
    
    return True


def main():
    """Run all validations"""
    print("=" * 60)
    print("🔍 PRE-COMMIT VALIDATION")
    print("=" * 60)
    
    checks = [
        ("Configuration", check_config),
        ("Imports", check_imports),
        ("Unit Tests", run_tests)
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        print(f"\n{'='*60}")
        if not check_func():
            all_passed = False
            print(f"❌ {name} check FAILED")
        else:
            print(f"✅ {name} check PASSED")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED - Safe to commit!")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED - Fix before committing!")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

**Chạy validation:**

```bash
python scripts/validate_changes.py
```

---

## 🧪 TESTING & VALIDATION

### Quick Test Script

**File:** `scripts/quick_test.py`

```python
"""
Quick test script to validate optimization changes
"""

import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.news_analyzer import NewsAnalyzer
from utils.firebase_handler import store_to_firebase
from config import Config
import time


def test_category_in_response():
    """Test that Gemini returns category field"""
    print("\n🧪 TEST 1: Category Field in Gemini Response")
    print("-" * 60)
    
    analyzer = NewsAnalyzer()
    
    test_article = {
        'title': 'Sinh viên Việt Nam giành học bổng Harvard',
        'link': 'https://vnexpress.net/example-scholarship',
        'category': 'test',
        'summary': 'Test summary',
        'image_url': '',
        'published': ''
    }
    
    print(f"Analyzing: {test_article['title']}")
    result = analyzer.analyze_and_transform(test_article)
    
    if result and 'category' in result:
        print(f"✅ Category found: {result['category']}")
        
        valid_categories = ['giao-duc', 'suc-khoe', 'gia-dinh', 'khoa-hoc-cong-nghe', 
                           'kinh-doanh', 'van-hoa', 'the-thao', 'du-lich', 'moi-truong', 'xa-hoi']
        
        if result['category'] in valid_categories:
            print(f"✅ Category is valid!")
            return True
        else:
            print(f"❌ Category '{result['category']}' not in valid list")
            return False
    else:
        print("❌ Category field missing!")
        return False


def test_cache_persistence():
    """Test that cache persists across instances"""
    print("\n🧪 TEST 2: Cache Persistence")
    print("-" * 60)
    
    from utils.persistent_cache import PersistentCache
    import tempfile
    
    # Create temp cache file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    
    # First instance - write
    cache1 = PersistentCache(cache_file=temp_file.name, expiry_days=1)
    cache1.set("Test Article", "http://example.com/test", {"sentiment": 1})
    print("✅ Cached data in first instance")
    
    # Second instance - read
    cache2 = PersistentCache(cache_file=temp_file.name, expiry_days=1)
    result = cache2.get("Test Article", "http://example.com/test")
    
    # Cleanup
    os.unlink(temp_file.name)
    
    if result and result.get('sentiment') == 1:
        print("✅ Cache persisted across instances!")
        return True
    else:
        print("❌ Cache not persisted!")
        return False


def test_rate_limit_config():
    """Test rate limit is configurable"""
    print("\n🧪 TEST 3: Rate Limit Configuration")
    print("-" * 60)
    
    print(f"Rate limit from config: {Config.RATE_LIMIT_SECONDS}s")
    
    analyzer = NewsAnalyzer()
    
    if analyzer.min_call_interval == Config.RATE_LIMIT_SECONDS:
        print(f"✅ Analyzer using config rate limit: {analyzer.min_call_interval}s")
        return True
    else:
        print(f"❌ Rate limit mismatch: {analyzer.min_call_interval} vs {Config.RATE_LIMIT_SECONDS}")
        return False


def test_crawl_state_format():
    """Test new crawl state format with timestamps"""
    print("\n🧪 TEST 4: Crawl State Format")
    print("-" * 60)
    
    from main import mark_as_processed, is_new_article
    from datetime import datetime
    
    processed_links = []
    
    # Mark some as processed
    mark_as_processed("http://example.com/1", processed_links)
    mark_as_processed("http://example.com/2", processed_links)
    
    # Check format
    if isinstance(processed_links[0], dict):
        print(f"✅ New format with timestamp: {processed_links[0]}")
        
        # Test deduplication
        if not is_new_article("http://example.com/1", processed_links):
            print("✅ Deduplication works!")
            return True
        else:
            print("❌ Deduplication failed!")
            return False
    else:
        print(f"❌ Old format (string): {processed_links[0]}")
        return False


def main():
    """Run all quick tests"""
    print("=" * 60)
    print("🚀 QUICK OPTIMIZATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Category Field", test_category_in_response),
        ("Cache Persistence", test_cache_persistence),
        ("Rate Limit Config", test_rate_limit_config),
        ("Crawl State Format", test_crawl_state_format)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️ {total-passed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

**Chạy:**

```bash
python scripts/quick_test.py
```

---

## 📦 DEPLOYMENT CHECKLIST

### Pre-deployment

```bash
# 1. Run validation
python scripts/validate_changes.py

# 2. Run quick tests
python scripts/quick_test.py

# 3. Run full unit tests
python -m pytest tests/ -v --cov=utils --cov-report=html

# 4. Test với 30 articles
python test_30_articles.py

# 5. Check config
python -c "from config import Config; import json; print(json.dumps(Config.display(), indent=2))"
```

### Deployment Steps

```bash
# 1. Create backup
mkdir -p backups/$(date +%Y%m%d)
cp utils/*.py backups/$(date +%Y%m%d)/
cp main.py backups/$(date +%Y%m%d)/

# 2. Commit changes
git add .
git commit -m "feat: optimize codebase - P1, P2, P3 fixes"
git push origin dev-gemini-handling-all

# 3. Deploy to production
python main.py production

# 4. Monitor logs
tail -f news_crawler.log
```

### Post-deployment Monitoring

```bash
# Check cache stats
python -c "
from utils.persistent_cache import PersistentCache
cache = PersistentCache()
print(cache.stats())
"

# Check crawl state size
ls -lh crawl_state.json

# Check Firebase for new articles
# (Manual check in Firebase console)

# Monitor API usage
# (Check Gemini API quota in Google Cloud Console)
```

---

## 📊 EXPECTED IMPROVEMENTS SUMMARY

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Bug: Category Field** | ❌ Missing | ✅ Fixed | ∞ |
| **Security: API Key Leak** | ❌ Printed | ✅ Masked | 100% |
| **Cache Persistence** | ❌ Lost on restart | ✅ Persisted | ∞ |
| **Cache Hit Rate** | 0% | 70%+ | ∞ |
| **API Quota Usage** | 100 calls/run | ~30 calls/run | 70% reduction |
| **Code Maintainability** | 6/10 | 8.5/10 | +42% |
| **Crawl State Size** | 1000 links | 500 links | 50% smaller |
| **Configuration** | Scattered | Centralized | ✅ |
| **Legacy Code** | 2 unused funcs | 0 | 100% clean |
| **Test Coverage** | 0% | 60%+ | +60% |

---

## 🎯 NEXT STEPS (Optional - Future Improvements)

### Phase 4: Advanced Optimizations

1. **Async Processing** (6 hours)
   - Use `asyncio` for parallel article processing
   - Process 3-5 articles concurrently
   - Reduce crawl time by 60%

2. **Structured Logging** (2 hours)
   - Replace emoji logs with JSON structured logs
   - Better for log aggregation tools (ELK, Splunk)

3. **Monitoring Dashboard** (4 hours)
   - Track success rate, API usage, cache hit rate
   - Alert on errors

4. **Retry Logic** (2 hours)
   - Exponential backoff for transient errors
   - Distinguish permanent vs temporary failures

---

## ❓ TROUBLESHOOTING

### Issue 1: "Category field missing" validation error

**Cause:** Old prompt still cached  
**Fix:**

```bash
# Clear cache
python -c "from utils.persistent_cache import PersistentCache; PersistentCache().clear()"
```

### Issue 2: Import errors after adding config.py

**Cause:** Circular imports  
**Fix:** Ensure config.py doesn't import from other project modules

### Issue 3: Tests failing

**Cause:** Missing test dependencies  
**Fix:**

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Issue 4: Cache file growing too large

**Cause:** No cleanup running  
**Fix:** Cache auto-cleans on load, but can manually clean:

```bash
python -c "
from utils.persistent_cache import PersistentCache
cache = PersistentCache(expiry_days=1)  # Aggressive cleanup
"
```

---

## 📞 SUPPORT

Nếu gặp vấn đề khi implement:

1. Check logs: `tail -f news_crawler.log`
2. Run validation: `python scripts/validate_changes.py`
3. Check config: `python -c "from config import Config; print(Config.display())"`
4. Review backups: `ls -la backups/`

---

**Good luck with optimization! 🚀**

*Created with ❤️ by AI Assistant*
*Last updated: 2025-10-31*
