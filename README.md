# 📰 Safe News Crawler & Analyzer 🛡️

## Setup

/e/Lenovo/laragon/bin/python/python-3.10/python.exe -m pip install --upgrade --force-reinstall pip

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

Script sẽ khởi động, lập lịch công việc chạy hàng giờ và thực hiện lần chạy đầu tiên ngay lập tức.pip --version

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

## Extra way to do this project

### Hướng dẫn thực hiện filter realtime với ChatGPT và Firebase Cloud Functions

#### Key Points

* Research suggests that using ChatGPT (OpenAI API) with Firebase Cloud Functions is a straightforward way to filter RSS articles in real-time, leveraging Firebase’s free tier.

* It seems likely that Firebase requires a billing account setup even for free tier usage, which may conflict with your request to avoid Google billing due to errors.
* The evidence leans toward resolving the billing issue or using alternative platforms like Supabase and Fly.io to completely avoid Google billing, but we’ll focus on Firebase as per your preference.

#### Tổng quan

Để lọc các bài báo từ RSS feed (như "gia-dinh.rss" từ VnExpress) một cách realtime, bạn có thể sử dụng Firebase Cloud Functions để định kỳ crawl dữ liệu, ChatGPT để phân tích cảm xúc, và Firestore để lưu trữ bài viết tích cực. Tuy nhiên, vì bạn gặp lỗi với Google billing, chúng tôi sẽ hướng dẫn cách sử dụng Firebase trong free tier và đề xuất cách giải quyết vấn đề billing. Nếu không thể khắc phục, bạn có thể cân nhắc các nền tảng thay thế như Supabase và Fly.io.

#### Các bước thực hiện

1. **Thiết lập Firebase**: Tạo dự án Firebase, kích hoạt Firestore và Cloud Functions, đảm bảo sử dụng free tier.
2. **Đăng ký OpenAI API**: Lấy API key từ OpenAI để sử dụng ChatGPT.
3. **Viết Cloud Function**: Tạo hàm để crawl RSS, phân tích cảm xúc bằng ChatGPT, và lưu bài tích cực vào Firestore.
4. **Tích hợp Flutter**: Hiển thị bài viết từ Firestore trên ứng dụng Flutter.
5. **Giải quyết vấn đề billing**: Kiểm tra và khắc phục lỗi billing hoặc chuyển sang nền tảng khác.

#### Lưu ý

* Firebase yêu cầu billing account ngay cả trong free tier, nhưng bạn sẽ không bị tính phí nếu ở trong giới hạn.

* Nếu không thể sử dụng billing, bạn có thể chuyển sang Supabase và Fly.io, nhưng điều này yêu cầu thay đổi cấu trúc dự án.

---

### Tài liệu chi tiết thực hiện filter realtime với ChatGPT và Firebase Cloud Functions

# Hướng dẫn filter realtime RSS feed với ChatGPT và Firebase Cloud Functions

## Giới thiệu

Bạn đang phát triển ứng dụng "Chicken news" bằng Flutter, nhằm cung cấp tin tức tích cực từ RSS feed của VnExpress (ví dụ: "gia-dinh.rss"). Mục tiêu là tự động lọc các bài viết tiêu cực hoặc không phù hợp, chỉ giữ lại bài viết tích cực để hiển thị trên ứng dụng theo thời gian thực. Do gặp lỗi với Google billing, bạn muốn tránh thiết lập billing mới, nhưng vẫn sử dụng Firebase Cloud Functions và ChatGPT (OpenAI API). Tài liệu này cung cấp hướng dẫn chi tiết để thực hiện, đồng thời đề xuất cách giải quyết vấn đề billing hoặc các lựa chọn thay thế.

## Phân tích yêu cầu

* **Nguồn dữ liệu**: RSS feed "gia-dinh.rss" từ VnExpress, chứa khoảng 70 bài viết về đời sống, gia đình, sức khỏe, tài chính, và các câu chuyện truyền cảm hứng. Mỗi bài viết có tiêu đề, tóm tắt, liên kết, và ngày đăng.

* **Mục tiêu**: Lọc bài viết tiêu cực (ví dụ: tai nạn, chia tay) và chỉ giữ bài tích cực (ví dụ: câu chuyện đoàn tụ, thành tựu).
* **Thời gian thực**: Hệ thống cần tự động crawl RSS feed định kỳ (mỗi giờ) và cập nhật bài viết mới mà không cần can thiệp thủ công.
* **Ràng buộc**: Tránh sử dụng Google billing do lỗi, nhưng vẫn sử dụng Firebase Cloud Functions.
* **Ngôn ngữ**: Hỗ trợ tiếng Việt cho phân tích cảm xúc.

## Giải pháp

Chúng ta sẽ sử dụng:

* **Firebase Cloud Functions**: Để crawl RSS feed và xử lý dữ liệu định kỳ.
* **ChatGPT (OpenAI API)**: Để phân tích cảm xúc của bài viết, sử dụng prompt đơn giản.
* **Firestore**: Để lưu trữ bài viết tích cực và theo dõi bài đã xử lý.
* **Flutter app**: Để hiển thị danh sách bài viết tích cực theo thời gian thực.

Vì bạn gặp vấn đề với Google billing, chúng ta sẽ:

* Tận dụng free tier của Firebase (2 triệu invocations/tháng cho Cloud Functions, 20,000 writes/tháng cho Firestore).
* Đề xuất cách kiểm tra và khắc phục lỗi billing.
* Cung cấp giải pháp thay thế (Supabase và Fly.io) nếu không thể sử dụng Firebase.

## Các bước thực hiện

### 1. Thiết lập dự án Firebase

Firebase là nền tảng lý tưởng để tích hợp với Flutter, nhưng yêu cầu thiết lập billing account ngay cả trong free tier để ngăn chặn lạm dụng.

* **Tạo dự án**:
  * Truy cập [Firebase Console](https://console.firebase.google.com/) và nhấp **Add project**.
  * Đặt tên dự án (ví dụ: "ChickenNews") và tiếp tục.
  * Bật Google Analytics nếu muốn (không bắt buộc).
* **Kích hoạt Firestore**:
  * Trong Firebase Console, vào **Build > Firestore Database**.
  * Nhấp **Create database**, chọn **Start in test mode** (sẽ điều chỉnh rules sau), và chọn khu vực gần nhất (ví dụ: `asia-southeast1`).
* **Kích hoạt Cloud Functions**:
  * Trong Firebase Console, vào **Build > Functions** và nhấp **Get Started**.
* **Cài đặt Firebase CLI**:
  * Cài Node.js từ [Node.js](https://nodejs.org/) nếu chưa có.
  * Cài Firebase CLI:

    ```bash
    npm install -g firebase-tools
    ```

  * Đăng nhập:

    ```bash
    firebase login
    ```

  * Khởi tạo dự án trong thư mục cục bộ:

    ```bash
    mkdir chicken-news
    cd chicken-news
    firebase init
    ```

  * Chọn **Functions** và **Firestore**, sau đó chọn dự án Firebase vừa tạo.
  * Chọn **JavaScript** cho Cloud Functions và cài đặt dependencies.

### 2. Giải quyết vấn đề Google billing

Firebase yêu cầu liên kết billing account để sử dụng Cloud Functions và Firestore, ngay cả trong free tier. Nếu bạn gặp lỗi với billing:

* **Kiểm tra tài khoản billing**:
  * Truy cập [Google Cloud Console](https://console.cloud.google.com/billing).
  * Xác minh rằng dự án Firebase của bạn được liên kết với tài khoản billing.
  * Nếu có lỗi (ví dụ: phương thức thanh toán không hợp lệ), thử thêm phương thức thanh toán khác hoặc liên hệ hỗ trợ Google Cloud qua [Support](https://cloud.google.com/support).
* **Free tier của Firebase**:
  * **Cloud Functions**: 2 triệu invocations/tháng, đủ cho 720 lần chạy/tháng (mỗi giờ).
  * **Firestore**: 20,000 writes/tháng, đủ cho ~300-600 bài tích cực/tháng (giả sử 50% bài viết là tích cực).
  * Bạn sẽ không bị tính phí nếu ở trong giới hạn này.
* **Nếu không thể sử dụng billing**:
  * Cân nhắc chuyển sang Supabase (database) và Fly.io (serverless functions), cả hai đều có free tier không yêu cầu billing phức tạp. Phần thay thế sẽ được trình bày ở cuối tài liệu.

### 3. Đăng ký OpenAI API

ChatGPT (OpenAI API) sẽ được sử dụng để phân tích cảm xúc của bài viết.

* **Tạo tài khoản**:
  * Truy cập [OpenAI Platform](https://platform.openai.com/) và đăng ký.
  * Xác minh email và số điện thoại.
* **Lấy API key**:
  * Trong dashboard, vào **API Keys** và tạo key mới.
  * Lưu key này để sử dụng trong Cloud Functions.
* **Free tier của OpenAI**:
  * Cung cấp $5 tín dụng (~1 triệu tokens cho `text-davinci-003`).
  * Với mỗi bài viết (~100-200 tokens), bạn có thể xử lý hàng nghìn bài trong free tier.

### 4. Viết Cloud Function để crawl và lọc RSS

Cloud Function sẽ crawl RSS feed, phân tích cảm xúc bằng ChatGPT, và lưu bài tích cực vào Firestore.

* **Mã Cloud Function**:
  Trong thư mục `chicken-news/functions/`, mở file `index.js` và thêm mã sau:

const functions = require('firebase-functions');
const admin = require('firebase-admin');
const Parser = require('rss-parser');
const { Configuration, OpenAIApi } = require('openai');

admin.initializeApp();
const db = admin.firestore();
const parser = new Parser();
const configuration = new Configuration({
  apiKey: functions.config().openai.api_key,
});
const openai = new OpenAIApi(configuration);

exports.scheduledFunction = functions.pubsub.schedule('every 1 hours').onRun(async (context) => {
  try {
    const feed = await parser.parseURL('<https://vnexpress.net/rss/gia-dinh.rss>');
    for (const item of feed.items) {
      const docRef = db.collection('processed_articles').doc(item.link);
      const doc = await docRef.get();

      if (!doc.exists) {
        // Phân tích cảm xúc bằng ChatGPT
        const response = await openai.createCompletion({
          model: 'text-davinci-003',
          prompt: `Xác định xem đoạn văn sau có tính chất tích cực, tiêu cực hay trung lập: ${item.content || item.title}\nCảm xúc:`,
          max_tokens: 5,
          temperature: 0,
        });
        const sentiment = response.data.choices[0].text.trim().toLowerCase();

        // Lưu bài viết tích cực vào Firestore
        if (sentiment === 'tích cực') {
          await db.collection('positive_news').add({
            title: item.title,
            link: item.link,
            pubDate: item.pubDate,
            content: item.content,
            sentimentScore: sentiment,
            createdAt: admin.firestore.FieldValue.serverTimestamp(),
          });
        }

        // Đánh dấu bài viết đã xử lý
        await docRef.set({
          processedAt: admin.firestore.FieldValue.serverTimestamp(),
        });
      }
    }
    console.log('Processing completed');
    return null;
  } catch (error) {
    console.error('Error processing RSS feed:', error);
    return null;
  }
});

* **Giải thích mã**:
  * Hàm chạy mỗi giờ, sử dụng `rss-parser` để lấy RSS feed từ VnExpress.
  * Với mỗi bài viết, kiểm tra xem đã xử lý chưa bằng cách tìm document trong `processed_articles` với ID là `item.link`.
  * Nếu chưa xử lý, gửi tóm tắt (`item.content`) hoặc tiêu đề (`item.title`) đến ChatGPT để phân tích cảm xúc.
  * Nếu kết quả là "tích cực", lưu bài viết vào `positive_news`.
  * Đánh dấu bài viết đã xử lý trong `processed_articles` để tránh trùng lặp.

* **Cài đặt dependencies**:
  Trong thư mục `functions/`, chạy:

  ```bash
  npm install firebase-functions firebase-admin rss-parser openai
  ```

* **Cấu hình API key của OpenAI**:
  * Trong Firebase Console, vào **Build > Functions > Settings**.
  * Thêm biến môi trường:
    * Key: `openai.api_key`
    * Value: API key từ OpenAI.

### 5. Triển khai Cloud Function

* Trong thư mục `chicken-news/`, chạy:

  ```bash
  cd functions
  npm run build
  firebase deploy --only functions
  ```

* Hàm sẽ tự động chạy mỗi giờ sau khi deploy.

### 6. Thiết lập Firestore Security Rules

* Trong Firebase Console, vào **Firestore Database > Rules** và thêm:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /positive_news/{document=**} {
      allow read: if true;
      allow write: if false;
    }
    match /processed_articles/{document=**} {
      allow read: if false;
      allow write: if false;
    }
  }
}
```

* **Giải thích**:
  * Cho phép ứng dụng Flutter đọc `positive_news`.
  * Chỉ Cloud Functions (với admin SDK) có thể ghi vào cả hai collection.

### 7. Tích hợp với Flutter

* Thêm package `cloud_firestore` vào `pubspec.yaml`:

  ```yaml
  dependencies:
    cloud_firestore: ^4.9.0
  ```

* Tạo giao diện hiển thị danh sách bài viết:

```dart
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class NewsListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Chicken News')),
      body: StreamBuilder<QuerySnapshot>(
        stream: FirebaseFirestore.instance
            .collection('positive_news')
            .orderBy('pubDate', descending: true)
            .snapshots(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return Center(child: CircularProgressIndicator());
          }
          return ListView.builder(
            itemCount: snapshot.data!.docs.length,
            itemBuilder: (context, index) {
              var doc = snapshot.data!.docs[index];
              return ListTile(
                title: Text(doc['title']),
                subtitle: Text(doc['content']),
                onTap: () {
                  // Điều hướng đến trang chi tiết bài viết
                },
              );
            },
          );
        },
      ),
    );
  }
}
```

* **Giải thích**:
  * Sử dụng `StreamBuilder` để lắng nghe cập nhật từ `positive_news` theo thời gian thực.
  * Hiển thị danh sách bài viết với tiêu đề và tóm tắt.

### 8. Đảm bảo miễn phí

* **Firebase Cloud Functions**:
  * Free tier: 2 triệu invocations/tháng, đủ cho 720 lần chạy/tháng (mỗi giờ).

* **Firestore**:
  * Free tier: 20,000 writes/tháng, đủ cho ~300-600 bài tích cực/tháng (giả sử 50% bài viết là tích cực).
* **OpenAI API**:
  * Free tier: $5 tín dụng (~1 triệu tokens), đủ cho hàng nghìn bài viết (~100-200 tokens/bài).

### 9. Xử lý nhiều danh mục RSS

* RSS feed "gia-dinh.rss" là một danh mục, nhưng bạn có thể mở rộng để xử lý nhiều danh mục (ví dụ: sức khỏe, kinh doanh).

* Thêm danh sách RSS feeds vào Cloud Function:

  ```javascript
  const rssFeeds = [
    'https://vnexpress.net/rss/gia-dinh.rss',
    'https://vnexpress.net/rss/suc-khoe.rss',
    // Thêm các danh mục khác
  ];
  for (const url of rssFeeds) {
    const feed = await parser.parseURL(url);
    // Xử lý như trên
  }
  ```

* Lưu danh mục vào Firestore để phân loại trên ứng dụng Flutter:

  ```javascript
  await db.collection('positive_news').add({
    title: item.title,
    link: item.link,
    pubDate: item.pubDate,
    content: item.content,
    sentimentScore: sentiment,
    category: url.split('/').pop().replace('.rss', ''),
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
  });
  ```

### 10. Giải pháp thay thế nếu không thể sử dụng Google billing

Nếu lỗi billing không thể khắc phục, bạn có thể chuyển sang:

* **Supabase**: Database với free tier (500 MB storage, 50,000 rows).
  * Tạo dự án trên [Supabase](https://supabase.com/).
  * Tạo bảng `positive_news` và `processed_articles` tương tự Firestore.
* **Fly.io**: Serverless functions với free tier (1 CPU, 256 MB RAM).
  * Tạo ứng dụng trên [Fly.io](https://fly.io/).
  * Triển khai mã tương tự Cloud Function, sử dụng `rss-parser`, `openai`, và `@supabase/supabase-js`.
  * Cấu hình cron job trong `fly.toml` để chạy mỗi giờ.

Mã cho Fly.io:

```javascript
const express = require('express');
const Parser = require('rss-parser');
const { Configuration, OpenAIApi } = require('openai');
const { createClient } = require('@supabase/supabase-js');

const app = express();
const parser = new Parser();
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

app.get('/filter', async (req, res) => {
  try {
    const feed = await parser.parseURL('https://vnexpress.net/rss/gia-dinh.rss');
    for (const item of feed.items) {
      const { data, error } = await supabase
        .from('processed_articles')
        .select('id')
        .eq('link', item.link)
        .single();
      if (error || data) continue;

      const response = await openai.createCompletion({
        model: 'text-davinci-003',
        prompt: `Xác định xem đoạn văn sau có tính chất tích cực, tiêu cực hay trung lập: ${item.content || item.title}\nCảm xúc:`,
        max_tokens: 5,
        temperature: 0,
      });
      const sentiment = response.data.choices[0].text.trim().toLowerCase();

      if (sentiment === 'tích cực') {
        await supabase.from('positive_news').insert({
          title: item.title,
          link: item.link,
          pubDate: item.pubDate,
          content: item.content,
          sentiment_score: 'positive',
        });
      }

      await supabase.from('processed_articles').insert({ link: item.link });
    }
    res.send('Filtered successfully');
  } catch (error) {
    console.error(error);
    res.status(500).send('Error filtering RSS');
  }
});

app.listen(8080, () => {
  console.log('Server running on port 8080');
});
```

* **Cấu hình Fly.io**:
  Tạo `fly.toml`:

  ```toml
  app = "chicken-news-filter"
  [[services]]
  name = "rss-filter"
  internal_port = 8080
  processes = ["app"]
  protocol = "http"
  cron = [
    { schedule = "0 * * * *", url = "/filter" }
  ]
  ```

### 11. Xử lý lỗi và tối ưu hóa

* **Xử lý lỗi**:
  * Mã Cloud Function bao gồm try-catch để ghi log lỗi.
  * Kiểm tra log trong Firebase Console (**Functions > Logs**).

* **Tối ưu hóa**:
  * Chỉ gửi tóm tắt (`item.content`) để giảm số token sử dụng trong OpenAI API.
  * Giảm tần suất chạy hàm (ví dụ: mỗi 2 giờ) nếu cần tiết kiệm tài nguyên.

### 12. Kết luận

Hệ thống này cho phép bạn lọc RSS feed theo thời gian thực, sử dụng ChatGPT để phân tích cảm xúc và Firestore để lưu trữ bài viết tích cực. Nếu lỗi billing không thể khắc phục, bạn có thể chuyển sang Supabase và Fly.io để tránh Google Cloud. Hệ thống hỗ trợ mở rộng cho nhiều danh mục RSS và tích hợp dễ dàng với Flutter.

## Bảng tóm tắt các bước

| **Bước** | **Mô tả** | **Công cụ** |
|----------|-----------|-------------|
| Thiết lập Firebase | Tạo dự án, kích hoạt Firestore và Cloud Functions | Firebase Console, Firebase CLI |
| Đăng ký OpenAI | Lấy API key | OpenAI Platform |
| Viết Cloud Function | Crawl RSS, phân tích cảm xúc, lưu bài tích cực | Node.js, rss-parser, openai |
| Triển khai Cloud Function | Deploy hàm | Firebase CLI |
| Thiết lập Firestore Rules | Bảo mật dữ liệu | Firebase Console |
| Tích hợp Flutter | Hiển thị bài viết | Flutter, cloud_firestore |
| Giải pháp thay thế | Supabase, Fly.io nếu không dùng billing | Supabase, Fly.io |

</xaiArtifact>

#### Key Citations

* [Firebase Cloud Functions Documentation](https://firebase.google.com/docs/functions)

* [OpenAI Platform for API Access](https://platform.openai.com/)
* [Firestore Security Rules Documentation](https://firebase.google.com/docs/firestore/security/get-started)
* [RSS Parser npm Package Documentation](https://www.npmjs.com/package/rss-parser)
* [Supabase Documentation](https://supabase.com/docs)
* [Fly.io Documentation](https://fly.io/docs/)
* [Flutter Supabase Package](https://pub.dev/packages/supabase_flutter)
* [Google Cloud Console for Billing](https://console.cloud.google.com/billing)
* [Node.js Official Website](https://nodejs.org/)

Đây là yêu cầu mới của tôi:
ở tôi đã tạo funcction thành công ròi, nhưng ở bước ghi vào file index.js thì code bạn đưa bị lỗi, bạn có thể research và sửa code lại theo doccument Firebase Cloud Functions được không: /**

* Import function triggers from their respective submodules:
*
* const {onCall} = require("firebase-functions/v2/https");
* const {onDocumentWritten} = require("firebase-functions/v2/firestore");
*
* See a full list of supported triggers at <https://firebase.google.com/docs/functions>
 */

const {onRequest} = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");

// Create and deploy your first functions
// <https://firebase.google.com/docs/functions/get-started>

// exports.helloWorld = onRequest((request, response) => {
//   logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });

const functions = require('firebase-functions'); const admin = require('firebase-admin'); const Parser = require('rss-parser'); const { Configuration, OpenAIApi } = require('openai');

admin.initializeApp(); const db = admin.firestore(); const parser = new Parser(); const configuration = new Configuration({ apiKey: functions.config().openai.api_key, }); const openai = new OpenAIApi(configuration);

exports.scheduledFunction = functions.pubsub.schedule('every 1 hours').onRun(async (context) => { try { const feed = await parser.parseURL('<https://vnexpress.net/rss/gia-dinh.rss>'); for (const item of feed.items) { const docRef = db.collection('processed_articles').doc(item.link); const doc = await docRef.get();

     if (!doc.exists) {
    // Phân tích cảm xúc bằng ChatGPT
    const response = await openai.createCompletion({
      model: 'text-davinci-003',
      prompt: `Xác định xem đoạn văn sau có tính chất tích cực, tiêu cực hay trung lập: ${item.content || item.title}\nCảm xúc:`,
      max_tokens: 5,
      temperature: 0,
    });
    const sentiment = response.data.choices[0].text.trim().toLowerCase();

    // Lưu bài viết tích cực vào Firestore
    if (sentiment === 'tích cực') {
      await db.collection('positive_news').add({
        title: item.title,
        link: item.link,
        pubDate: item.pubDate,
        content: item.content,
        sentimentScore: sentiment,
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
      });
    }

    // Đánh dấu bài viết đã xử lý
    await docRef.set({
      processedAt: admin.firestore.FieldValue.serverTimestamp(),
    });
  }
}
console.log('Processing completed');
return null;

} catch (error) { console.error('Error processing RSS feed:', error); return null; } });
