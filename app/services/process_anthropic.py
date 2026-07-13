""" This script provides a service to add markdown to the anthropic articles."""

from typing import Optional

import sys
from pathlib import Path

# Getting the right path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.anthropic import AnthropicScraper
from app.database.repository import Repository

def process_anthropic_markdown(limit: Optional[int] = None) -> dict:
    scraper = AnthropicScraper()

    repo = Repository()

    # Get the articles without the markdown
    articles = repo.get_anthropic_articles_without_markdown(limit=limit)

    # initializing the categories where markdowns are processed and where they are failed
    processed = 0
    failed = 0

    for a in articles:
        markdown = scraper.url_to_markdown(a.url)
        try:
            if markdown:
                repo.update_anthropic_article_markdown(guid=a.guid, markdown=markdown)
                processed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1 
            print(f"Error processing article {a.guid}: {e}")
            continue

    return {
        "total": len(articles),
        "processed": processed,
        "failed": failed
    }

if __name__ == "__main__":
    result = process_anthropic_markdown()
    print(f"Total articles: {result["total"]}")
    print(f"Processed: {result["processed"]}")
    print(f"Failed: {result["failed"]}")