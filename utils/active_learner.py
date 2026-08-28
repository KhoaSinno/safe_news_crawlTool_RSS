"""
Active Learning & User Feedback Loop
Tự động thu thập các bài báo bị người dùng report trên ứng dụng di động,
sử dụng Gemini để phân tích nguyên nhân và trích xuất từ khóa tiêu cực mới
nhằm liên tục cập nhật bộ lọc Fast Rule mà không cần can thiệp thủ công.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from google import genai
from google.genai import types

class ActiveLearner:
    """Module tự động học từ phản hồi và báo cáo của người dùng"""

    def __init__(self, api_key: str, config_path: str = "config/learned_patterns.json"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
        self.config_path = config_path
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        dir_name = os.path.dirname(self.config_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

    def load_learned_patterns(self) -> List[str]:
        """Đọc danh sách các mẫu từ khóa đã tự động học"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('learned_patterns', [])
            except Exception as e:
                logging.warning(f"⚠️ Không thể đọc file learned patterns: {e}")
        return []

    def save_learned_patterns(self, patterns: List[str]):
        """Lưu danh sách các mẫu từ khóa mới vào file cấu hình"""
        self._ensure_config_dir()
        existing = set(self.load_learned_patterns())
        existing.update(patterns)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({'learned_patterns': sorted(list(existing))}, f, ensure_ascii=False, indent=2)
        logging.info(f"💾 Đã cập nhật {len(existing)} learned patterns vào {self.config_path}")

    def process_user_reports(self, db) -> int:
        """
        Quét Firestore collection `article_reports` và tự động cập nhật bộ lọc
        """
        if db is None:
            logging.warning("⚠️ Firestore DB client is not initialized.")
            return 0

        try:
            reports_ref = db.collection('article_reports')
            # Lấy các báo cáo chưa được xử lý
            query = reports_ref.where('processed', '==', False).limit(20)
            docs = list(query.stream())

            # Fallback nếu trường processed chưa có
            if not docs:
                query = reports_ref.limit(20)
                all_docs = list(query.stream())
                docs = [d for d in all_docs if not d.to_dict().get('processed', False)]

            if not docs:
                logging.info("ℹ️ Không có bài báo cáo nào mới từ người dùng.")
                return 0

            logging.info(f"🔍 Tìm thấy {len(docs)} báo cáo cần xử lý qua Active Learning...")
            new_patterns = []

            for doc in docs:
                data = doc.to_dict()
                title = data.get('title', '')
                reason = data.get('reason', '')

                pattern = self._extract_keyword_pattern(title, reason)
                if pattern:
                    new_patterns.append(pattern)
                    logging.info(f"🧠 [ACTIVE-LEARNED] Trích xuất mẫu mới: '{pattern}' từ báo cáo: '{title[:40]}...'")

                # Đánh dấu đã xử lý
                doc.reference.update({
                    'processed': True,
                    'processed_at': types.datetime.datetime.now().isoformat() if hasattr(types, 'datetime') else "PROCESSED"
                })

            if new_patterns:
                self.save_learned_patterns(new_patterns)

            return len(new_patterns)

        except Exception as e:
            logging.error(f"❌ Lỗi khi xử lý Active Learning reports: {e}")
            return 0

    def _extract_keyword_pattern(self, title: str, reason: str) -> Optional[str]:
        """Sử dụng Gemini để trích xuất cụm từ tiêu cực đặc trưng"""
        prompt = f"""
Bạn là chuyên gia NLP. Người dùng đã báo cáo bài báo sau là tiêu cực/bạo lực hoặc phân loại sai:
- Tiêu đề: "{title}"
- Lý do báo cáo: "{reason}"

Nhiệm vụ: Trích xuất 1 cụm từ tiếng Việt ngắn (2-4 từ) tiêu biểu nhất đại diện cho hành vi/nội dung tiêu cực trong bài báo này để làm mẫu regex lọc bài tự động.

Yêu cầu đầu ra (JSON ONLY):
{{
    "pattern": "từ_khóa_tiếng_việt"
}}
Nếu không có từ khóa tiêu cực rõ ràng, trả về: {{"pattern": null}}
"""
        try:
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=256,
                response_mime_type="application/json",
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            if response.text:
                cleaned = response.text.replace('***', '').strip()
                res = json.loads(cleaned)
                pat = res.get('pattern')
                if pat and len(pat.strip()) > 2:
                    return pat.strip().lower()
        except Exception as e:
            logging.debug(f"AI Keyword extraction error: {e}")
        return None
