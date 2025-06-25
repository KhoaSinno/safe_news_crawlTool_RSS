# 🎯 Enhanced Category Classification & JSON Response

## 🤔 **TẠI SAO PHẢI TRẢ VỀ JSON?**

### ✅ **Lý do sử dụng JSON Format:**

1. **🔧 Structured Data**: Dễ parse, validate và xử lý tự động
2. **⚡ Performance**: Faster processing, không cần regex complex
3. **🎯 Consistency**: Đảm bảo format chuẩn, tránh parsing errors
4. **📊 Rich Information**: Có thể chứa nhiều thông tin (sentiment, confidence, reason, category...)
5. **🔄 Scalability**: Dễ mở rộng thêm fields mới

### ❌ **Vấn đề với text response:**

```
"Bài này tích cực vì có nội dung về thành công" → Khó parse
"POSITIVE với confidence 0.8" → Phải regex, dễ lỗi
"Tích cực, thuộc danh mục giáo dục" → Không chuẩn hóa
```

## 🎯 **ENHANCED CATEGORY CLASSIFICATION**

### **📂 Danh mục bài báo có thể phân loại:**

- 🏠 **FAMILY**: Gia đình, hôn nhân, nuôi dạy con
- 💻 **TECHNOLOGY**: Công nghệ, AI, internet, gaming  
- 🎓 **EDUCATION**: Giáo dục, học tập, nghiên cứu
- 🏛️ **SOCIETY**: Xã hội, chính trị, pháp luật
- 🏥 **HEALTH**: Y tế, sức khỏe, làm đẹp
- 💰 **BUSINESS**: Kinh doanh, tài chính, bất động sản
- 🎨 **CULTURE**: Văn hóa, nghệ thuật, giải trí
- ⚽ **SPORTS**: Thể thao, Olympic, giải đấu
- 🌍 **ENVIRONMENT**: Môi trường, khí hậu, thiên nhiên
- ✈️ **TRAVEL**: Du lịch, khám phá, ẩm thực

### **🎯 Enhanced JSON Response Structure:**

```json
{
  "sentiment": "POSITIVE/NEGATIVE/NEUTRAL",
  "confidence": 0.92,
  "category": "FAMILY/TECHNOLOGY/EDUCATION/...",
  "subcategory": "marriage/startup/scholarship/...",
  "audience_suitability": ["KIDS_SAFE", "FAMILY_FRIENDLY"],
  "emotional_impact": "inspiring/uplifting/educational",
  "reason": "Chi tiết phân tích dựa trên full content",
  "plot_twist_detected": false,
  "keywords": ["cưới", "hạnh phúc", "tình yêu"]
}
```

### **🔥 Enhanced Prompt Template:**

```python
def create_enhanced_category_prompt(title: str, url: str, summary: str = "") -> str:
    """Enhanced prompt với category classification"""
    
    prompt = f"""
🤖 CHUYÊN GIA PHÂN TÍCH & PHÂN LOẠI TIN TỨC

🎯 NHIỆM VỤ: 
1. Phân tích cảm xúc tin tức
2. Phân loại chính xác theo danh mục  
3. Đánh giá tính phù hợp với đối tượng

📰 BÀI BÁO: {url}
📌 Tiêu đề: "{title}"

📂 DANH MỤC & TIÊU CHÍ TÍCH CỰC:

🏠 FAMILY POSITIVE:
• Đám cưới đẹp, tình yêu chân thành
• Sinh con, nuôi dạy con thành công
• Gia đình sum họp, vượt qua khó khăn

💻 TECHNOLOGY POSITIVE:  
• Breakthrough innovations giúp đỡ con người
• Startups thành công, tech for good
• Vietnam tech achievements globally

🎓 EDUCATION POSITIVE:
• Thành tích học tập, học bổng
• Phương pháp giảng dạy sáng tạo
• Học sinh giúp cộng đồng

🏥 HEALTH POSITIVE:
• Đột phá y tế, phát hiện thuốc chữa bệnh
• Câu chuyện hồi phục, điều trị thành công
• Lối sống healthy transformation

⚠️ PLOT TWIST THEO DANH MỤC:
• FAMILY: "Thông báo cưới" → Scandal phanh phui
• BUSINESS: "Công ty thành công" → Điều tra gian lận
• EDUCATION: "Học sinh xuất sắc" → Phát hiện gian lận

🎯 AUDIENCE SUITABILITY:
• KIDS_SAFE: Phù hợp trẻ em
• TEEN_SAFE: Phù hợp teen
• FAMILY_FRIENDLY: Toàn gia đình
• ADULT_GENERAL: Người lớn

📤 TRẢ VỀ JSON CHÍNH XÁC theo cấu trúc trên.

🔍 HƯỚNG DẪN:
1. Đọc TOÀN BỘ bài từ URL
2. Xác định danh mục chính xác  
3. Phát hiện plot twist
4. Đánh giá audience suitability
5. CHỈ POSITIVE khi thực sự inspiring
"""
    return prompt
```

### **📊 Ví dụ phân loại chính xác:**

#### **FAMILY Category:**

```json
{
    "sentiment": "POSITIVE",
    "confidence": 0.92,
    "category": "FAMILY",
    "subcategory": "marriage",
    "audience_suitability": ["TEEN_SAFE", "FAMILY_FRIENDLY"],
    "emotional_impact": "inspiring",
    "reason": "Câu chuyện tình yêu đẹp, vượt khó khăn",
    "plot_twist_detected": false,
    "keywords": ["cưới", "tình yêu", "hạnh phúc"]
}
```

#### **TECHNOLOGY Category:**

```json
{
    "sentiment": "POSITIVE", 
    "confidence": 0.88,
    "category": "TECHNOLOGY",
    "subcategory": "ai_for_good",
    "audience_suitability": ["ADULT_GENERAL", "TEEN_SAFE"],
    "emotional_impact": "educational",
    "reason": "AI giúp chẩn đoán bệnh hiếm, cứu người",
    "plot_twist_detected": false,
    "keywords": ["AI", "y tế", "cứu người"]
}
```

#### **EDUCATION với Plot Twist:**

```json
{
    "sentiment": "NEGATIVE",
    "confidence": 0.95,
    "category": "EDUCATION", 
    "subcategory": "academic_scandal",
    "audience_suitability": [],
    "emotional_impact": "disappointing",
    "reason": "Tiêu đề nói thành tích, nhưng phát hiện gian lận",
    "plot_twist_detected": true,
    "keywords": ["gian lận", "thi cử", "scandal"]
}
```

## 🤔 **TẠI SAO PHẢI CÓ CONFIDENCE SCORE?**

### 🎯 **Lý do quan trọng của Confidence:**

#### **1. 🚦 Quality Control & Filtering**

```python
# Chỉ lưu articles với confidence cao
def should_store_article(analysis_result):
    if analysis_result['sentiment'] == 'POSITIVE':
        if analysis_result['confidence'] >= 0.8:
            return True  # High quality positive news
        elif analysis_result['confidence'] >= 0.6:
            return "MANUAL_REVIEW"  # Cần review thủ công
        else:
            return False  # Quá thấp, không lưu
    return False

# Ví dụ thực tế:
article_1 = {"sentiment": "POSITIVE", "confidence": 0.95}  # ✅ Lưu ngay
article_2 = {"sentiment": "POSITIVE", "confidence": 0.65}  # ⚠️ Cần review 
article_3 = {"sentiment": "POSITIVE", "confidence": 0.45}  # ❌ Không lưu
```

#### **2. 📊 Risk Assessment & False Positive Prevention**

```python
# Confidence giúp phát hiện edge cases
def analyze_confidence_patterns():
    """
    LOW CONFIDENCE (0.3-0.6) thường có nghĩa:
    - Ambiguous content (không rõ tích cực hay tiêu cực)
    - Mixed signals (có cả positive và negative elements)
    - Plot twist potential (tiêu đề vs nội dung khác nhau)
    - Context-dependent (phụ thuộc quan điểm cá nhân)
    """
    
    # Ví dụ LOW confidence cases:
    low_confidence_examples = [
        {
            "title": "Công ty công bố kết quả kinh doanh Q4",
            "content": "Doanh thu tăng 10% nhưng lợi nhuận giảm 5%",
            "confidence": 0.4,  # Mixed signals
            "reason": "Có cả tin tốt và xấu, khó xác định overall sentiment"
        },
        {
            "title": "Sinh viên nhận học bổng du học",
            "content": "Nhưng phải vay thêm 50% chi phí, gia đình khó khăn",
            "confidence": 0.5,  # Achievement nhưng có burden
            "reason": "Thành tích tích cực nhưng có financial stress"
        }
    ]
```

#### **3. 🎯 Dynamic Threshold Management**

```python
class ConfidenceBasedProcessor:
    """Xử lý dựa trên confidence levels"""
```

## 🌐 **URL-BASED ANALYSIS: GEMINI CÓ THỂ ĐỌC URL HIỆU QUẢ KHÔNG?**

### 🎯 **Khả năng Web Browsing của Gemini 2.0 Flash:**

#### **✅ Ưu điểm của URL-based approach:**

```python
def analyze_with_url_only(title, url):
    """Chỉ gửi URL cho Gemini, không gửi content"""
    
    prompt = f"""
🤖 Hãy truy cập và đọc toàn bộ bài báo tại URL: {url}

📌 Tiêu đề: "{title}"

🎯 NHIỆM VỤ:
1. Truy cập URL và đọc TOÀN BỘ nội dung bài báo
2. Phân tích sentiment dựa trên full content (không chỉ title)
3. Phát hiện plot twist (title vs content contradiction)
4. Đánh giá độ tích cực thực sự của bài báo

⚠️ QUAN TRỌNG: 
- PHẢI đọc full article, không chỉ dựa vào title
- Chú ý plot twist: title tích cực nhưng content tiêu cực
- CHỈ POSITIVE khi >90% content thực sự tích cực

📤 JSON Response:
{{"sentiment": "POSITIVE/NEGATIVE/NEUTRAL", "confidence": 0.XX, "reason": "Dựa trên full content analysis"}}
"""
    
    # Gửi cho Gemini - chỉ tốn 1 API call
    return gemini_client.generate_content(prompt)
```

#### **🚀 Quota Efficiency Analysis:**

| Approach | Token Usage | API Calls | Quota Efficiency | Accuracy |
|----------|-------------|-----------|------------------|----------|
| **URL-only** | ~150 tokens | 1 call | ⭐⭐⭐⭐⭐ Tối ưu | 85-90% |
| **Content + URL** | ~800-1500 tokens | 1 call | ⭐⭐⭐ Vừa phải | 90-95% |
| **Pre-scraping** | ~1000 tokens | 1 call + scraping | ⭐⭐ Kém | 88-92% |

### 📊 **Thực tế về Gemini URL Reading:**

#### **✅ HOẠT ĐỘNG TỐT KHI:**

```python
# Test cases cho URL-based analysis
url_test_cases = [
    {
        "type": "VNExpress Standard Article",
        "url": "https://vnexpress.net/giao-duc/...",
        "success_rate": "90-95%",
        "notes": "Clean HTML, good structure"
    },
    {
        "type": "Simple News Sites", 
        "url": "https://tuoitre.vn/...",
        "success_rate": "85-90%",
        "notes": "Standard news format"
    },
    {
        "type": "Blog Posts",
        "url": "https://medium.com/...",
        "success_rate": "80-85%", 
        "notes": "Good content structure"
    }
]

def test_url_reading_capability():
    """Test thực tế khả năng đọc URL của Gemini"""
    
    success_patterns = [
        "✅ Standard news websites (VNExpress, Tuoitre, etc.)",
        "✅ Blog platforms (Medium, WordPress)", 
        "✅ Government websites (.gov.vn)",
        "✅ University websites (.edu.vn)",
        "✅ Clean HTML structure sites"
    ]
    
    challenge_patterns = [
        "⚠️ Heavy JavaScript sites (SPA)",
        "⚠️ Paywall protected content", 
        "⚠️ Login required pages",
        "⚠️ Sites with complex anti-bot measures",
        "⚠️ Very image-heavy articles"
    ]
    
    return success_patterns, challenge_patterns
```

#### **❌ CÓ THỂ GẶP KHÓ KHĂN KHI:**

```python
def identify_problematic_urls():
    """Các loại URL có thể gây khó khăn"""
    
    problematic_cases = {
        "paywall_sites": [
            "Wall Street Journal", "New York Times premium"
        ],
        "javascript_heavy": [
            "Single Page Applications", "React/Vue heavy sites"
        ],
        "anti_bot_protection": [
            "Cloudflare protected", "CAPTCHA required"
        ],
        "dynamic_content": [
            "Comments section", "Live updating content"
        ],
        "multimedia_heavy": [
            "Video-first articles", "Interactive graphics"
        ]
    }
    
    # Cách handle:
    fallback_strategies = {
        "retry_mechanism": "3 attempts với delay",
        "content_extraction": "Fallback to RSS summary",
        "user_agent_rotation": "Simulate different browsers",
        "cache_strategy": "Cache successful reads"
    }
    
    return problematic_cases, fallback_strategies
```

### 🔥 **Optimized URL-Based Workflow:**

```python
class OptimizedURLAnalyzer:
    """Tối ưu hóa URL-based analysis"""
    
    def __init__(self):
        self.success_cache = {}  # Cache sites that work well
        self.failure_cache = {}  # Cache problematic sites
        self.quota_tracker = QuotaTracker()
    
    def analyze_url_efficiently(self, title, url, summary=""):
        """Phân tích URL với optimization tối đa"""
        
        # 1. Quick domain check
        domain = self.extract_domain(url)
        
        if domain in self.failure_cache:
            # Skip domains that consistently fail
            return self.fallback_to_summary_analysis(title, summary)
        
        # 2. Try URL-based analysis
        try:
            result = self.gemini_url_analysis(title, url)
            
            # Track success
            self.success_cache[domain] = self.success_cache.get(domain, 0) + 1
            self.quota_tracker.log_success()
            
            return result
            
        except Exception as e:
            # Handle failure
            self.failure_cache[domain] = self.failure_cache.get(domain, 0) + 1
            
            if self.failure_cache[domain] >= 3:
                # Domain consistently fails, fallback
                return self.fallback_to_summary_analysis(title, summary)
            else:
                # Retry once
                return self.retry_with_different_approach(title, url, summary)
    
    def gemini_url_analysis(self, title, url):
        """Core Gemini URL analysis với optimized prompt"""
        
        # Shorter, more efficient prompt
        prompt = f"""
Đọc bài: {url}
Tiêu đề: "{title}"

Phân tích sentiment dựa trên TOÀN BỘ nội dung. 
Chú ý plot twist (title vs content khác nhau).
CHỈ POSITIVE khi content thực sự tích cực.

JSON: {{"sentiment": "POSITIVE/NEGATIVE/NEUTRAL", "confidence": 0.XX, "reason": "..."}}
"""
        
        response = gemini_client.generate_content(
            prompt,
            generation_config={
                'temperature': 0.1,
                'max_output_tokens': 100,  # Giảm token để save quota
                'top_p': 0.8
            }
        )
        
        return self.parse_response(response.text)
    
    def fallback_to_summary_analysis(self, title, summary):
        """Fallback khi URL reading fail"""
        
        # Simplified analysis based on title + summary only
        prompt = f"""
Phân tích sentiment dựa trên:
Tiêu đề: "{title}"
Tóm tắt: "{summary}"

⚠️ LƯU Ý: Không có full content, chỉ dựa trên summary.
Confidence sẽ thấp hơn do thiếu thông tin.

JSON: {{"sentiment": "NEUTRAL", "confidence": 0.4, "reason": "Limited to summary only"}}
"""
        
        return gemini_client.generate_content(prompt)

class QuotaTracker:
    """Track quota usage cho URL-based analysis"""
    
    def __init__(self):
        self.daily_quota = 1500
        self.used_quota = 0
        self.success_rate = 0
        self.url_success_count = 0
        self.total_attempts = 0
    
    def log_success(self):
        self.used_quota += 1
        self.url_success_count += 1
        self.total_attempts += 1
        self.success_rate = self.url_success_count / self.total_attempts
    
    def log_failure(self):
        self.used_quota += 1  # Still costs quota even on failure
        self.total_attempts += 1
        self.success_rate = self.url_success_count / self.total_attempts
    
    def get_quota_stats(self):
        return {
            'used': self.used_quota,
            'remaining': self.daily_quota - self.used_quota,
            'success_rate': self.success_rate,
            'efficiency': f"{(self.success_rate * 100):.1f}% URL reading success"
        }
```
