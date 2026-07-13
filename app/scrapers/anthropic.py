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
        now = datetime.now(timezone.utc) # setting the current time
        cutoff_time = now - timedelta(hours=hours) # defining the cutoff time
        articles = [] # initializing the articles list
        seen_guids = set() # initializing a set of guids so we dont include the same article twice, each from different website

        for rss_url in self.rss_url: # checking for rss_urls utility
            feed = feedparser.parse(rss_url) # parsing the rss_url to get the feed
            if not feed.entries: 
                return []

            for entry in feed.entries: 
                published_parsed = getattr(entry, "published_parsed", None) # getting the published time and checking if it exists for the article
                if not published_parsed: # if it doesnt exist, we continue
                    continue

                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc) # converting the published parsed time to a format to compare with cutoff time
                if published_time > cutoff_time: # passing the condition 
                    guid = entry.get("id", entry.get("link", "")) # getting the guid
                    if guid not in seen_guids: # checking the set to see if it is a unique GUID
                        seen_guids.add(guid) # Adding unique GUIDs to the set
                        articles.append(AnthropicArticles( # Since the article is unique adding the contents to the articles list
                            title=entry.get("title", ""),
                            description=entry.get("description", ""),
                            url=entry.get("link", ""),
                            guid=guid,
                            published_at=published_time,
                            category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                        ))

        return articles
    
    # creating a function to convert the url to markdown
    def url_to_markdown(self, url: str) -> Optional[str]:
        try:
            result = self.converter.convert(url) # using docling document converter 
            return result.document.export_to_markdown() # utilizing the functionality to convert the link into markdown
        except Exception: 
            return None


if __name__ == "__main__":
    scraper = AnthropicScraper() # Initializing the scraper
    articles: List[AnthropicArticles] = scraper.get_articles(hours=100) # getting the list of articles
    markdown: str = scraper.url_to_markdown(articles[0].url) # converting the articles to markdown
    print(markdown) # printing the markdown