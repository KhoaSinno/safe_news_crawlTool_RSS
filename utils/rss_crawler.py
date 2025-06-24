import feedparser
from bs4 import BeautifulSoup  


def fetch_rss(rss_url):
    try:
        feed = feedparser.parse(rss_url)
        entries = []
        for item in feed.entries:
            # Lấy mô tả và làm sạch HTML
            description = item.get("description", "")
            soup = BeautifulSoup(description, "html.parser")
            clean_description = soup.get_text(strip=True)

            # Lấy URL ảnh từ enclosure (nếu có)
            image_url = 'N/A'
            for enclosure in item.get("enclosures", []):
                if enclosure.get("type", "").startswith("image/"):
                    image_url = enclosure.get("url")
                    break

            entry = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "pubDate": item.get("published", ""),
                "description": clean_description,
                "image_url": image_url,
            }
            entries.append(entry)
        return entries
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return []
