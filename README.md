# 📰 Safe News Crawler & Analyzer 🛡️

Một công cụ Python để thu thập tin tức từ các nguồn RSS của VNExpress, phân tích cảm xúc và độc tính của bài viết, sau đó lưu trữ chúng vào Firebase.

## ✨ Tính năng nổi bật

* 📰 **Thu thập RSS Feed:** Lấy tin tức từ nhiều nguồn RSS của VNExpress.
* 😊 **Phân tích Cảm xúc:** Xác định nội dung bài viết là Tích cực, Tiêu cực hay Trung tính (sử dụng model `wonrax/phobert-base-vietnamese-sentiment`).
* 🚫 **Phát hiện Độc tính:** Nhận diện nội dung bài viết có độc hại hay không (sử dụng model `naot97/vietnamese-toxicity-detection_1`).
* 🔥 **Tích hợp Firebase:** Lưu trữ các bài viết đã xử lý cùng với điểm cảm xúc và độc tính vào Firebase Realtime Database.
* ⏰ **Lập lịch Tự động:** Tự động chạy mỗi giờ để thu thập và xử lý các bài viết mới.

## 📡 Nguồn RSS (VNExpress)

* <https://vnexpress.net/rss/tin-moi-nhat.rss>
* <https://vnexpress.net/rss/tin-xem-nhieu.rss>
* <https://vnexpress.net/rss/the-gioi.rss>
* <https://vnexpress.net/rss/thoi-su.rss>
* <https://vnexpress.net/rss/kinh-doanh.rss>
* <https://vnexpress.net/rss/startup.rss>
* <https://vnexpress.net/rss/giai-tri.rss>
* <https://vnexpress.net/rss/the-thao.rss>
* <https://vnexpress.net/rss/phap-luat.rss>
* <https://vnexpress.net/rss/giao-duc.rss>
* <https://vnexpress.net/rss/suc-khoe.rss>
* <https://vnexpress.net/rss/gia-dinh.rss>
* <https://vnexpress.net/rss/du-lich.rss>
* <https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss>
* <https://vnexpress.net/rss/oto-xe-may.rss>
* <https://vnexpress.net/rss/y-kien.rss>
* <https://vnexpress.net/rss/tam-su.rss>
* <https://vnexpress.net/rss/cuoi.rss>

## 🛠️ Công nghệ sử dụng

* 🐍 Python 3.10+
* 🤖 Transformers (Hugging Face)
* 🔥 PyTorch
* ☁️ Firebase Admin SDK
* 📄 BeautifulSoup4
* 📰 Feedparser
* ⏰ Schedule

## ⚙️ Cài đặt và Thiết lập

1. **Clone repository (Tải mã nguồn):**

   ```bash
   git clone <your-repository-url>
   cd safe_news_crawlTool_RSS
   ```

2. **Môi trường Python:**

   Dự án này được cấu hình để chạy với Python 3.10. Nếu bạn sử dụng Laragon, hãy đảm bảo môi trường Python của bạn trỏ đến đúng phiên bản:
   Ví dụ: `/e/Lenovo/laragon/bin/python/python-3.10/python.exe`

3. **Cài đặt các thư viện cần thiết:**

   Bạn nên tạo một tệp `requirements.txt`. Hiện tại, bạn có thể cài đặt từng gói bằng môi trường Python đã chỉ định ở trên:

   ```bash
   # Thay thế 'python.exe' bằng đường dẫn thực thi Python 3.10 của bạn nếu khác
   /e/Lenovo/laragon/bin/python/python-3.10/python.exe -m pip install beautifulsoup4 feedparser schedule transformers torch firebase-admin
   ```

   *(Lưu ý: Việc cài đặt `torch` có thể yêu cầu các lệnh cụ thể tùy thuộc vào phiên bản CUDA của bạn nếu bạn dự định sử dụng GPU. Đối với CPU, cài đặt pip tiêu chuẩn thường là đủ.)*

4. **Thiết lập Firebase:**

   * Đặt tệp `serviceAccountKey.json` của bạn vào thư mục gốc của dự án.
   * Đảm bảo Firebase Realtime Database hoặc Firestore đã được thiết lập trong dự án Firebase của bạn.
   * **Quan trọng:** Đừng quên thêm `serviceAccountKey.json` vào tệp `.gitignore` của bạn để tránh đưa key này lên repository công khai.

## ▶️ Cách chạy dự án

Thực thi tệp `main.py` bằng trình thông dịch Python 3.10 của bạn:

```bash
/e/Lenovo/laragon/bin/python/python-3.10/python.exe main.py
```

Script sẽ khởi động, lập lịch công việc chạy hàng giờ và thực hiện lần chạy đầu tiên ngay lập tức.

## 📁 Cấu trúc thư mục dự án

```text
safe_news_crawlTool_RSS/
│
├── main.py                 # Script chính để chạy crawler và scheduler
├── README.md               # Tệp README này
├── serviceAccountKey.json  # Key của Firebase service account (❗Thêm vào .gitignore!)
├── utils/
│   ├── rss_crawler.py      # Module thu thập và phân tích RSS feeds
│   ├── news_filter.py      # Module phân tích cảm xúc và độc tính
│   └── firebase_handler.py # Module xử lý các thao tác với Firebase
└── ... (các tệp khác như .gitignore, LICENSE nếu có)
```

## 🔍 Giải thích các Module

### `main.py` 🚀

* Đây là điểm khởi đầu của ứng dụng.
* Import các module cần thiết từ thư mục `utils`.
* Định nghĩa hàm `job()` thực hiện toàn bộ quy trình:
  * Lấy danh sách các RSS feed.
  * Với mỗi feed, lấy các bài viết.
  * Với mỗi bài viết, kết hợp tiêu đề và mô tả để phân tích.
  * Gọi `analyze_sentiment` và `detect_toxicity` từ `news_filter.py`.
  * Lưu trữ kết quả vào Firebase thông qua `store_news` từ `firebase_handler.py`.
* Sử dụng thư viện `schedule` để chạy hàm `job()` mỗi giờ.
* Thực hiện một lần chạy `job()` ngay khi khởi động.
* Vòng lặp `while True` để giữ cho scheduler hoạt động.

### `utils/news_filter.py` 🧐

Module này chịu trách nhiệm phân tích cảm xúc và độc tính của văn bản tiếng Việt.

* **Chức năng cốt lõi:**
  * Sử dụng các mô hình đã được huấn luyện trước từ Hugging Face Transformers.
  * **Phân tích Cảm xúc (Sentiment Analysis):**
    * Model: `wonrax/phobert-base-vietnamese-sentiment`
    * Đầu ra: `0` (Tiêu cực - NEG), `1` (Tích cực - POS), `2` (Trung tính - NEU).
  * **Phát hiện Độc tính (Toxicity Detection):**
    * Model: `naot97/vietnamese-toxicity-detection_1`
    * Đầu ra: `True` (Độc hại), `False` (Không độc hại).
* **Quy trình hoạt động:**
  1. **Tokenization:** Văn bản đầu vào được chuyển đổi thành định dạng mà mô hình có thể hiểu (tokens).
  2. **Dự đoán (Inference):** Dữ liệu đã tokenize được đưa vào mô hình tương ứng. `torch.no_grad()` được sử dụng để tối ưu hóa bộ nhớ và tốc độ khi dự đoán.
  3. **Xử lý Kết quả:** Kết quả đầu ra của mô hình (logits) được chuyển đổi thành xác suất bằng hàm softmax. Lớp có xác suất cao nhất (cho sentiment) hoặc so sánh xác suất với ngưỡng 0.5 (cho toxicity) sẽ được trả về.

### `utils/rss_crawler.py` 📰

* Thu thập các mục tin tức từ các URL RSS VNExpress được cung cấp bằng thư viện `feedparser`.
* Làm sạch nội dung HTML từ mô tả bài viết bằng `BeautifulSoup`.
* Trích xuất thông tin liên quan: tiêu đề, liên kết, ngày xuất bản, mô tả đã làm sạch và URL hình ảnh (nếu có).
* Trả về một danh sách các dictionary, mỗi dictionary chứa thông tin của một bài viết.

### `utils/firebase_handler.py` 🔥

* Khởi tạo Firebase Admin SDK bằng tệp `serviceAccountKey.json`.
* Cung cấp hàm `store_news` để lưu trữ các bài viết đã được xử lý (bao gồm tiêu đề, liên kết, mô tả, danh mục, cảm xúc và trạng thái độc tính) vào Firebase Realtime Database dưới một key duy nhất cho mỗi bài viết (thường là ID được tạo tự động hoặc dựa trên link).

---

*README này được cập nhật lần cuối vào ngày 13 tháng 06 năm 2025.*
