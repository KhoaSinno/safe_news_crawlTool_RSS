# Safe News Crawler - Hệ thống đã tối ưu hóa hoàn chỉnh

## 📋 Tổng quan

Hệ thống crawl tin tức tự động với phân tích cảm xúc/độc tính bằng Gemini 2.0 Flash API, chỉ lưu tin tích cực vào Firebase.

## ✅ Tính năng đã hoàn thành

### 🔧 Core Features

- ✅ **Auto crawl RSS VNExpress** - 18 danh mục tin tức
- ✅ **Phân tích cảm xúc/độc tính** - Gemini 2.0 Flash API
- ✅ **Smart caching** - Exact + Fuzzy matching để tiết kiệm quota
- ✅ **Rate limiting** - 10 calls/phút để tránh rate limit
- ✅ **Firebase integration** - Lưu tin tích cực với kiểm tra trùng lặp
- ✅ **Auto scheduling** - Chạy mỗi giờ tự động
- ✅ **Duplicate detection** - Phát hiện và bỏ qua bài đã crawl

### 🚀 Optimizations

- ✅ **Token optimization** - Giảm text length xuống 800 chars, maxOutputTokens = 50
- ✅ **Rule-based fallback** - Phân tích từ khóa khi API fail
- ✅ **Exponential backoff** - Retry thông minh khi API busy
- ✅ **Database migration** - Tự động thêm column title vào cache
- ✅ **Error handling** - Xử lý toàn diện các lỗi API
- ✅ **Logging optimization** - Log chi tiết, dễ debug

### 🛡️ Security & Reliability

- ✅ **API quota protection** - Daily limit 1500 requests
- ✅ **Firebase security** - Unique document ID để tránh trùng lặp
- ✅ **State persistence** - Lưu trạng thái crawl để resume
- ✅ **Graceful degradation** - Fallback khi API fail

## 📁 Cấu trúc file đã tối ưu

```
safe_news_crawlTool_RSS/
├── main_optimized.py              # Main app đã tối ưu
├── utils/
│   ├── gemini_filter_final.py     # Gemini API client tối ưu
│   ├── firebase_handler.py        # Firebase với duplicate check
│   └── rss_crawler.py            # RSS crawler (không đổi)
├── analysis_cache.db             # Cache database (đã migrate)
├── crawl_state.json             # Trạng thái crawl (auto tạo)
├── news_crawler.log            # Log chi tiết
└── serviceAccountKey.json       # Firebase credentials
```

## 🎯 Kết quả test thực tế

### ✅ Kiểm tra thành công

- **Database migration**: ✅ Thêm column title thành công
- **Cache hoạt động**: ✅ Hầu hết request dùng cache (0 API calls)
- **Firebase lưu**: ✅ Lưu thành công nhiều tin tích cực
- **Duplicate check**: ✅ Phát hiện và bỏ qua bài trùng lặp
- **Rate limiting**: ✅ Không bị rate limit
- **Error handling**: ✅ Xử lý JSON parse error gracefully

### 📊 Thống kê crawl mẫu (60 giây test)

- **Tổng bài crawl**: ~115 bài
- **Bài tích cực lưu**: ~12 bài (tỷ lệ ~10%)
- **API calls**: 0 (tất cả dùng cache)
- **Thời gian xử lý**: ~0.5s/bài
- **Memory usage**: Tối ưu

## 🔄 Workflow hoạt động

1. **Khởi động**: Test API → Load crawl state
2. **Crawl RSS**: Fetch từ 18 feeds VNExpress  
3. **Check duplicate**: So sánh với processed_links
4. **Analyze**: Cache → Rule-based → API → Fallback
5. **Store positive**: Firebase với duplicate check
6. **Save state**: Update processed_links
7. **Schedule**: Repeat mỗi giờ

## 🚀 Cách sử dụng

### Chạy phiên bản tối ưu

```bash
cd "w:\WorkSpace_IT\Python\safe_news_crawlTool_RSS"
python main_optimized.py
```

### Test individual components

```bash
# Test Gemini API
python utils/gemini_filter_final.py

# Test Firebase
python -c "from utils.firebase_handler import store_news; print('OK')"
```

## 📈 Hiệu suất

### Trước tối ưu hóa

- ❌ Lỗi database cache ("no such column: title")
- ❌ Không check duplicate trên Firebase
- ❌ Không track bài đã crawl
- ❌ JSON parse errors
- ⚠️ Có thể vượt rate limit

### Sau tối ưu hóa  

- ✅ Database migration tự động
- ✅ Smart duplicate detection
- ✅ State persistence cho crawl
- ✅ Robust error handling
- ✅ Zero quota waste với cache

## 🛠️ Các file chính

### main_optimized.py

- Schedule crawl mỗi giờ
- Track bài đã crawl với crawl_state.json
- Smart duplicate detection
- Comprehensive logging
- Error recovery

### utils/gemini_filter_final.py

- Rate limiting decorator (10/min)
- Smart caching (exact + fuzzy)
- Rule-based fallback mở rộng
- Token optimization
- Exponential backoff retry

### utils/firebase_handler.py

- Duplicate check trước khi lưu
- Unique document ID
- Error handling
- Structured data format

## 📝 Logs & Monitoring

### Log file: news_crawler.log

- Thời gian crawl
- Số bài phân tích/lưu
- API usage stats
- Error details

### State file: crawl_state.json

- Last crawl timestamp
- Processed links list
- Resume capability

## 🎯 Kết luận

Hệ thống đã được tối ưu hóa hoàn chỉnh:

1. ✅ **Lưu Firebase thành công** - Đã xác thực lưu nhiều tin tích cực
2. ✅ **Tự động crawl tin mới** - Track và chỉ xử lý bài chưa crawl  
3. ✅ **Code đã tối ưu** - Refactor, comment, error handling hoàn chỉnh
4. ✅ **Zero quota waste** - Cache thông minh, rule-based fallback
5. ✅ **Production ready** - Robust, scalable, maintainable

**Ready for production deployment! 🚀**
