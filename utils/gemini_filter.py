"""
Gemini Safe News Handling
Tối ưu hóa cho Gemini 2.0 Flash API với rate limiting, caching và fallback
Author: Sinoo colab Claude
Version: 2.0
"""

import google.generativeai as genai
import requests
import json
import time
import hashlib
import sqlite3
from typing import Dict, Optional
import random
from functools import wraps
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def rate_limit_decorator(max_calls_per_minute=10):
    """
    Decorator để giới hạn số calls API per minute để tránh rate limit
    Args:
        max_calls_per_minute: Số calls tối đa mỗi phút (default: 10)
    """
    def decorator(func):
        last_called = [0.0]
        call_count = [0]
        window_start = [time.time()]

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()

            # Reset counter nếu đã qua 1 phút
            if current_time - window_start[0] >= 60:
                call_count[0] = 0
                window_start[0] = current_time

            # Kiểm tra nếu đã đạt limit
            if call_count[0] >= max_calls_per_minute:
                wait_time = 60 - (current_time - window_start[0])
                logging.info(
                    f"Rate limit reached, waiting {wait_time:.1f}s...")
                time.sleep(wait_time + 2)  # Thêm 2s buffer
                # Reset sau khi wait
                call_count[0] = 0
                window_start[0] = time.time()

            # Thêm delay giữa các calls
            elapsed = current_time - last_called[0]
            min_interval = 60.0 / max_calls_per_minute
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)

            call_count[0] += 1
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class GeminiNewsFilter:
    """
    Lớp chính để phân tích sentiment và toxicity của tin tức bằng Gemini API

    Features:
    - Rate limiting (10 calls/minute)
    - Smart caching (exact + fuzzy matching)
    - Rule-based fallback
    - Exponential backoff retry
    - Token optimization
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "gemini-2.0-flash"
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

        # Limits và counters
        self.request_count = 0
        self.daily_limit = 1500
        self.minute_limit = 10

        # Khởi tạo cache và backup model
        self.cache = ResultCache()
        genai.configure(api_key=api_key)
        self.backup_model = genai.GenerativeModel('gemini-pro')

    @rate_limit_decorator(max_calls_per_minute=10)
    def _call_gemini_api(self, title: str, content: str) -> Dict:
        """
        Gọi Gemini 2.0 Flash API trực tiếp với rate limiting
        """
        if self.request_count >= self.daily_limit:
            raise Exception("Đã đạt giới hạn daily limit của Gemini API")

        # Tối ưu độ dài text
        text = f"{title}. {content}"[:800]

        # Prompt tối ưu hóa
        prompt = f"""
    Phân tích ngắn gọn: "{text}"

    Trả về JSON:
    {{"sentiment": "POSITIVE/NEGATIVE/NEUTRAL", "toxicity": false, "confidence": 0.8}}

    Positive: vui, thành công, hạnh phúc, cưới, giải thưởng
    Negative: tai nạn, chết, bệnh, tham nhũng, tội phạm
    """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 50,
                "topP": 0.8,
                "topK": 10
            }
        }

        headers = {'Content-Type': 'application/json'}
        max_retries = 3

        for attempt in range(max_retries):
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
                    content_text = result['candidates'][0]['content']['parts'][0]['text'].strip(
                    )

                    # Parse JSON response
                    try:
                        if content_text.startswith('```json'):
                            content_text = content_text.replace(
                                '```json', '').replace('```', '').strip()

                        parsed_result = json.loads(content_text)

                        if self._validate_result(parsed_result):
                            return parsed_result
                        else:
                            return self._get_fallback_result()

                    except json.JSONDecodeError as e:
                        logging.error(
                            f"JSON Parse Error: {e}, Response: {content_text}")
                        return self._get_fallback_result()

                elif response.status_code == 429:
                    # Rate limit exceeded
                    logging.warning(
                        f"Rate limit exceeded (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        wait_time = 30 + random.uniform(5, 15)
                        time.sleep(wait_time)
                        continue
                    else:
                        return self._rule_based_analysis(title, content)

                elif response.status_code == 503:
                    # Model overloaded
                    logging.warning(
                        f"Model overloaded (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        wait_time = 20 + random.uniform(5, 10)
                        time.sleep(wait_time)
                        continue
                    else:
                        return self._rule_based_analysis(title, content)

                else:
                    logging.error(
                        f"API Error: {response.status_code}, {response.text}")
                    return self._rule_based_analysis(title, content)

            except Exception as e:
                logging.error(
                    f"Gemini API call error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                    continue
                else:
                    return self._rule_based_analysis(title, content)

        return self._rule_based_analysis(title, content)

    def analyze_news(self, title: str, content: str) -> Dict:
        """
        Phân tích tin tức với caching thông minh và fallback

        Thứ tự ưu tiên:
        1. Exact cache match
        2. Fuzzy cache match  
        3. Rule-based analysis (nếu confidence cao)
        4. Gemini API call
        5. Rule-based fallback
        """
        text = f"{title}. {content}"

        # 1. Kiểm tra exact cache
        cached_result = self.cache.get_cached_result(text)
        if cached_result:
            logging.info("Using exact cached result")
            return {
                "sentiment": cached_result[0],
                "toxicity": bool(cached_result[1]),
                "confidence": cached_result[2]
            }

        # 2. Kiểm tra fuzzy cache
        similar_result = self.cache.get_similar_result(title)
        if similar_result:
            logging.info("Using similar cached result")
            return {
                "sentiment": similar_result[0],
                "toxicity": bool(similar_result[1]),
                "confidence": similar_result[2] * 0.8  # Giảm confidence
            }

        # 3. Thử rule-based trước
        rule_based_result = self._rule_based_analysis(title, content)
        if rule_based_result['confidence'] > 0.7:
            logging.info("Using rule-based analysis (high confidence)")
            self.cache.cache_result(text, rule_based_result)
            return rule_based_result

        # 4. Gọi API nếu rule-based không đủ tin cậy
        try:
            result = self._call_gemini_api(title, content)
            self.cache.cache_result(text, result)
            return result
        except Exception as e:
            logging.error(f"Direct API failed: {e}, using rule-based fallback")
            return rule_based_result

    def _rule_based_analysis(self, title: str, content: str) -> Dict:
        """
        Phân tích dựa trên từ khóa cho các trường hợp API fail
        """
        text = f"{title} {content}".lower()

        # Từ khóa tiêu cực (mở rộng)
        negative_keywords = [
            "tai nạn", "chết", "tử vong", "qua đời", "thiệt mạng", "hy sinh",
            "bệnh", "ung thư", "covid", "dịch bệnh", "viêm", "nhiễm trùng",
            "ly hôn", "chia tay", "tan vỡ", "khủng hoảng", "xung đột",
            "tham nhũng", "tội phạm", "trộm cắp", "cướp", "lừa đảo", "bắt giữ",
            "thảm họa", "lũ lụt", "động đất", "cháy nổ", "sập", "đổ",
            "mất việc", "phá sản", "suy thoái", "đình công", "khó khăn",
            "chiến tranh", "bạo lực", "đánh", "giết", "tấn công",
            "buồn", "đau khổ", "thất vọng", "lo lắng", "sợ hãi", "khóc",
            "cáo buộc", "kiện", "phạt", "vi phạm", "lỗi", "án"
        ]

        # Từ khóa tích cực (mở rộng)
        positive_keywords = [
            "thành công", "chiến thắng", "đạt được", "hoàn thành", "xuất sắc",
            "hạnh phúc", "vui mừng", "kỷ niệm", "lễ hội", "ăn mừng", "vui vẻ",
            "cưới", "đám cưới", "sinh con", "chào đời", "em bé", "gia đình",
            "thăng tiến", "tăng lương", "được tặng", "nhận giải", "vinh danh",
            "đoàn tụ", "sum họp", "hòa giải", "yêu thương", "tình yêu",
            "phát triển", "tăng trưởng", "cải thiện", "tốt lên", "tiến bộ",
            "học giỏi", "thủ khoa", "giải thưởng", "khen thưởng", "tốt nghiệp",
            "khỏe mạnh", "bình phục", "chữa khỏi", "điều trị thành công",
            "giúp đỡ", "từ thiện", "tặng", "hỗ trợ", "cứu", "cứu trợ",
            "khai trương", "mở cửa", "ra mắt", "công bố"
        ]

        # Từ khóa trung tính
        neutral_keywords = [
            "dự báo", "thời tiết", "nhiệt độ", "mây", "nắng", "mưa",
            "lịch", "chương trình", "kế hoạch", "thông báo", "công bố",
            "họp", "hội nghị", "cuộc gặp", "thảo luận", "bàn bạc",
            "số liệu", "thống kê", "báo cáo", "nghiên cứu", "khảo sát"
        ]

        # Đếm từ khóa
        negative_count = sum(1 for word in negative_keywords if word in text)
        positive_count = sum(1 for word in positive_keywords if word in text)
        neutral_count = sum(1 for word in neutral_keywords if word in text)

        # Xác định sentiment
        if positive_count > negative_count and positive_count > neutral_count:
            sentiment = "POSITIVE"
            confidence = min(0.9, 0.6 + positive_count * 0.1)
        elif negative_count > positive_count and negative_count > neutral_count:
            sentiment = "NEGATIVE"
            confidence = min(0.9, 0.6 + negative_count * 0.1)
        elif neutral_count > 0:
            sentiment = "NEUTRAL"
            confidence = min(0.8, 0.5 + neutral_count * 0.1)
        else:
            sentiment = "NEUTRAL"
            confidence = 0.5

        # Tăng confidence nếu có nhiều từ khóa
        total_keywords = negative_count + positive_count + neutral_count
        if total_keywords >= 3:
            confidence += 0.1

        return {
            "sentiment": sentiment,
            "toxicity": False,  # Rule-based không detect toxicity
            "confidence": confidence
        }

    def _validate_result(self, result: Dict) -> bool:
        """Validate kết quả từ API"""
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
        """Kết quả mặc định khi API fail"""
        return {"sentiment": "NEUTRAL", "toxicity": False, "confidence": 0.5}

    def is_positive_news(self, title: str, content: str) -> bool:
        """
        Kiểm tra tin tức có tích cực không (threshold giảm để lưu nhiều tin hơn)
        """
        result = self.analyze_news(title, content)
        return (
            result["sentiment"] == "POSITIVE" and
            not result["toxicity"] and
            result["confidence"] > 0.5  # Giảm từ 0.6 xuống 0.5
        )

    def get_stats(self) -> Dict:
        """Thống kê sử dụng API"""
        return {
            "requests_used": self.request_count,
            "requests_remaining": self.daily_limit - self.request_count,
            "usage_percentage": (self.request_count / self.daily_limit) * 100
        }


class ResultCache:
    """
    Cache kết quả phân tích để tránh duplicate API calls
    Features: Exact matching + Fuzzy matching dựa trên title
    """

    def __init__(self, db_path="analysis_cache.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        """Tạo bảng cache với migration cho column title"""
        # Tạo bảng chính
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                content_hash TEXT PRIMARY KEY,
                sentiment TEXT,
                toxicity BOOLEAN,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: Thêm column title nếu chưa có
        try:
            self.conn.execute(
                "ALTER TABLE analysis_cache ADD COLUMN title TEXT")
            logging.info("Migration: Added title column to cache database")
        except sqlite3.OperationalError:
            # Column đã tồn tại
            pass

        self.conn.commit()

    def get_cached_result(self, text: str) -> Optional[tuple]:
        """Lấy kết quả cache exact match"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cursor = self.conn.execute(
            "SELECT sentiment, toxicity, confidence FROM analysis_cache WHERE content_hash = ?",
            (text_hash,)
        )
        return cursor.fetchone()

    def get_similar_result(self, title: str) -> Optional[tuple]:
        """
        Tìm kết quả tương tự dựa trên title để tiết kiệm API calls
        """
        words = title.lower().split()[:3]  # Lấy 3 từ đầu
        if len(words) < 2:
            return None

        query = f"%{words[0]}%{words[1]}%"
        cursor = self.conn.execute(
            "SELECT sentiment, toxicity, confidence FROM analysis_cache WHERE title LIKE ? LIMIT 1",
            (query,)
        )
        return cursor.fetchone()

    def cache_result(self, text: str, result: Dict):
        """Lưu kết quả vào cache"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        title = text.split('.')[0][:100]  # Lấy title (100 chars đầu)
        self.conn.execute(
            "INSERT OR REPLACE INTO analysis_cache VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)",
            (text_hash, result['sentiment'],
             result['toxicity'], result['confidence'], title)
        )
        self.conn.commit()


def test_gemini_filter():
    """Test function để kiểm tra Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please create .env file with: GEMINI_API_KEY=your_api_key")
        return

    filter_obj = GeminiNewsFilter(api_key)

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
        print(f"\n🧪 Test {i}: {test['title']}")
        result = filter_obj.analyze_news(test['title'], test['content'])
        print(f"📊 Result: {result}")
        print(
            f"✅ Is Positive: {filter_obj.is_positive_news(test['title'], test['content'])}")

    print(f"\n📈 API Usage Stats: {filter_obj.get_stats()}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    test_gemini_filter()
