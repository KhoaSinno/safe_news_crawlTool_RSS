"""
News Analyzer (Tầng 2 & 3: Trafilatura Direct Extraction + Gemini 2.5 Flash)
- Bóc tách nội dung HTML thực tế bài báo bằng Trafilatura (nhanh, chính xác 100%, 0đ chi phí Search)
- Phân tích sắc thái (sentiment), lọc độc hại (toxicity) và tóm tắt bài báo bằng Gemini 2.5 Flash
"""

import json
import logging
import hashlib
import random
import time
from typing import Annotated, Any, Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, ValidationError
import trafilatura
from google import genai
from google.genai import types
from config import settings


class ArticleAnalysisResult(BaseModel):
    """Schema ràng buộc cứng định dạng JSON đầu ra của Gemini 2.5 Flash"""
    # Do not use extra="forbid": Gemini's v1beta Schema rejects additionalProperties.
    model_config = ConfigDict(strict=True)

    description: str = Field(
        min_length=1,
        description="Tóm tắt 1-2 câu tiếng Việt từ nội dung thực tế (tối đa 200 ký tự)",
    )
    is_toxic: bool = Field(
        description="True nếu độc hại, khiêu dâm 18+, bạo lực phản cảm hoặc tin giả"
    )
    sentiment: Annotated[int, Field(ge=-1, le=1)] = Field(
        description="Sắc thái: 1 (Tích cực), 0 (Trung tính / Báo cáo / Cảnh báo an toàn), -1 (Tiêu cực / Bi kịch / Tử vong)"
    )


class NewsAnalyzer:
    """
    News Analyzer với Trafilatura Direct Extraction + Gemini 2.5 Flash.
    Không phụ thuộc vào Google Search Tool, đạt độ ổn định cao và tối ưu chi phí.
    """

    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """Khởi tạo Gemini client và config"""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name or settings.GEMINI_MODEL

        # Cấu hình generate ép kiểu JSON thuần túy với Constrained Decoding Schema
        self.config = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=1024,
            response_mime_type="application/json",
            response_schema=ArticleAnalysisResult,
        )

        self.cache = {}  # In-memory cache cho các bài đã phân tích
        logging.info(f"✅ NewsAnalyzer initialized with Trafilatura + {self.model_name} Direct (Constrained Schema)")

    def extract_content(self, url: str, fallback_text: str = "") -> Tuple[str, float]:
        """
        Trích xuất nội dung văn bản sạch từ URL bằng Trafilatura
        Returns: (clean_text, extraction_time_seconds)
        """
        import time
        start_time = time.time()
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                extracted = trafilatura.extract(
                    downloaded,
                    include_comments=False,
                    include_tables=False,
                    include_images=False,
                    no_fallback=False
                )
                if extracted and len(extracted.strip()) > 50:
                    # Bỏ qua nếu nội dung chỉ là hướng dẫn phím tắt của video player
                    if 'phím tắt điều khiển video' in extracted.lower():
                        elapsed = time.time() - start_time
                        return fallback_text.strip(), elapsed

                    elapsed = time.time() - start_time
                    return extracted.strip(), elapsed

            # Fallback nếu không bóc tách được từ web
            elapsed = time.time() - start_time
            return fallback_text.strip(), elapsed
        except Exception as e:
            logging.warning(f"⚠️ Trafilatura extraction failed for {url}: {e}")
            elapsed = time.time() - start_time
            return fallback_text.strip(), elapsed

    def analyze_and_transform(self, rss_data: Dict) -> Optional[Dict]:
        """
        Bóc tách text bằng Trafilatura -> Phân tích bằng Gemini -> Chuyển đổi sang Firebase Schema.
        
        Args:
            rss_data: Dict với keys: title, link, summary, image_url, published, category
        Returns:
            Dict chuẩn Firebase schema hoặc None nếu lỗi
        """
        title = rss_data.get('title', '')
        link = rss_data.get('link', '')
        summary = rss_data.get('summary', '')

        # 1. Kiểm tra cache
        cache_key = self._generate_cache_key(title, link)
        if cache_key in self.cache:
            logging.info(f"✅ Cache hit: {title[:50]}...")
            return self.cache[cache_key]

        # 2. Bóc tách nội dung thực tế bằng Trafilatura
        article_text, extract_time = self.extract_content(link, fallback_text=summary)
        
        # Cắt bớt văn bản (2000 ký tự đầu là đủ thông tin cốt lõi, tiết kiệm token)
        clean_content = article_text[:2000] if article_text else title

        # 3. Gọi Gemini phân tích văn bản trực tiếp
        gemini_result, metrics = self._call_gemini_direct(title, clean_content)
        if not gemini_result:
            return None

        metrics['extract_time'] = extract_time
        metrics['content_length'] = len(article_text)

        # 4. Transform sang Firebase schema
        firebase_data = self._transform_to_firebase(gemini_result, rss_data)
        firebase_data['_metrics'] = metrics

        # 5. Lưu cache
        self.cache[cache_key] = firebase_data

        # 6. Log kết quả
        sentiment = firebase_data.get('sentiment', 0)
        is_toxic = firebase_data.get('is_toxic', False)
        sentiment_text = "POSITIVE" if sentiment == 1 else "NEGATIVE" if sentiment == -1 else "NEUTRAL"
        toxic_text = "TOXIC" if is_toxic else "SAFE"

        logging.info(
            f"⚡ [AI-ANALYZED] {title[:50]}... ({sentiment_text}, {toxic_text}) [Extract: {extract_time:.2f}s | LLM: {metrics.get('llm_time', 0):.2f}s | Tokens: {metrics.get('total_tokens', 0)}]"
        )

        return firebase_data

    def _call_gemini_direct(self, title: str, content: str) -> Tuple[Optional[Dict], Dict]:
        """Gọi Gemini API, validate output schema và retry lỗi tạm thời."""
        prompt = self._create_analysis_prompt(title, content)
        metrics = {
            'prompt_tokens': 0,
            'candidates_tokens': 0,
            'total_tokens': 0,
            'llm_time': 0.0,
            'attempts': 0,
            'retry_count': 0,
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                metrics['attempts'] = attempt + 1
                start_llm = time.time()
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self.config,
                )
                llm_time = time.time() - start_llm
                metrics['llm_time'] = round(llm_time, 3)

                # Lấy token count từ usage_metadata nếu có
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    metrics['prompt_tokens'] = response.usage_metadata.prompt_token_count or 0
                    metrics['candidates_tokens'] = response.usage_metadata.candidates_token_count or 0
                    metrics['total_tokens'] = metrics['prompt_tokens'] + metrics['candidates_tokens']

                if not response.candidates:
                    logging.warning(f"⚠️ No candidates in response: {title[:50]}...")
                    return self._get_blocked_content_result(), metrics

                result = self._parse_structured_response(response)

                if result:
                    return result, metrics

                logging.warning(
                    "⚠️ Invalid Gemini structured response for '%s' | Raw=%s...",
                    title[:40],
                    self._response_text(response)[:120],
                )
                if attempt < max_retries - 1:
                    # A schema-compliant response can still fail local business validation
                    # (for example, an overlong summary). Regenerate rather than persist it.
                    wait_time = min(8.0, 2 ** attempt) + random.uniform(0, 0.5)
                    metrics['retry_count'] += 1
                    logging.warning(
                        "⏳ Regenerating invalid structured response for '%s...' in %.2fs.",
                        title[:35], wait_time,
                    )
                    time.sleep(wait_time)
                    continue
                return None, metrics

            except Exception as e:
                if self._is_retryable_error(e) and attempt < max_retries - 1:
                    # Exponential backoff with jitter prevents synchronized retries.
                    wait_time = min(8.0, 2 ** attempt) + random.uniform(0, 0.5)
                    metrics['retry_count'] += 1
                    logging.warning(
                        "⏳ Retryable Gemini error for '%s...' (attempt %d/%d): %s. Retrying in %.2fs.",
                        title[:35], attempt + 1, max_retries, e, wait_time,
                    )
                    time.sleep(wait_time)
                    continue

                logging.error(f"❌ Gemini API error: {title[:50]}... Error: {e}")
                return None, metrics

        logging.error(f"❌ Failed to analyze '{title[:50]}' after {max_retries} attempts.")
        return None, metrics

    def _create_analysis_prompt(self, title: str, content: str) -> str:
        """Tạo prompt phân tích nội dung chuẩn xác"""
        return f"""
ĐÂY LÀ NỘI DUNG THỰC TẾ CỦA BÀI BÁO:
Tiêu đề: "{title}"
Nội dung bài viết:
\"\"\"
{content}
\"\"\"

DỰA VÀO NỘI DUNG TRÊN, hãy phân tích theo các tiêu chí sau:

=== PHÂN LOẠI SENTIMENT ===

POSITIVE (sentiment = 1):
- Thành tựu, giải thưởng, tốt nghiệp, học bổng
- Niềm vui gia đình, đám cưới, sinh con, đoàn tụ
- Chữa khỏi bệnh, đột phá y học, sức khỏe tốt
- Từ thiện, tình nguyện, việc tốt, giúp đỡ cộng đồng
- Công nghệ tích cực, chuyển đổi số, khám phá khoa học
- Lễ hội văn hóa, thành tựu nghệ thuật, thể thao chiến thắng
- Vượt khó thành công, câu chuyện truyền cảm hứng

NEUTRAL (sentiment = 0) - Dành cho tin báo cáo khách quan hoặc giáo dục phòng chống:
- Thống kê, số liệu kinh tế, báo cáo chính sách
- Hướng dẫn kỹ thuật, thủ tục hành chính
- Cảnh báo thủ đoạn lừa đảo / tội phạm (mang tính giáo dục phòng tránh cho người dân)
- Phản ánh vấn đề xã hội để cải thiện, kiến nghị mang tính xây dựng

NEGATIVE (sentiment = -1) - Chỉ khi THỰC SỰ bi kịch / tiêu cực:
- Tử vong, án mạng, bạo lực, giết người
- Tai nạn giao thông nghiêm trọng, thảm họa thiên tai gây thương vong
- Mất mát, bi kịch nặng nề

TOXIC (is_toxic = true):
- Kích động thù hận, phân biệt đối xử
- Nội dung khiêu dâm 18+, bạo lực phản cảm
- Tin giả gây hại, ngôn từ tục tĩu

"""

    def _get_blocked_content_result(self) -> Dict:
        """Kết quả mặc định khi nội dung bị safety filter chặn"""
        return {
            'description': 'Nội dung bị chặn bởi bộ lọc an toàn',
            'is_toxic': True,
            'sentiment': -1
        }

    @staticmethod
    def _response_text(response: Any) -> str:
        """Read response text safely; blocked responses may not expose text."""
        try:
            return response.text or ""
        except Exception:
            return ""

    def _parse_structured_response(self, response: Any) -> Optional[Dict]:
        """Use the SDK parsed value first, then locally validate the full contract."""
        raw_result = getattr(response, 'parsed', None)
        if raw_result is None:
            response_text = self._response_text(response)
            if not response_text:
                return None
            try:
                raw_result = json.loads(response_text)
            except json.JSONDecodeError:
                return None

        if isinstance(raw_result, dict) and set(raw_result) != set(ArticleAnalysisResult.model_fields):
            logging.debug("Gemini structured response contains missing or unexpected fields")
            return None

        try:
            result = ArticleAnalysisResult.model_validate(raw_result).model_dump()
            # Gemini may occasionally exceed maxLength. Preserve the valid analysis
            # while enforcing the Firebase storage contract deterministically.
            result['description'] = result['description'][:200]
            return result
        except ValidationError as exc:
            logging.debug("Gemini structured response failed local validation: %s", exc)
            return None

    @staticmethod
    def _is_retryable_error(error: Exception) -> bool:
        """Return True only for transient provider/network failures."""
        message = str(error).lower()
        retryable_markers = (
            '429', 'resource_exhausted', 'rate limit', 'timeout', 'timed out',
            'deadline_exceeded', 'connection reset', 'connection aborted',
            '500', '502', '503', '504', 'unavailable', 'high demand',
        )
        return any(marker in message for marker in retryable_markers)

    def _transform_to_firebase(self, gemini_result: Dict, rss_data: Dict) -> Dict:
        """Chuẩn hóa dữ liệu sang schema Firestore"""
        return {
            "category": rss_data.get("category", "tin-moi-nhat"),
            "description": gemini_result.get("description", rss_data.get("summary", ""))[:200],
            "image_url": rss_data.get("image_url", ""),
            "is_toxic": gemini_result.get("is_toxic", False),
            "link": rss_data["link"],
            "published": rss_data.get("published", ""),
            "sentiment": gemini_result.get("sentiment", 0),
            "title": rss_data["title"]
        }

    def _generate_cache_key(self, title: str, url: str) -> str:
        """Tạo cache key MD5"""
        content = f"{title}|{url}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
