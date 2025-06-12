import feedparser

def fetch_rss(url):
    feed = feedparser.parse(url)
    return feed.entries