# safe_news_crawlTool_RSS

## Môi trường chạy python trên máy (Setup vào lagaron)
/e/Lenovo/laragon/bin/python/python-3.10/python.exe -m pip install beautifulsoup4



## File: news_filter.py

Dự án này được thiết kế để phân tích văn bản tiếng Việt nhằm xác định tình cảm (tích cực, tiêu cực, trung tính) và phát hiện nội dung độc hại. Nó sử dụng các mô hình học máy đã được huấn luyện trước từ thư viện Hugging Face Transformers.

Quy trình hoạt động chính:

Tải và Khởi tạo Mô hình:

Thư viện: Mã nguồn sử dụng transformers để dễ dàng tải các mô hình và tokenizer, và torch (PyTorch) làm nền tảng cho các tính toán của mô hình.
Sentiment Analysis (Phân tích Tình cảm):
sentiment_model_name = "wonrax/phobert-base-vietnamese-sentiment": Định danh của một mô hình PhoBERT đã được tinh chỉnh (fine-tuned) cho tác vụ phân tích tình cảm tiếng Việt, được lưu trữ trên Hugging Face Model Hub.
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name): Tải tokenizer tương ứng với mô hình sentiment. Tokenizer có nhiệm vụ chuyển đổi văn bản thô thành một định dạng (các token ID) mà mô hình có thể hiểu.
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name): Tải chính mô hình phân loại tình cảm. AutoModelForSequenceClassification là một lớp chung có thể tải nhiều kiến trúc mô hình khác nhau phù hợp cho tác vụ phân loại chuỗi (ví dụ: phân loại văn bản).
Toxicity Detection (Phát hiện Độc tính):
toxicity_model_name = "naot97/vietnamese-toxicity-detection_1": Định danh của mô hình phát hiện độc tính cho tiếng Việt.
toxicity_tokenizer = AutoTokenizer.from_pretrained(toxicity_model_name): Tải tokenizer cho mô hình độc tính.
toxicity_model = AutoModelForSequenceClassification.from_pretrained(toxicity_model_name): Tải mô hình phát hiện độc tính.
Hàm analyze_sentiment(text) (Phân tích Tình cảm):

Tokenization:
inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512):
Văn bản đầu vào (text) được đưa qua sentiment_tokenizer.
return_tensors="pt": Yêu cầu tokenizer trả về kết quả dưới dạng PyTorch tensors.
truncation=True: Nếu văn bản dài hơn max_length, nó sẽ được cắt ngắn.
max_length=512: Giới hạn độ dài tối đa của chuỗi token đầu vào.
Dự đoán (Inference):
with torch.no_grad():: Context manager này của PyTorch vô hiệu hóa việc tính toán gradient. Điều này quan trọng trong quá trình inference (khi chỉ sử dụng mô hình để dự đoán, không phải huấn luyện) vì nó giúp tiết kiệm bộ nhớ và tăng tốc độ xử lý.
outputs = sentiment_model(**inputs): Dữ liệu đã được tokenize (inputs) được truyền vào sentiment_model. Toán tử** giải nén dictionary inputs thành các đối số cho mô hình.
Xử lý Kết quả:
logits = outputs.logits: Lấy ra logits từ kết quả của mô hình. Logits là các điểm số thô (chưa được chuẩn hóa) mà mô hình gán cho mỗi lớp tình cảm (ví dụ: tiêu cực, tích cực, trung tính).
probabilities = torch.softmax(logits, dim=-1): Áp dụng hàm softmax lên logits để chuyển đổi chúng thành xác suất. Hàm softmax đảm bảo rằng tổng các xác suất của tất cả các lớp là 1. dim=-1 chỉ định rằng softmax được áp dụng trên chiều cuối cùng của tensor (chiều của các lớp).
return probabilities.argmax().item():
probabilities.argmax(): Tìm chỉ số (index) của lớp có xác suất cao nhất.
.item(): Chuyển đổi tensor kết quả (chỉ chứa một giá trị là chỉ số lớp) thành một số Python tiêu chuẩn.
Kết quả trả về là một số nguyên: 0 (Tiêu cực - NEG), 1 (Tích cực - POS), hoặc 2 (Trung tính - NEU).
Hàm detect_toxicity(text) (Phát hiện Độc tính):

Tokenization và Dự đoán: Tương tự như hàm analyze_sentiment, nhưng sử dụng toxicity_tokenizer và toxicity_model.
Xử lý Kết quả:
logits = outputs.logits
probabilities = torch.softmax(logits, dim=-1)
return probabilities[0][1].item() > 0.5:
Mô hình này có vẻ trả về xác suất cho hai lớp: không độc hại (thường là index 0) và độc hại (thường là index 1).
probabilities[0][1] truy cập vào xác suất của lớp "độc hại" (index 1) cho mẫu đầu vào đầu tiên (index 0, vì inputs có thể là một batch, nhưng ở đây ta xử lý từng text một).
.item(): Chuyển đổi tensor xác suất thành số Python.
> 0.5: So sánh xác suất này với một ngưỡng (0.5). Nếu xác suất văn bản là độc hại lớn hơn 0.5, hàm trả về True (độc hại), ngược lại trả về False (không độc hại).
Tóm lại: Dự án này cung cấp hai công cụ: một để đánh giá tình cảm của văn bản tiếng Việt và một để kiểm tra xem văn bản đó có chứa nội dung độc hại hay không. Cả hai công cụ đều dựa trên việc tải các mô hình ngôn ngữ đã được huấn luyện trước, xử lý văn bản đầu vào thông qua tokenization, sau đó đưa vào mô hình để nhận dự đoán và cuối cùng là diễn giải kết quả đầu ra của mô hình.
