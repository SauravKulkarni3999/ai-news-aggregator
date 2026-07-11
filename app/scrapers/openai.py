from datetime import datetime, timedelta, timezone # getting the imports for time to setup cutoff timings
from typing import List, Optional 
from pydantic import BaseModel # to define the basemodels for the classes
from docling.document_converter import DocumentConverter # to convert the inputs to docling formats
import feedparser

# Defining a class for storing each openai article in the time frame of interest
class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    published_at: datetime
    category: Optional[str] = None

# Creating the scraper class with required functionalities
class OpenAIScraper:
    def __init__(self):
        self.rss_url = "https://openai.com/news/rss.xml" # rss url for openai news website
        self.converter = DocumentConverter() # initializing the document converter to convert into docling friendly format

    # getting required articles, parameters include the cutoff time, storing it in the articles class (BaseModel) created above
    def get_articles(self, hours: int = 24) -> List[OpenAIArticle]:
        feed = feedparser.parse(self.rss_url) # parsing the feed using the rss url and storing it into a variable
        if not feed.entries: # if the feed is not collecting anything then return an empty list
            return []
        
        now = datetime.now(tz=timezone.utc) # storing the current time so that the cutoff can use it
        cutoff_time = now - timedelta(hours=hours) # setting the cutoff time
        articles = [] # Initializing an empty list to store articles that pass the cutoff criteria

        # looping over all entries in the feed to check if they clear the cutoff criteria
        for entry in feed.entries:
                published_parsed = getattr(entry, "published_parsed", None) # getting the time the entry was published using the functionalities of "entry"
                if not published_parsed:
                    continue

                published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc) # converting the format of the published time to be comparable to the cutoff time
                if published_time > cutoff_time: # checking the condition for each article and then storing relevant information in the format required
                    articles.append(OpenAIArticle(
                        title=entry.get("title", ""),
                        description=entry.get("description", ""),
                        url=entry.get("url", ""),
                        published_at=published_time,
                        category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                    ))

        return articles


if __name__ == "__main__":
    scraper = OpenAIScraper() # initializing the scraper
    articles: List[OpenAIArticle] = scraper.get_articles(hours=24) # getting the articles required
    print(articles)