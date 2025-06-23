# 🚀 Báo cáo Giải pháp Tối ưu hóa News Filter

## 📋 Vấn đề hiện tại

Hệ thống hiện tại sử dụng **local models** để phân tích cảm xúc và độc tính:

- 🤖 `wonrax/phobert-base-vietnamese-sentiment` (Phân tích cảm xúc)
- 🛡️ `naot97/vietnamese-toxicity-detection_1` (Phát hiện độc tính)

### ⚠️ Nhược điểm của local models

- **Tiêu tốn tài nguyên**: Mỗi lần crawl máy chạy rất nặng
- **Tốc độ chậm**: Phải load models vào memory và xử lý
- **Dung lượng lớn**: Models có kích thước hàng trăm MB
- **RAM cao**: Yêu cầu nhiều RAM để load models

---

## 🎯 Các giải pháp tối ưu

### 1. 🌟 **Gemini API (KHUYẾN NGHỊ)**

#### ✅ Ưu điểm

- **Miễn phí**: Free tier hào phóng (1500 requests/day)
- **Hiệu suất cao**: Xử lý nhanh, không tốn tài nguyên máy
- **Độ chính xác**: AI model mạnh mẽ của Google
- **Hỗ trợ tiếng Việt**: Hiểu ngữ cảnh tiếng Việt tốt
- **Không cần tải models**: Chỉ cần API key

#### 📊 Free Tier Gemini API

- **1,500 requests/ngày** (đủ cho crawl mỗi giờ = ~24 requests/ngày)
- **32K tokens/request** (đủ xử lý bài viết dài)
- **Không cần thẻ tín dụng** để đăng ký

#### 💡 Cách triển khai

```python
# pip install google-generativeai
import google.generativeai as genai

genai.configure(api_key='YOUR_GEMINI_API_KEY')
model = genai.GenerativeModel('gemini-pro')

def analyze_with_gemini(text):
    prompt = f"""
    Phân tích bài viết tin tức tiếng Việt sau và trả về kết quả JSON:
    
    Văn bản: "{text}"
    
    Yêu cầu phân tích:
    1. Cảm xúc: POSITIVE (tích cực), NEGATIVE (tiêu cực), NEUTRAL (trung tính)
    2. Độc tính: true (có độc hại), false (không độc hại)
    3. Điểm tin cậy: 0.0-1.0
    
    Chỉ trả về JSON format:
    {{"sentiment": "...", "toxicity": boolean, "confidence": float}}
    """
    
    response = model.generate_content(prompt)
    return response.text
```

### 2. 🔄 **Caching & Optimization**

#### Model Caching (Giải pháp trung gian)

```python
# Load models một lần khi khởi động
class ModelCache:
    _instance = None
    _models_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_models(self):
        if not self._models_loaded:
            # Load models chỉ một lần
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(...)
            self.toxicity_model = AutoModelForSequenceClassification.from_pretrained(...)
            self._models_loaded = True
```

### 3. 🌐 **Các API miễn phí khác**

#### a) **Hugging Face Inference API**

- Free tier: 30,000 requests/tháng
- Sử dụng trực tiếp models đã train

#### b) **Cohere API**

- Free tier: 1000 requests/tháng
- Hỗ trợ sentiment analysis

#### c) **Perspective API (Google)**

- Miễn phí cho non-commercial
- Chuyên về toxicity detection

---

## 📈 So sánh chi tiết

| Giải pháp | Chi phí | Tốc độ | Tài nguyên máy | Độ chính xác | Giới hạn |
|-----------|---------|--------|----------------|--------------|----------|
| **Local Models** | Miễn phí | Chậm | Rất cao | Tốt | Không |
| **Gemini API** | Miễn phí | Rất nhanh | Rất thấp | Rất tốt | 1500/ngày |
| **HuggingFace API** | Miễn phí | Nhanh | Thấp | Tốt | 30K/tháng |
| **OpenAI API** | Trả phí | Rất nhanh | Rất thấp | Xuất sắc | Theo usage |

---

## 🎯 Giải pháp được khuyến nghị

### **Phương án A: Gemini API (Tối ưu nhất)**

**Lý do chọn:**

- ✅ Hoàn toàn miễn phí cho use case của bạn
- ✅ Hiệu suất cao, không tốn tài nguyên máy
- ✅ Độ chính xác cao với tiếng Việt
- ✅ Dễ implement và maintain

**Implementation:**

1. Đăng ký Gemini API key tại [Google AI Studio](https://makersuite.google.com/)
2. Thay thế `news_filter.py` bằng Gemini API calls
3. Implement retry logic và error handling
4. Cache kết quả để tránh duplicate requests

### **Phương án B: Hybrid (Backup plan)**

Kết hợp Gemini API + Local models:

- Dùng Gemini API làm primary
- Fallback về local models khi hết quota
- Caching thông minh để tối ưu requests

---

## 📝 Hướng dẫn implement Gemini API

### Bước 1: Cài đặt thư viện

```bash
pip install google-generativeai
```

### Bước 2: Tạo file `gemini_filter.py`

```python
import google.generativeai as genai
import requests
import json
import time
import hashlib
import sqlite3
from typing import Dict, Optional
import os

class GeminiNewsFilter:
    def __init__(self, api_key: str):
        # Cấu hình API key cho Gemini 2.0 Flash
        self.api_key = api_key
        self.model_name = "gemini-2.0-flash"
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        self.request_count = 0
        self.daily_limit = 1500  # Free tier limit
        
        # Khởi tạo cache
        self.cache = ResultCache()
        
        # Configure với google-generativeai library (backup method)
        genai.configure(api_key=api_key)
        self.backup_model = genai.GenerativeModel('gemini-pro')
    
    def analyze_news_direct_api(self, title: str, content: str) -> Dict:
        """
        Sử dụng Direct REST API với Gemini 2.0 Flash
        """
        if self.request_count >= self.daily_limit:
            raise Exception("Đã đạt giới hạn daily limit của Gemini API")
        
        # Giới hạn độ dài text để tối ưu token usage
        text = f"{title}. {content}"[:2000]
        
        # Tạo prompt tối ưu cho việc phân tích tin tức
        prompt = f"""
Phân tích bài viết tin tức tiếng Việt sau và trả về CHÍNH XÁC JSON format:

Tiêu đề: {title}
Nội dung: {content[:1500]}

Yêu cầu phân tích:
1. Cảm xúc (sentiment):
   - POSITIVE: tin vui, thành công, hạnh phúc, đoàn tụ, kết hôn, sinh con, thăng tiến
   - NEGATIVE: tai nạn, tử vong, bệnh tật, ly hôn, mất việc, thảm họa, tham nhũng  
   - NEUTRAL: thông tin bình thường, thời tiết, lịch trình, thông báo

2. Độc tính (toxicity):
   - true: bạo lực, căm thù, phân biệt chủng tộc, ngôn từ thô tục
   - false: nội dung bình thường

3. Điểm tin cậy (confidence): 0.0-1.0

Chỉ trả về JSON format này, không thêm text khác:
{{"sentiment": "POSITIVE", "toxicity": false, "confidence": 0.95}}
"""
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,  # Giảm randomness để có kết quả ổn định
                "maxOutputTokens": 100,  # Giới hạn output cho JSON
                "topP": 0.8,
                "topK": 10
            }
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            self.request_count += 1
            
            if response.status_code == 200:
                result = response.json()
                content_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON từ response
                try:
                    # Loại bỏ markdown formatting nếu có
                    if content_text.startswith('```json'):
                        content_text = content_text.replace('```json', '').replace('```', '').strip()
                    
                    parsed_result = json.loads(content_text)
                    
                    # Validate kết quả
                    if self._validate_result(parsed_result):
                        return parsed_result
                    else:
                        return self._get_fallback_result()
                        
                except json.JSONDecodeError as e:
                    print(f"JSON Parse Error: {e}, Response: {content_text}")
                    return self._get_fallback_result()
            else:
                print(f"API Error: {response.status_code}, {response.text}")
                return self._get_fallback_result()
                
        except Exception as e:
            print(f"Gemini API Direct call error: {e}")
            return self._get_fallback_result()
    
    def analyze_news(self, title: str, content: str) -> Dict:
        """
        Phân tích tin tức với caching và fallback
        """
        # Tạo cache key
        text = f"{title}. {content}"
        cached_result = self.cache.get_cached_result(text)
        if cached_result:
            return {
                "sentiment": cached_result[0], 
                "toxicity": bool(cached_result[1]), 
                "confidence": cached_result[2]
            }
        
        # Thử API trực tiếp trước
        try:
            result = self.analyze_news_direct_api(title, content)
            self.cache.cache_result(text, result)
            return result
        except Exception as e:
            print(f"Direct API failed: {e}, trying backup...")
            # Fallback với google-generativeai library
            return self._analyze_with_backup(title, content)
    
    def _analyze_with_backup(self, title: str, content: str) -> Dict:
        """
        Backup method sử dụng google-generativeai library
        """
        try:
            text = f"{title}. {content}"[:2000]
            prompt = f"""
Phân tích cảm xúc bài báo tiếng Việt: "{text}"

Trả về JSON:
{{"sentiment": "POSITIVE/NEGATIVE/NEUTRAL", "toxicity": false, "confidence": 0.8}}
            """
            
            response = self.backup_model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            parsed = json.loads(result_text)
            return parsed if self._validate_result(parsed) else self._get_fallback_result()
            
        except Exception as e:
            print(f"Backup method failed: {e}")
            return self._rule_based_analysis(title, content)
    
    def _validate_result(self, result: Dict) -> bool:
        """
        Validate kết quả từ API
        """
        required_keys = ['sentiment', 'toxicity', 'confidence']
        if not all(key in result for key in required_keys):
            return False
        
        if result['sentiment'] not in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']:
            return False
        
        if not isinstance(result['toxicity'], bool):
            return False
            
        if not (0.0 <= result['confidence'] <= 1.0):
            return False
            
        return True
    
    def _get_fallback_result(self) -> Dict:
        """
        Kết quả mặc định khi API fail
        """
        return {"sentiment": "NEUTRAL", "toxicity": False, "confidence": 0.5}
    
    def _rule_based_analysis(self, title: str, content: str) -> Dict:
        """
        Phân tích dựa trên từ khóa khi tất cả API fail
        """
        text = f"{title} {content}".lower()
        
        # Từ khóa tiêu cực
        negative_keywords = [
            "tai nạn", "chết", "tử vong", "qua đời", "thiệt mạng",
            "bệnh", "ung thư", "covid", "dịch bệnh",
            "ly hôn", "chia tay", "tan vỡ", "khủng hoảng",
            "tham nhũng", "tội phạm", "trộm cắp", "cướp",
            "thảm họa", "lũ lụt", "động đất", "cháy nổ",
            "mất việc", "phá sản", "kinh tế khó khăn"
        ]
        
        # Từ khóa tích cực
        positive_keywords = [
            "thành công", "chiến thắng", "đạt được", "hoàn thành",
            "hạnh phúc", "vui mừng", "kỷ niệm", "lễ hội",
            "cưới", "đám cưới", "sinh con", "chào đời",
            "thăng tiến", "tăng lương", "được tặng", "nhận giải",
            "đoàn tụ", "sum họp", "hòa giải", "yêu thương",
            "phát triển", "tăng trưởng", "cải thiện", "tốt lên"
        ]
        
        negative_count = sum(1 for word in negative_keywords if word in text)
        positive_count = sum(1 for word in positive_keywords if word in text)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            confidence = min(0.8, 0.5 + positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment = "NEGATIVE" 
            confidence = min(0.8, 0.5 + negative_count * 0.1)
        else:
            sentiment = "NEUTRAL"
            confidence = 0.6
        
        return {
            "sentiment": sentiment,
            "toxicity": False,  # Rule-based không detect toxicity
            "confidence": confidence
        }
    
    def is_positive_news(self, title: str, content: str) -> bool:
        """
        Kiểm tra tin tức có tích cực không
        """
        result = self.analyze_news(title, content)
        return (
            result["sentiment"] == "POSITIVE" and 
            not result["toxicity"] and 
            result["confidence"] > 0.6
        )
    
    def get_stats(self) -> Dict:
        """
        Thống kê sử dụng API
        """
        return {
            "requests_used": self.request_count,
            "requests_remaining": self.daily_limit - self.request_count,
            "usage_percentage": (self.request_count / self.daily_limit) * 100
        }


class ResultCache:
    """
    Cache kết quả phân tích để tránh duplicate API calls
    """
    def __init__(self, db_path="analysis_cache.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()
    
    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                content_hash TEXT PRIMARY KEY,
                sentiment TEXT,
                toxicity BOOLEAN,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def get_cached_result(self, text: str) -> Optional[tuple]:
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cursor = self.conn.execute(
            "SELECT sentiment, toxicity, confidence FROM analysis_cache WHERE content_hash = ?",
            (text_hash,)
        )
        return cursor.fetchone()
    
    def cache_result(self, text: str, result: Dict):
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        self.conn.execute(
            "INSERT OR REPLACE INTO analysis_cache VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (text_hash, result['sentiment'], result['toxicity'], result['confidence'])
        )
        self.conn.commit()


# Test function
def test_gemini_filter():
    """
    Test function để kiểm tra Gemini API
    """
    api_key = "AIzaSyCZbOdmDcqzmzJceMKWCznm-mlp8HBrsbk"
    filter_obj = GeminiNewsFilter(api_key)
    
    # Test cases
    test_cases = [
        {
            "title": "Cặp đôi kết hôn sau 10 năm yêu nhau",
            "content": "Sau 10 năm gắn bó, cặp đôi đã quyết định tổ chức đám cưới trong niềm hạnh phúc của gia đình hai bên."
        },
        {
            "title": "Tai nạn giao thông nghiêm trọng",
            "content": "Vụ tai nạn giao thông xảy ra vào sáng nay đã khiến 3 người bị thương nặng và phải đưa đi cấp cứu."
        },
        {
            "title": "Dự báo thời tiết ngày mai",
            "content": "Theo dự báo của trung tâm khí tượng, ngày mai trời sẽ có mây, nhiệt độ từ 25-30 độ C."
        }
    ]
    
    print("=== TEST GEMINI 2.0 FLASH API ===")
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['title']}")
        result = filter_obj.analyze_news(test['title'], test['content'])
        print(f"Result: {result}")
        print(f"Is Positive: {filter_obj.is_positive_news(test['title'], test['content'])}")
    
    print(f"\nAPI Usage Stats: {filter_obj.get_stats()}")

if __name__ == "__main__":
    test_gemini_filter()
```

### Bước 3: Cập nhật `main.py`

```python
from utils.gemini_filter import GeminiNewsFilter
from utils.rss_crawler import get_rss_feeds, get_articles_from_feed
from utils.firebase_handler import store_news
import schedule
import time
import os

# Cấu hình API key
GEMINI_API_KEY = "AIzaSyCZbOdmDcqzmzJceMKWCznm-mlp8HBrsbk"

# Khởi tạo Gemini filter với API key thực tế
news_analyzer = GeminiNewsFilter(GEMINI_API_KEY)

def job():
    """
    Job chính để crawl và lọc tin tức
    """
    print("🚀 Bắt đầu crawl tin tức...")
    
    try:
        feeds = get_rss_feeds()
        total_articles = 0
        positive_articles = 0
        
        for feed_url in feeds:
            print(f"📡 Đang xử lý feed: {feed_url}")
            articles = get_articles_from_feed(feed_url)
            
            for article in articles:
                total_articles += 1
                print(f"📰 Đang phân tích: {article['title'][:50]}...")
                
                # Sử dụng Gemini API để phân tích
                if news_analyzer.is_positive_news(article['title'], article.get('description', '')):
                    positive_articles += 1
                    store_news(article)
                    print(f"✅ Lưu tin tích cực: {article['title']}")
                else:
                    print(f"❌ Bỏ qua tin không phù hợp")
        
        # Thống kê
        stats = news_analyzer.get_stats()
        print(f"\n📊 THỐNG KÊ:")
        print(f"- Tổng số bài: {total_articles}")
        print(f"- Bài tích cực: {positive_articles}")
        print(f"- API calls đã dùng: {stats['requests_used']}")
        print(f"- API calls còn lại: {stats['requests_remaining']}")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình crawl: {e}")

def main():
    """
    Main function
    """
    print("🤖 Safe News Crawler với Gemini 2.0 Flash API")
    print("=" * 50)
    
    # Test API trước khi bắt đầu
    try:
        test_result = news_analyzer.analyze_news(
            "Test bài viết", 
            "Đây là bài test để kiểm tra API hoạt động"
        )
        print(f"✅ API test thành công: {test_result}")
    except Exception as e:
        print(f"❌ API test thất bại: {e}")
        return
    
    # Chạy job ngay lần đầu
    job()
    
    # Lập lịch chạy mỗi giờ
    schedule.every().hour.do(job)
    
    print("⏰ Lập lịch chạy mỗi giờ...")
    print("Nhấn Ctrl+C để dừng")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
```

### 🧪 Bước 4: Test API trước khi chạy chính

```bash
# Test Gemini API với file test
/e/Lenovo/laragon/bin/python/python-3.10/python.exe utils/gemini_filter.py
```

### 🔧 Bước 5: Cấu hình Environment Variable (Tuỳ chọn)

Để bảo mật API key tốt hơn, tạo file `.env`:

```bash
# File .env
GEMINI_API_KEY=AIzaSyCZbOdmDcqzmzJceMKWCznm-mlp8HBrsbk
```

Và cập nhật `main.py`:

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

### 📊 Bước 6: Monitoring và Optimization

Thêm vào `main.py` để theo dõi performance:

```python
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_crawler.log'),
        logging.StreamHandler()
    ]
)

def job():
    start_time = datetime.now()
    logging.info("🚀 Bắt đầu crawl tin tức...")
    
    # ... existing code ...
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logging.info(f"⏱️ Hoàn thành trong {duration:.2f} giây")
```

### 🚨 Lưu ý quan trọng

1. **Giới hạn API**: 1500 requests/ngày, tương đương ~24 requests/giờ
2. **Rate limiting**: Thêm delay giữa các requests nếu cần
3. **Caching**: Sử dụng SQLite cache để tránh duplicate calls
4. **Error handling**: Có fallback khi API fail
5. **Monitoring**: Log chi tiết để debug

### 🎯 Kết quả mong đợi

- ⚡ **Tốc độ**: Tăng 5-10x so với local models
- 💾 **RAM**: Giảm 90% usage
- 🎯 **Độ chính xác**: Cao hơn nhờ AI model mạnh
- 💰 **Chi phí**: Hoàn toàn miễn phí trong free tier

---
