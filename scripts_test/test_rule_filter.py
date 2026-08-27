"""
Unit Test cho RuleFilter (Tầng 1 - Fast Rule Engine)
"""

import os
import sys

# Add root path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rule_filter import RuleFilter


def test_rule_filter():
    filter_engine = RuleFilter()

    test_cases = [
        # Nhóm 1: Tiêu cực nặng (Bắt buộc phải chặn -> is_negative = True)
        ("Bảo vệ 'đá tới tấp vào đầu tài xế giao hàng' bị bắt", True, "Hành hung, bạo lực"),
        ("Chưa có nạn nhân người Việt trong thảm họa lũ quét ở biên giới Nepal", True, "Thảm họa lũ quét"),
        ("Tai nạn liên hoàn trên cao tốc khiến 3 người tử vong", True, "Tử vong, tai nạn"),
        ("Bắt đối tượng vận chuyển 20 bánh ma túy qua biên giới", True, "Vận chuyển ma túy"),
        ("Phát hiện thi thể người đàn ông trôi dạt trên sông Sài Gòn", True, "Thi thể"),
        ("Hỏa hoạn thiêu rụi xưởng gỗ trong đêm", True, "Hỏa hoạn thiêu rụi"),

        # Nhóm 2: Tích cực (Không được chặn -> is_negative = False)
        ("Thủ tướng: Giáo dục phải thoát khỏi áp lực điểm số", False, "Giáo dục tích cực"),
        ("Cậu học trò nghèo giành học bổng toàn phần Đại học Oxford", False, "Học bổng, vượt khó"),
        ("Bác sĩ Bệnh viện Chợ Rẫy cứu sống bệnh nhân ngừng tim 45 phút", False, "Cứu sống / Y tế"),
        ("Khánh thành cây cầu nối đôi bờ vui cho bà con vùng sâu", False, "Công trình xã hội"),
        ("Đội tuyển bóng đá nữ Việt Nam giành huy chương vàng SEA Games", False, "Thể thao thành tích"),

        # Nhóm 3: Cảnh báo thủ đoạn / Whitelist (Không được chặn -> is_negative = False)
        ("Công an cảnh báo thủ đoạn lừa đảo giả danh nhân viên ngân hàng", False, "Cảnh báo lừa đảo"),
        ("Kỹ năng thoát hiểm khi xảy ra cháy nổ ở chung cư", False, "Kỹ năng thoát hiểm"),
    ]

    print("=" * 80)
    print("🧪 BẮT ĐẦU KIỂM THỬ RULE FILTER (TẦNG 1):")
    print("=" * 80)

    passed_count = 0
    total_count = len(test_cases)

    for i, (title, expected_blocked, category_desc) in enumerate(test_cases, 1):
        is_blocked, reason = filter_engine.check_article(title)
        
        status = "PASSED" if is_blocked == expected_blocked else "FAILED"
        if status == "PASSED":
            passed_count += 1

        icon = "✅" if status == "PASSED" else "❌"
        block_text = "BLOCKED (Loại bỏ)" if is_blocked else "PASSED (Cho qua)"
        expected_text = "BLOCKED" if expected_blocked else "PASSED"

        print(f"[{i:02d}/{total_count:02d}] {icon} [{status}] {title}")
        print(f"     -> Kết quả: {block_text} | Kỳ vọng: {expected_text} | Lý do: {reason or 'Không phát hiện từ khóa xấu'}")

    print("=" * 80)
    print(f"📊 KẾT QUẢ TEST: {passed_count}/{total_count} bài kiểm thử thành công ({passed_count/total_count*100:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    test_rule_filter()
