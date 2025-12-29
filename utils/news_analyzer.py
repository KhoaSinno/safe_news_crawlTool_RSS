"""
Simple News Analyzer - Optimized for Firebase Integration
Tích hợp với Gemini 2.5 Flash + Google Search Grounding để đọc bài báo realtime
Author: AI Assistant
Version: 4.0 (Google Search Grounding)
"""

import json
import logging
import hashlib
import re
from typing import Dict, Optional
from datetime import datetime

# SDK mới google-genai (hỗ trợ Google Search tool)
from google import genai
from google.genai import types


class NewsAnalyzer:
    """
    Analyzer với Google Search Grounding - ĐỌC ĐƯỢC BÀI BÁO MỚI TINH

    QUAN TRỌNG: Gemini KHÔNG THỂ đọc URL trực tiếp nếu không có Google Search tool
    - Bài báo CŨ (trong training data): Gemini "nhớ" được → dễ gây hiểu lầm
    - Bài báo MỚI: BẮT BUỘC phải dùng Google Search Grounding

    Đã test và chứng minh: test_proof_search_vs_training.py
    """

    def __init__(self, api_key: str):
        """Khởi tạo với Gemini API key và Google Search tool"""

        # Sử dụng SDK mới google-genai
        self.client = genai.Client(api_key=api_key)

        # Cấu hình Google Search Grounding tool
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Config cho generate_content
        self.config = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            temperature=0.1,
            max_output_tokens=2048,
        )

        self.model_name = 'gemini-2.5-flash'
        self.cache = {}  # Simple in-memory cache

        logging.info(
            f"✅ NewsAnalyzer initialized with Google Search Grounding (model: {self.model_name})")

    def analyze_and_transform(self, rss_data: Dict) -> Optional[Dict]:
        """
        Phân tích với Gemini + Google Search và transform sang Firebase schema
        Args:
            rss_data: Dict với keys: title, link, summary, image_url, published
        Returns:
            Dict với Firebase schema hoặc None nếu không phù hợp
        """
        # Check cache first
        cache_key = self._generate_cache_key(
            rss_data['title'], rss_data['link'])
        if cache_key in self.cache:
            logging.info(f"✅ Cache hit: {rss_data['title'][:50]}...")
            return self.cache[cache_key]

        # 1. Gọi Gemini với Google Search Grounding
        gemini_result, grounding_used = self._call_gemini_with_search(
            rss_data['title'],
            rss_data['link']
        )

        if not gemini_result:
            return None

        # 2. Transform sang Firebase schema
        firebase_data = self._transform_to_firebase(gemini_result, rss_data)

        # 3. Cache result
        self.cache[cache_key] = firebase_data

        # 4. Log kết quả với thông tin grounding
        sentiment = firebase_data.get('sentiment', 0)
        grounding_status = "🔍 SEARCH" if grounding_used else "📚 TRAINING"

        if sentiment >= 0 and not firebase_data.get('is_toxic', True):
            logging.info(
                f"✅ [{grounding_status}] Analysis success: {rss_data['title'][:50]}...")
        else:
            sentiment_text = "POSITIVE" if sentiment == 1 else "NEGATIVE" if sentiment == -1 else "NEUTRAL"
            toxic_text = "TOXIC" if firebase_data.get(
                'is_toxic', False) else "SAFE"
            logging.info(
                f"⚠️ [{grounding_status}] Filtered: {rss_data['title'][:50]}... ({sentiment_text}, {toxic_text})")

        return firebase_data

    def _call_gemini_with_search(self, title: str, url: str) -> tuple[Optional[Dict], bool]:
        """
        Gọi Gemini API với Google Search Grounding
        Returns: (result_dict, grounding_was_used)
        """
        prompt = self._create_search_prompt(title, url)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config,
            )

            # Check if response exists
            if not response.candidates:
                logging.warning(
                    f"⚠️ No candidates in response: {title[:50]}...")
                return self._get_blocked_content_result(), False

            # Check grounding metadata
            grounding_used = False
            if response.candidates[0].grounding_metadata:
                gm = response.candidates[0].grounding_metadata
                if gm.web_search_queries:
                    grounding_used = True
                    logging.debug(f"🔍 Search queries: {gm.web_search_queries}")

            # Parse response
            result = self._parse_json_response(response.text)

            if self._validate_gemini_result(result):
                return result, grounding_used
            else:
                logging.warning(f"⚠️ Invalid Gemini result: {title[:50]}...")
                return None, grounding_used

        except Exception as e:
            logging.error(f"❌ Gemini API error: {title[:50]}... Error: {e}")
            return None, False

    def _create_search_prompt(self, title: str, url: str) -> str:
        """Tạo prompt yêu cầu Google Search đọc bài báo"""
        return f"""
SỬ DỤNG GOOGLE SEARCH ĐỂ TÌM VÀ ĐỌC NỘI DUNG BÀI BÁO SAU:
URL: {url}
Tiêu đề: "{title}"

SAU KHI ĐỌC NỘI DUNG THỰC TẾ TỪ BÀI BÁO, hãy phân tích theo hướng dẫn sau:

=== PHÂN LOẠI SENTIMENT ===

POSITIVE (sentiment = 1):
- Thành tựu, giải thưởng, tốt nghiệp, học bổng
- Niềm vui gia đình, đám cưới, sinh con, đoàn tụ
- Chữa khỏi bệnh, đột phá y học, sức khỏe tốt
- Từ thiện, tình nguyện, việc tốt, giúp đỡ
- Công nghệ tích cực, khám phá khoa học
- Lễ hội văn hóa, thành tựu nghệ thuật
- Vượt khó thành công, chuyển đổi tích cực

NEUTRAL (sentiment = 0) - Ưu tiên cho tin cảnh báo/giáo dục:
- Thống kê, báo cáo khách quan
- Hướng dẫn kỹ thuật, thủ tục
- Thông tin giáo dục, cảnh báo lừa đảo/tội phạm
- Phản ánh vấn đề xã hội để cải thiện
- Cảnh báo sức khỏe có tính giáo dục

NEGATIVE (sentiment = -1) - Chỉ khi THỰC SỰ bất hạnh:
- Tử vong, tai nạn, thảm họa NGHIÊM TRỌNG
- Tội phạm, bạo lực CHẾT NGƯỜI
- Bi kịch, mất mát NẶNG NỀ về thể chất/tinh thần

TOXIC (is_toxic = true):
- Kích động thù hận, phân biệt
- Bạo lực, nội dung 18+
- Tin giả có hại, lừa đảo trực tiếp
- Ngôn từ xúc phạm, tục tĩu

=== LƯU Ý QUAN TRỌNG ===
- Tin cảnh báo lừa đảo/tội phạm = CÓ ÍCH = NEUTRAL (không phải Negative)
- Phát hiện Clickbait: So sánh tiêu đề với nội dung thực tế
- Đọc TOÀN BỘ nội dung, không chỉ dựa vào tiêu đề

=== OUTPUT FORMAT (JSON ONLY) ===
{{
    "description": "Tóm tắt 1-2 câu tiếng Việt từ nội dung thực tế (max 200 chars)",
    "is_toxic": boolean,
    "sentiment": integer  // 1, 0, hoặc -1
}}

CHỈ TRẢ JSON, không giải thích thêm.
"""

    def _get_blocked_content_result(self) -> Dict:
        """Return default result for blocked/failed content"""
        return {
            'description': 'Content blocked by safety filters',
            'is_toxic': True,
            'sentiment': -1
        }

    def _parse_json_response(self, response_text: str) -> Optional[Dict]:
        """Parse JSON từ Gemini response"""
        try:
            if not response_text or not response_text.strip():
                logging.error("❌ Empty response from Gemini")
                return None

            text = response_text.strip()

            # Extract JSON from markdown if present
            if '```json' in text:
                json_match = re.search(
                    r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    text = json_match.group(1)
            elif '```' in text:
                text = text.replace('```', '').strip()

            return json.loads(text)

        except json.JSONDecodeError as e:
            logging.error(f"JSON parse error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected parse error: {e}")
            return None

    def _validate_gemini_result(self, result: Dict) -> bool:
        """Validate kết quả từ Gemini"""
        if not result:
            return False

        required_fields = ['description', 'is_toxic', 'sentiment']
        if not all(field in result for field in required_fields):
            return False

        if result['sentiment'] not in [1, 0, -1]:
            return False

        if not isinstance(result['is_toxic'], bool):
            return False

        if not result['description'] or len(str(result['description']).strip()) < 5:
            return False

        return True

    def _transform_to_firebase(self, gemini_result: Dict, rss_data: Dict) -> Dict:
        """Transform thành Firebase schema chính xác"""
        return {
            "category": rss_data.get("category", "xa-hoi"),
            "description": gemini_result.get("description", rss_data.get("summary", ""))[:200],
            "image_url": rss_data.get("image_url", ""),
            "is_toxic": gemini_result.get("is_toxic", False),
            "link": rss_data["link"],
            "published": rss_data.get("published", ""),
            "sentiment": gemini_result.get("sentiment", 0),
            "title": rss_data["title"]
        }

    def _generate_cache_key(self, title: str, url: str) -> str:
        """Tạo cache key từ title và URL"""
        content = f"{title}|{url}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
