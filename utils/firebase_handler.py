import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
# print(f"Title: {entry['title']}, Link: {entry['link']}, Description: {entry['description']}, Published: {entry['pubDate']}, Image URL: {entry['image_url'] if entry['image_url'] else 'N/A'}")


def store_news(entry, sentiment, is_toxic):
    print(
        f"Checking article: {entry['title']}, Sentiment: {sentiment}, Toxic: {is_toxic}")
    if sentiment == 1 and not is_toxic:
        print("Saving to Firebase...")
        doc_ref = db.collection('news-template').document()
        doc_ref.set({
            'title': entry['title'],
            'link': entry['link'],
            'description': entry['description'],
            'published': entry['pubDate'],
            'image_url': entry['image_url'] if entry['image_url'] else 'N/A',
            'sentiment': sentiment,
            'is_toxic': is_toxic
        })
        print("Saved successfully")
    else:
        print("Article not saved (negative/toxic)")
