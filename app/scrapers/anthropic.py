from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import List, Optional
from docling.document_converter import DocumentConverter
import feedparser

# Defining the class to store the anthropic articles
class AnthropicArticles(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None

# defining the scraper class and adding the functionalities
class AnthropicScraper():
    def __init__(self):
        self.rss_url = [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml", # url for general anthropic news
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml", # url for antrhopic research news
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml" # url for anthropic engineering news
        ]
        self.converter = DocumentConverter() # initializing the converter

    def get_articles(self, hours: int = 24) -> List[AnthropicArticles]:
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []
        seen_guids = set()

        for rss_url in self.rss_url:
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                return []

            for entry in feed.entries:
                published_parsed = getattr(entry, "published_parsed", None)
                if not published_parsed:
                    continue

                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                if published_time > cutoff_time:
                    guid = entry.get("id", entry.get("link", ""))
                    if guid not in seen_guids:
                        seen_guids.add(guid)
                        articles.append(AnthropicArticles(
                            title=entry.get("title", ""),
                            description=entry.get("description", ""),
                            url=entry.get("link", ""),
                            guid=guid,
                            published_at=published_time,
                            category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                        ))

        return articles
        
    def url_to_markdown(self, url: str) -> Optional[str]:
        try:
            result = self.converter.convert(url)
            return result.document.export_to_markdown()
        except Exception:
            return None


if __name__ == "__main__":
    scraper = AnthropicScraper()
    articles: List[AnthropicArticles] = scraper.get_articles(hours=100)
    markdown: str = scraper.url_to_markdown(articles[0].url)
    print(markdown)