import firebase_admin
from firebase_admin import credentials, firestore
import logging
import hashlib
from datetime import datetime

# Khởi tạo Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def generate_article_id(title, link):
    """
    Tạo ID duy nhất cho bài báo dựa trên title và link
    """
    content = f"{title}|{link}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def is_article_exists(title, link):
    """
    Kiểm tra xem bài báo đã tồn tại trong Firebase chưa
    """
    article_id = generate_article_id(title, link)
    try:
        doc_ref = db.collection('news-crawler').document(article_id)
        doc = doc_ref.get()
        return doc.exists
    except Exception as e:
        logging.error(f"Error checking article existence: {e}")
        return False


def store_to_firebase(firebase_data: dict, collection_name: str = 'positive_news_test') -> bool:
    """
    Lưu tin tức vào Firebase collection với schema chuẩn
    Args:
        firebase_data: Dict với Firebase schema (8 fields)
        collection_name: Tên collection (mặc định: positive_news_test)
    Returns:
        bool: True nếu lưu thành công
    """
    try:
        title = firebase_data.get('title', '')
        link = firebase_data.get('link', '')

        # Kiểm tra trùng lặp
        if is_article_exists_in_collection(title, link, collection_name):
            logging.info(f"📰 Article already exists: {title[:50]}...")
            return False

        # Tạo document ID duy nhất
        doc_id = generate_article_id(title, link)

        # Thêm timestamp và loại bỏ các trường nội bộ (bắt đầu bằng _)
        clean_data = {k: v for k, v in firebase_data.items() if not k.startswith('_')}
        firebase_data_with_timestamp = {
            **clean_data,
            'created_at': datetime.now().isoformat(),
            'source': 'gemini-2.5-flash'
        }

        # Lưu vào Firebase
        db.collection(collection_name).document(
            doc_id).set(firebase_data_with_timestamp)

        logging.info(
            f"✅ Stored to Firebase [{collection_name}]: {title[:50]}...")
        return True

    except Exception as e:
        logging.error(f"❌ Firebase storage error: {e}")
        return False


def is_article_exists_in_collection(title: str, link: str, collection_name: str) -> bool:
    """
    Kiểm tra xem bài báo đã tồn tại trong collection cụ thể chưa
    """
    article_id = generate_article_id(title, link)
    try:
        doc_ref = db.collection(collection_name).document(article_id)
        doc = doc_ref.get()
        return doc.exists
    except Exception as e:
        logging.error(f"Error checking article existence: {e}")
        return False


def store_news(entry, sentiment, is_toxic):
    """
    LEGACY FUNCTION - Giữ lại để tương thích với code cũ
    """
    title = entry.get('title', '')
    link = entry.get('link', '')

    # Log thông tin kiểm tra
    logging.info(
        f"Checking article: {title[:50]}..., Sentiment: {sentiment}, Toxic: {is_toxic}")

    # Chuyển đổi sentiment từ string sang number
    sentiment_number = 1 if sentiment == 'POSITIVE' else 0

    # Chỉ lưu tin tích cực và không độc hại
    if sentiment == 'POSITIVE' and not is_toxic:
        # Kiểm tra trùng lặp trước khi lưu
        if is_article_exists(title, link):
            logging.info(f"Article already exists, skipping: {title[:50]}...")
            print(f"🔄 Bài đã tồn tại, bỏ qua: {title[:50]}...")
            return False

        try:
            # Tạo ID duy nhất cho document
            article_id = generate_article_id(title, link)
            doc_ref = db.collection('news-crawler').document(article_id)

            # Lưu dữ liệu theo đúng schema Firebase
            doc_ref.set({
                'title': title,
                'category': entry.get('category', ''),
                'link': link,
                'description': entry.get('description', ''),
                'published': entry.get('pubDate', ''),
                'image_url': entry.get('image_url', ''),
                'sentiment': sentiment_number,  # number: 1 cho POSITIVE
                'is_toxic': is_toxic            # boolean
            })

            logging.info(f"✅ Stored positive news: {title}")
            print(f"✅ Đã lưu tin tích cực: {title[:50]}...")
            return True

        except Exception as e:
            error_msg = f"Error saving to Firebase: {e}"
            logging.error(error_msg)
            print(f"❌ Lỗi lưu Firebase: {e}")
            return False
    else:
        logging.info(
            f"Article not saved (sentiment: {sentiment}, toxic: {is_toxic})")
        print(f"❌ Không lưu bài (sentiment: {sentiment}, toxic: {is_toxic})")
        return False
