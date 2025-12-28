# Detailed Logging Feature

## Mô tả

Tính năng ghi log chi tiết giúp tracking và phân tích hiệu suất của hệ thống crawl và AI analysis. Logs được lưu theo định dạng JSON để dễ dàng xử lý và cải thiện mô hình.

## Cấu trúc Log File

```json
{
  "total": 20,              // Tổng số bài báo được xử lý
  "analyzed": 20,           // Số bài báo đã phân tích
  "positive": 13,           // Số bài tích cực (sentiment = 1)
  "negative": 0,            // Số bài tiêu cực (sentiment = -1)
  "neutral": 7,             // Số bài trung tính (sentiment = 0)
  "toxic": 0,               // Số bài có nội dung độc hại
  "stored": 13,             // Số bài đã lưu vào Firebase
  "errors": 0,              // Số lỗi xảy ra
  "categories": {           // Phân bố theo category
    "giao-duc": 6,
    "suc-khoe": 2,
    "du-lich": 1
  },
  "results": [              // Chi tiết từng bài báo
    {
      "index": 1,
      "title": "Tiêu đề bài báo",
      "link": "https://...",
      "source_category": "giao-duc",
      "category": "giao-duc",
      "sentiment": 1,
      "is_toxic": false,
      "description": "Mô tả ngắn gọn..."
    }
  ],
  "timestamp": "2025-12-17T11:36:14.852314",
  "collection": "positive_news"
}
```

## Sử dụng

### 1. Chạy Test Crawl với Logging

```bash
python main.py test --save-logs
```

Logs sẽ được lưu vào: `logs_prod/crawl_result_YYYYMMDD_HHMMSS.json`

### 2. Chạy Production Crawl với Logging

```bash
python main.py production --save-logs
```

### 3. Chạy Scheduled Crawl với Logging

```bash
python main.py schedule --save-logs
```

Mỗi lần chạy (15 phút một lần) sẽ tạo một file log mới.

## Lợi ích

1. **Tracking Performance**: Theo dõi tỷ lệ thành công, phân bố sentiment
2. **Debugging**: Xem chi tiết từng bài báo được xử lý
3. **AI Improvement**: Phân tích kết quả để cải thiện prompt và model
4. **Analytics**: Thống kê category, sentiment distribution
5. **Audit Trail**: Lưu lại lịch sử crawl để review

## Tắt Logging

Chạy không có flag `--save-logs`:

```bash
python main.py production
```

## Quản lý Log Files

- Log files được lưu trong thư mục `logs_prod/`
- Mỗi file có timestamp unique trong tên file
- Nên định kỳ backup và xóa log files cũ để tiết kiệm dung lượng
- Có thể dùng log files để train/fine-tune AI models

## So sánh với Test Logs

Log structure tương thích hoàn toàn với format trong `log_test_json/`:

- Cùng schema JSON
- Cùng cách tracking sentiment/toxic
- Cùng format chi tiết từng article
- Khác: thêm `timestamp` và `collection` để phân biệt production/test runs
