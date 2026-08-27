"""
Fast Rule Filter (Tầng 1 - Heuristic & Keyword Filter)
Phát hiện và loại bỏ các tin tức tiêu cực nặng, tai nạn chết người, bạo lực trong 0ms.
Giúp tiết kiệm chi phí gọi Gemini API và tăng tốc độ xử lý pipeline.
"""

import re
import logging
from typing import Tuple, Optional


class RuleFilter:
    """Bộ lọc quy tắc nhanh cho tin tức tiếng Việt"""

    # Danh sách các mẫu regex từ khóa tiêu cực nặng (Bắt buộc loại bỏ)
    EXTREME_NEGATIVE_PATTERNS = [
        # Án mạng, giết người, bạo lực dã man
        r"giết\s*người",
        r"sát\s*hại",
        r"án\s*mạng",
        r"tử\s*hình",
        r"đâm\s*chết",
        r"chém\s*(người|chết|thương)",
        r"thi\s*thể",
        r"xác\s*chết",
        r"phát\s*hiện\s*xác",
        r"bóp\s*cổ",
        r"hạ\s*sát",
        r"hành\s*hung\s*(dã\s*man|tàn\s*bạo)?",
        r"đá\s*tới\s*tấp",
        r"bắn\s*chết",
        r"truy\s*sát",
        r"bắt\s*cóc",
        r"hiếp\s*dâm",
        r"xâm\s*hại\s*(tình\s*dục|trẻ\s*em)",

        # Tử vong, tai nạn, thảm họa thương tâm
        r"tử\s*vong",
        r"chết\s*người",
        r"thiệt\s*mạng",
        r"thảm\s*họa(\s*lũ\s*quét|\s*cháy|\s*rơi\s*máy\s*bay)?",
        r"tai\s*nạn\s*(kinh\s*hoàng|liên\s*hoàn|thảm\s*khốc|chết)",
        r"(lũ\s*quét|sạt\s*lở).*(vùi\s*lấp|cuốn\s*trôi|thương\s*vong)",
        r"đuối\s*nước.*(tử\s*vong|chết)",
        r"cháy\s*nhà.*(chết|thiêu\s*rụi|nạn\s*nhân)",
        r"hỏa\s*hoạn.*(chết|thương\s*vong|thiêu\s*rụi)",
        r"rơi\s*lầu.*(tử\s*vong|chết)",
        r"tự\s*tử",
        r"treo\s*cổ",

        # Tội phạm ma túy, buôn người, cướp giật quy mô lớn
        r"vận\s*chuyển.*ma\s*túy",
        r"đường\s*dây\s*ma\s*túy",
        r"buôn\s*bán\s*người",
        r"đường\s*dây\s*đánh\s*bạc.*(nghìn\s*tỷ|lớn)",
        r"cướp\s*(giật|tiệm\s*vàng|ngân\s*hàng)",
    ]

    # Danh sách các từ khóa ngoại lệ (Bypass/Whitelist) - Chuyển sang AI đánh giá
    WHITELIST_PATTERNS = [
        r"cảnh\s*báo\s*(thủ\s*đoạn|lừa\s*đảo|chiêu\s*trò|nguy\s*cơ)",
        r"thủ\s*đoạn\s*(lừa\s*đảo|chiếm\s*đoạt)",
        r"phòng\s*tránh",
        r"kỹ\s*năng\s*(thoát\s*hiểm|xử\s*lý)",
        r"cứu\s*sống",
        r"chữa\s*khỏi",
        r"vượt\s*qua\s*(bạo\s*bệnh|khó\s*khăn|nghịch\s*cảnh)",
        r"bác\s*bỏ\s*tin\s*đồn",
        r"tuyên\s*dương",
        r"khen\s*thưởng",
    ]

    def __init__(self):
        # Compile trước regex để tối ưu hiệu năng tối đa
        self.compiled_negative = [
            re.compile(p, re.IGNORECASE | re.UNICODE) for p in self.EXTREME_NEGATIVE_PATTERNS
        ]
        self.compiled_whitelist = [
            re.compile(p, re.IGNORECASE | re.UNICODE) for p in self.WHITELIST_PATTERNS
        ]
        logging.info(f"✅ RuleFilter initialized with {len(self.compiled_negative)} negative patterns.")

    def check_article(self, title: str, summary: str = "") -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra bài báo có thuộc diện tiêu cực nặng cần loại bỏ ngay không.
        
        Args:
            title: Tiêu đề bài báo
            summary: Đoạn tóm tắt ngắn từ RSS (nếu có)
            
        Returns:
            (is_negative, reason):
            - is_negative = True: Cần loại bỏ ngay (sentiment = -1)
            - is_negative = False: Tin an toàn hoặc cần đưa sang AI phân tích
        """
        text_to_check = f"{title} {summary}".strip()
        if not text_to_check:
            return False, None

        # 1. Kiểm tra whitelist (Nếu chứa từ khóa giáo dục/cảnh báo -> KHÔNG chặn)
        for pattern in self.compiled_whitelist:
            match = pattern.search(text_to_check)
            if match:
                # Đưa sang AI đánh giá chi tiết
                return False, f"WHITELISTED: {match.group(0)}"

        # 2. Kiểm tra danh sách tiêu cực nặng
        for pattern in self.compiled_negative:
            match = pattern.search(text_to_check)
            if match:
                matched_word = match.group(0)
                logging.info(f"⚡ [FAST-RULE] Blocked negative article: '{title[:50]}...' (Matched: '{matched_word}')")
                return True, f"MATCHED_NEGATIVE: {matched_word}"

        # Không phát hiện tiêu cực rõ ràng -> Chuyển sang Tầng 2
        return False, None
