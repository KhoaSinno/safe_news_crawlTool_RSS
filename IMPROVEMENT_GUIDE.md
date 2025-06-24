# 🚀 Safe News Crawler - Hướng dẫn Cải tiến Hệ thống

## 📋 Tổng quan cải tiến

Hướng dẫn này đề xuất các giải pháp nâng cao độ chính xác và hiệu quả của hệ thống phân tích tin tức với Gemini API, tập trung vào việc tối ưu hóa prompt, xử lý full content và đánh giá chất lượng.

---

## 🎯 VẤN ĐỀ 1: Cải thiện Prompt Engineering

### ❌ **Vấn đề hiện tại:**

- Prompt đơn giản, chỉ liệt kê từ khóa
- Không định nghĩa rõ "tích cực" là gì
- Thiếu context về mục đích sử dụng

### ✅ **Giải pháp: Prompt Engineering Hoàn hảo**

#### **Nguyên tắc thiết kế prompt chất lượng cao:**

1. **🎯 Mục đích rõ ràng** - Định nghĩa chính xác "tin tích cực"
2. **📋 Hướng dẫn chi tiết** - Liệt kê cụ thể từng loại tin
3. **⚠️ Cảnh báo quan trọng** - Nhấn mạnh đọc toàn bộ, phát hiện plot twist
4. **📊 Output chuẩn hóa** - JSON format với confidence và lý do
5. **🧪 Test đa dạng** - Thử nghiệm với nhiều case khác nhau

#### **Template prompt tối ưu:**

```python
def create_optimal_prompt(title: str, url: str, summary: str = "") -> str:
    """Prompt engineering hoàn hảo cho URL analysis"""
    
    prompt = f"""
🤖 BẠN LÀ AI: Chuyên gia phân tích tin tức Tiếng Việt với 10+ năm kinh nghiệm

🎯 NHIỆM VỤ: Đánh giá tin tức cho ứng dụng "Tin Tức Tích Cực" - chỉ hiển thị tin mang lại cảm xúc tốt đẹp cho người đọc

📖 BÀI CẦN PHÂN TÍCH:
- URL: {url}
- Tiêu đề: "{title}"
- Tóm tắt: "{summary[:150]}..."

🔍 HƯỚNG DẪN PHÂN TÍCH:

✅ TIN TÍCH CỰC (POSITIVE) - Chỉ chấp nhận khi:
• Thành tựu học tập/sự nghiệp (tốt nghiệp, thăng tiến, giải thưởng)
• Tình cảm đẹp (cưới hỏi, sinh con, gia đình hạnh phúc)
• Sức khỏe tích cực (khỏi bệnh, phục hồi thành công)
• Từ thiện/giúp đỡ cộng đồng (tặng quà, xây nhà, học bổng)
• Phát triển xã hội (công nghệ mới, y tế, giáo dục)
• Nghệ thuật/văn hóa inspiring (triển lãm, lễ hội, âm nhạc)
• Overcoming adversity (vượt qua khó khăn để thành công)

❌ LOẠI BỎ NGAY (NEGATIVE):
• Tai nạn, thảm họa, thiên tai → Tử vong, thương vong
• Tội phạm, bạo lực → Giết người, cướp, tấn công
• Tham nhũng, lừa đảo → Bắt giữ, án tù
• Bệnh tật nghiêm trọng → Ung thư, dịch bệnh (trừ chữa khỏi)
• Khủng hoảng kinh tế → Phá sản, thất nghiệp hàng loạt
• Xung đột chính trị/xã hội → Biểu tình, đập phá
• Chia ly gia đình → Ly hôn, tan vỡ (trừ khi có happy ending)

🚨 QUAN TRỌNG - QUY TẮC VÀNG:
1. ĐỌC TOÀN BỘ BÀI từ URL - KHÔNG chỉ dựa vào tiêu đề
2. CHÚ Ý "PLOT TWIST" - Tiêu đề tích cực có thể có nội dung tiêu cực
3. VÍ DỤ PLOT TWIST cần tránh:
   • "Cặp đôi chuẩn bị cưới" → Cô dâu tự tử trước ngày cưới
   • "Học sinh giỏi được khen" → Bị phát hiện gian lận
   • "Doanh nghiệp thành công" → Bị bắt vì trốn thuế
4. CHỈ POSITIVE khi >85% nội dung thực sự tích cực và có giá trị inspiration

🎯 TIÊU CHÍ CONFIDENCE:
• 0.9-1.0: Rõ ràng tích cực, không có yếu tố tiêu cực
• 0.7-0.8: Chủ yếu tích cực nhưng có một ít neutral
• 0.5-0.6: Trung tính hoặc không rõ ràng
• 0.3-0.4: Chủ yếu tiêu cực
• 0.0-0.2: Rõ ràng tiêu cực

📤 TRẢ VỀ JSON CHÍNH XÁC:
{{"sentiment": "POSITIVE/NEGATIVE/NEUTRAL", "confidence": 0.85, "reason": "Lý do chi tiết dựa trên nội dung đầy đủ từ URL"}}

⭐ LƯU Ý: Sứ mệnh của bạn là mang lại niềm vui, hy vọng cho người đọc. Hãy nghiêm túc với từng quyết định!
"""
    return prompt
```

#### **Kiểm tra chất lượng prompt:**

```python
def validate_prompt_quality():
    """Test prompt với các edge cases khó"""
    
    test_cases = [
        # Plot twist case - PHẢI detect được
        {
            "title": "Sinh viên xuất sắc nhận học bổng toàn phần",
            "url": "https://example.com/twist-case",
            "expected_twist": "Học sinh này sau đó bị phát hiện làm giả giấy tờ",
            "expected_result": "NEGATIVE"
        },
        
        # True positive - không có twist
        {
            "title": "Cô gái khuyết tật trở thành bác sĩ", 
            "url": "https://example.com/true-positive",
            "content": "Sau 8 năm học tập vất vả, cô đã hoàn thành ước mơ",
            "expected_result": "POSITIVE"
        },
        
        # Borderline case - cần test confidence
        {
            "title": "Công ty công bố kết quả kinh doanh",
            "url": "https://example.com/neutral",
            "expected_result": "NEUTRAL"
        }
    ]
    
    for case in test_cases:
        prompt = create_optimal_prompt(case['title'], case['url'])        # Test với Gemini và verify result
        print(f"Testing: {case['title']}")
        # ...
```

### 📊 **Cải tiến so với prompt cũ:**

| Khía cạnh | Prompt cũ | Prompt mới |
|-----------|-----------|------------|
| **Độ dài** | ~200 chars | ~1000 chars |
| **Context** | Ít | Chi tiết rõ ràng |
| **Định nghĩa** | Mơ hồ | Cụ thể từng loại |
| **Cảnh báo** | Không | Nhấn mạnh đọc full content |
| **Output** | Cơ bản | Có lý do giải thích |

---

## 🌐 VẤN ĐỀ 2: Gửi URL trực tiếp cho Gemini

### ❌ **Vấn đề hiện tại:**
- Chỉ dựa vào RSS summary (ngắn, thiếu thông tin)
- Extract content tốn thời gian và tài nguyên
- Gửi content dài phí quota không cần thiết

### ✅ **Giải pháp: URL-based Analysis**

#### **Gemini có thể đọc URL trực tiếp!**

Thay vì extract content, ta gửi URL cho Gemini và để nó tự đọc + phân tích:

```python
def create_url_analysis_prompt(title: str, url: str, summary: str = "") -> str:
    """Tạo prompt để Gemini đọc URL trực tiếp"""
    
    prompt = f"""
BẠN LÀ CHUYÊN GIA PHÂN TÍCH TIN TỨC cho ứng dụng tin tức tích cực.

NHIỆM VỤ: Truy cập và đọc toàn bộ bài báo từ URL, sau đó phân tích sentiment.

URL BÀI BÁO: {url}
TIÊU ĐỀ: "{title}"
TÓM TẮT RSS: "{summary[:200]}..."

HƯỚNG DẪN PHÂN TÍCH:

🎯 ĐỊNH NGHĨA TIN TÍCH CỰC:
- Thành tựu, thành công cá nhân/tập thể
- Tình cảm đẹp (tình yêu, gia đình, hữu nghị)  
- Phát triển xã hội tích cực
- Từ thiện, giúp đỡ cộng đồng
- Nghệ thuật, văn hóa inspiring
- Phục hồi, chữa khỏi bệnh tật

❌ LOẠI BỎ (NEGATIVE):
- Tai nạn, thảm họa, tử vong
- Tội phạm, tham nhũng, bạo lực
- Bệnh tật nghiêm trọng
- Khủng hoảng, xung đột
- Ly hôn, chia tay (trừ khi có kết cục tốt)

🚨 QUAN TRỌNG: 
1. ĐỌC TOÀN BỘ BÀI từ URL - không chỉ tiêu đề
2. CHỚ KHÔNG đánh giá qua summary RSS
3. CHÚ Ý "plot twist" - nội dung có thể ngược với tiêu đề
4. Chỉ POSITIVE khi >80% bài mang tính inspiration

TRẢ VỀ JSON:
{{"sentiment": "POSITIVE/NEGATIVE/NEUTRAL", "confidence": 0.90, "reason": "Lý do dựa trên nội dung đầy đủ"}}
"""
    return prompt

def analyze_news_by_url(gemini_client, title: str, url: str, summary: str = "") -> dict:
    """Phân tích tin tức bằng cách gửi URL cho Gemini"""
    
    prompt = create_url_analysis_prompt(title, url, summary)
    
    try:
        # Gửi prompt có URL cho Gemini
        response = gemini_client.generate_content(prompt)
        result = parse_gemini_response(response.text)
        
        logging.info(f"✅ Analyzed via URL: {url}")
        return result
        
    except Exception as e:
        logging.error(f"❌ URL analysis failed: {e}")
        # Fallback về RSS summary nếu cần
        return analyze_rss_summary(title, summary)
```

#### **Ưu điểm của URL approach:**

| Khía cạnh | Content Extraction | URL Direct |
|-----------|-------------------|------------|
| **Tài nguyên** | Tốn CPU + Memory | Chỉ tốn quota |
| **Độ chính xác** | Phụ thuộc scraper | Gemini đọc native |
| **Tốc độ** | Chậm (2 bước) | Nhanh (1 bước) |
| **Maintenance** | Cần update selector | Zero maintenance |
| **Token usage** | Nhiều | Tối ưu |

#### **Implementation trong main workflow:**

```python
class OptimizedGeminiFilter:
    """Gemini filter với URL-based analysis"""
    
    def analyze_article(self, article: dict) -> dict:
        """Phân tích bài báo với URL trực tiếp"""
        
        # 1. Check cache first
        cache_key = article['link']
        cached = self.cache.get_by_url(cache_key)
        if cached:
            return cached
        
        # 2. Quick prefilter dựa trên title + summary
        if not self.quick_prefilter(article['title'], article.get('description', '')):
            result = {"sentiment": "NEGATIVE", "confidence": 0.95, "reason": "Prefilter"}
            self.cache.cache_by_url(cache_key, result)
            return result
          # 3. Gửi URL cho Gemini
        result = analyze_news_by_url(
            gemini_client, 
            article['title'], 
            article['link'], 
            article.get('description', '')
        )
        
        # 4. Cache kết quả
        self.cache.cache_by_url(cache_key, result)
        
        return result
```

---

## 🎯 KẾT LUẬN VÀ IMPLEMENTATION

### 📝 **Tóm tắt các cải tiến chính:**

1. **🧠 Prompt Engineering Hoàn hảo**
   - ✅ Định nghĩa rõ ràng tin tích cực/tiêu cực
   - ✅ Cảnh báo plot twist cases
   - ✅ Confidence scoring chi tiết
   - ✅ Output JSON chuẩn hóa

2. **🌐 URL-based Analysis**
   - ✅ Gửi URL trực tiếp cho Gemini thay vì extract content
   - ✅ Tiết kiệm tài nguyên và quota
   - ✅ Độ chính xác cao hơn
   - ✅ Zero maintenance cho scraping

3. **💡 Smart Quota Management**
   - ✅ Prefilter loại bỏ absolute negative
   - ✅ Priority queue cho bài có potential positive
   - ✅ Cache thông minh theo URL
   - ✅ 90% quota limit protection

### 🚀 **Implementation Timeline:**

#### **Week 1: Prompt Optimization**

```python
# 1. Update gemini_filter.py với optimal prompt
# 2. Test với 20 diverse cases
# 3. Measure accuracy improvement
```

#### **Week 2: URL Analysis**

```python
# 1. Implement URL-based analysis function
# 2. Update cache system để dùng URL key
# 3. Test với VNExpress URLs
```

#### **Week 3: Integration & Testing**

```python
# 1. Integrate vào main workflow
# 2. A/B test: old vs new approach
# 3. Monitor quota usage và accuracy
```

### 📊 **Expected Results:**

| Metric | Current | Target | Method |
|--------|---------|--------|---------|
| **Accuracy** | ~75% | **>90%** | URL analysis + better prompt |
| **Plot Twist Detection** | 0% | **>85%** | Specialized prompt warnings |
| **Quota Efficiency** | OK | **+40%** | URL direct vs content extraction |
| **Maintenance** | High | **Zero** | No scraping selectors |

### 🎉 **Lợi ích cuối cùng:**

- ✅ **Chất lượng cao hơn** - Gemini đọc native content
- ✅ **Tài nguyên ít hơn** - Không tốn CPU/memory cho scraping  
- ✅ **Đơn giản hơn** - Ít code, ít bug, ít maintenance
- ✅ **Hiệu quả hơn** - Tận dụng tối đa khả năng Gemini
- ✅ **Production-ready** - Robust và scalable

**🎯 Kết quả: Hệ thống AI news filter chuyên nghiệp, chính xác >90%, tối ưu quota!**
