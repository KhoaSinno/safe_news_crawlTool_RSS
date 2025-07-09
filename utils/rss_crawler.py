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
                "published": item.get("published", ""),
                "description": clean_description,
                "image_url": image_url,
            }
            entries.append(entry)
        return entries
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        return []
    

# <item>
# <title>Chốn nghỉ dưỡng mang cảm hứng cung đình giữa cố đô</title>

# <description>
# <![CDATA[ <a href="https://vnexpress.net/chon-nghi-duong-mang-cam-hung-cung-dinh-giua-co-do-4909750.html"><img src="https://i1-dulich.vnecdn.net/2025/07/07/image-1726376836-extractword-0-3729-5711-1751878548.png?w=1200&h=0&q=100&dpr=1&fit=crop&s=IzwFnLLMsJpb5SUrl3_B6w"></a></br>Silk Path Grand Hue Hotel &amp; Spa giao hòa giữa chốn nghỉ dưỡng cao cấp và chất Huế, mang đến không gian thư giãn an yên giữa lòng cố đô. ]]>
# </description>

# <pubDate>Tue, 08 Jul 2025 08:30:00 +0700</pubDate>

# <link>https://vnexpress.net/chon-nghi-duong-mang-cam-hung-cung-dinh-giua-co-do-4909750.html</link>

# <guid>https://vnexpress.net/chon-nghi-duong-mang-cam-hung-cung-dinh-giua-co-do-4909750.html</guid>

# <enclosure type="image/jpeg" length="1200" url="https://i1-dulich.vnecdn.net/2025/07/07/image-1726376836-extractword-0-3729-5711-1751878548.png?w=1200&h=0&q=100&dpr=1&fit=crop&s=IzwFnLLMsJpb5SUrl3_B6w"/>

# </item>