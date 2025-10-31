"""
Simple News Analyzer - Optimized for Firebase Integration
Tích hợp với Gemini 2.0 Flash để phân tích tin tức và transform sang Firebase schema
Author: AI Assistant
Version: 3.0
"""

import json
import logging
import hashlib
import time
from typing import Dict, Optional
import google.generativeai as genai
from datetime import datetime


class NewsAnalyzer:
    """
    Analyzer đơn giản với transform từ Gemini response sang Firebase schema
    Chỉ sử dụng title + URL, Gemini tự đọc full content
    """

    def __init__(self, api_key: str):
        """Khởi tạo với Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.cache = {}  # Simple in-memory cache
        self.last_call_time = 0
        self.min_call_interval = 2.0  # Minimum 2 seconds between calls

    def analyze_and_transform(self, rss_data: Dict) -> Optional[Dict]:
        """
        Phân tích với Gemini và transform sang Firebase schema
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

        # Rate limiting
        self._wait_for_rate_limit()

        # 1. Gọi Gemini với title + URL
        gemini_result = self._call_gemini(rss_data['title'], rss_data['link'])

        if not gemini_result:
            return None        # 2. Transform sang Firebase schema
        firebase_data = self._transform_to_firebase(gemini_result, rss_data)

        # 3. Cache result (bất kể sentiment)
        self.cache[cache_key] = firebase_data

        # 4. Log kết quả
        sentiment = firebase_data.get('sentiment', 0)
        if sentiment >= 0 and not firebase_data.get('is_toxic', True):
            logging.info(f"✅ Analysis success: {rss_data['title'][:50]}...")
        else:
            sentiment_text = "POSITIVE" if sentiment == 1 else "NEGATIVE" if sentiment == -1 else "NEUTRAL"
            toxic_text = "TOXIC" if firebase_data.get(
                'is_toxic', False) else "SAFE"
            logging.info(
                f"⚠️ Article filtered out: {rss_data['title'][:50]}... ({sentiment_text}, {toxic_text})")

        return firebase_data

    def _call_gemini(self, title: str, url: str) -> Optional[Dict]:
        """Gọi Gemini API với prompt đơn giản"""
        prompt = self._create_firebase_prompt(title, url)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'max_output_tokens': 200,  # Tăng từ 150 lên 200
                    'top_p': 0.8,
                    'top_k': 10
                }
            )

            result = self._parse_json_response(response.text)

            if self._validate_gemini_result(result):
                return result
            else:
                logging.warning(f"⚠️ Invalid Gemini result: {title[:50]}...")
                return None

        except Exception as e:
            logging.error(f"❌ Gemini API error: {title[:50]}... Error: {e}")
            return None

    def _create_firebase_prompt(self, title: str, url: str) -> str:
        return f"""
                BẠN LÀ MỘT CHUYÊN GIA PHÂN TÍCH TIN TỨC TIẾNG VIỆT

                NHIỆM VỤ:
                1. Truy cập và đọc TOÀN BỘ bài báo từ URL (CHỈ QUAN TÂM ĐOẠN TEXT - CONTENT bài báo, KHÔNG QUAN TÂM CODE)
                2. Phân tích cảm xúc dựa trên toàn bộ nội dung
                3. Phân loại chủ đề để tập trung khi phân tích, tạo mô tả ngắn
                4. Đánh giá tính độc hại nội dung bài báo
                5. Phát hiện đánh lừa bởi tiêu đề

                BÀI BÁO:
                URL: {url}
                Tiêu đề: "{title}"


                PHÂN LOẠI SENTIMENT (CHÚ Ý: NEGATIVE khác TOXIC):

                POSITED NEWS (sentiment = 1):
                - Thành tựu: Học bổng, giải thưởng, tốt nghiệp
                - Niềm vui gia đình: Đám cưới, sinh con, đoàn tụ
                - Sức khỏe: Chữa khỏi bệnh, đột phá y học
                - Việc tốt: Từ thiện, tình nguyện, giúp đỡ
                - Sáng tạo: Công nghệ tích cực, khám phá khoa học
                - Cảm hứng: Lễ hội văn hóa, thành tựu nghệ thuật
                - Vượt khó: Khuyết tật thành công, chuyển đổi tích cực
                - Thành công: Kinh doanh phát triển, khởi nghiệp

                NEUTRAL (sentiment = 0) - ƯU TIÊN CHO TIN CẢNH BÁO/GIÁO DỤC:
                - Thống kê, báo cáo khách quan
                - Hướng dẫn kỹ thuật, thủ tục
                - Thông tin giáo dục, cảnh báo
                - Phản ánh vấn đề xã hội để cải thiện
                - Tin tức thông tin không mang cảm xúc mạnh
                - Cảnh báo sức khỏe có tính giáo dục
                - Phân tích khó khăn với mục đích thông tin

                NEGATIVE NEWS (sentiment = -1) - CHỈ KHI THỰC SỰ BẤT HẠNH:
                - Tử vong, tai nạn, thảm họa NGHIÊM TRỌNG
                - Tội phạm, bạo lực, khủng bố CHẾT NGƯỜI
                - Dịch bệnh, đau khổ, bi kịch NẶNG NỀ
                - Mất mát nghiêm trọng về sức khỏe/cơ thể (mất chức năng sống, hỏng hoặc cắt bỏ bộ phận cơ thể, di chứng nặng nề)
                - Nội dung mô tả hậu quả kinh dị, gây ám ảnh, mất mát lớn về thể chất hoặc tinh thần
                - Ly hôn, chia tay, mất mát lớn về THỂ CHẤT hoặc TINH THẦN
                - Phá sản, thất nghiệp, khủng hoảng THIỆT HẠI NGHIÊM TRỌNG
                - Tham nhũng, lừa đảo, bê bối nghiêm trọng KHÍCH CHÍNH QUYỀN

                TOXIC CONTENT (is_toxic = true):
                - Kích động thù hận, phân biệt chủng tộc
                - Bạo lực, nội dung 18+
                - Tin giả có hại, lừa đảo trực tiếp
                - Ngôn từ xúc phạm, chửi bới, tục tiểu
                - Kích động bạo lực, tự tử
                => ĐẶT is_toxic = true khi THỰC SỰ có hại

                LỪA ĐẢO TIÊU ĐỀ:
                CHÚ Ý: Tiêu đề tích cực nhưng nội dung tiêu cực
                VD: "Sinh viên nhận học bổng" nhưng phát hiện gian lận

                BƯỚC PHÂN TÍCH:
                1. Đọc TOÀN BỘ nội dung từ URL
                2. KHÔNG chỉ dựa vào tiêu đề
                3. Ưu tiên giá trị thông tin/giáo dục của bài viết
                4. Cân nhắc sentiment = 0 cho tin cảnh báo/giáo dục
                5. Chỉ đánh is_toxic = true nếu THỰC SỰ có hại
                6. Tạo mô tả tích cực, tập trung vào giá trị thông tin

                MẪU JSON TRẢ VỀ:
                {{
                    "description": "Mô tả tích cực 1-2 câu tiếng Việt",
                    "is_toxic": true chỉ khi nội dung thực có hại,
                    "sentiment": 1 (tích cực), 0 (trung tính - ưu tiên), -1 (tiêu cực thật sự)
                }}

                CHỈ trả JSON, không giải thích.
            """

    def _parse_json_response(self, response_text: str) -> Optional[Dict]:
        """Parse JSON từ Gemini response"""
        try:
            # Clean response
            text = response_text.strip()

            # Extract JSON from markdown if present
            if '```json' in text:
                import re
                json_match = re.search(
                    r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    text = json_match.group(1)
            elif '```' in text:
                text = text.replace('```', '').strip()

            # Parse JSON
            result = json.loads(text)
            return result

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

        # Check required fields
        required_fields = ['category', 'description', 'is_toxic', 'sentiment']
        if not all(field in result for field in required_fields):
            return False

        # Check sentiment
        if result['sentiment'] not in [1, 0, -1]:
            return False

        # Check is_toxic
        if not isinstance(result['is_toxic'], bool):
            return False

        # Check description
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

    def _wait_for_rate_limit(self):
        """Rate limiting để tránh vượt quá API limits"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time

        if time_since_last_call < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last_call
            time.sleep(sleep_time)

        self.last_call_time = time.time()
