import urllib.parse
import feedparser
import requests
from bs4 import BeautifulSoup

def fetch_google_rss_news(query: str, max_items: int = 5) -> str:
    """
    ইউজার ইনপুট অনুযায়ী গুগল নিউজ আরএসএস (বাংলা) থেকে খবর খুঁজে বের করে।
    """
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=bn&gl=IN&ceid=IN:bn"
    
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return ""

    compiled_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    for idx, entry in enumerate(feed.entries[:max_items], 1):
        title = entry.get("title", "")
        source = entry.get("source", {}).get("title", "অজানা সূত্র")
        published = entry.get("published", "")
        summary_html = entry.get("summary", "")
        
        # আরএসএস সামারি থেকে এইচটিএমএল ট্যাগ পরিষ্কার করা
        clean_summary = BeautifulSoup(summary_html, "html.parser").get_text(separator=" ", strip=True)
        
        news_item = (
            f"খবর {idx}:\n"
            f"শিরোনাম: {title}\n"
            f"সূত্র: {source} | সময়: {published}\n"
            f"সংক্ষিপ্ত তথ্য: {clean_summary}\n"
        )
        compiled_news.append(news_item)

    return "\n---\n".join(compiled_news)
