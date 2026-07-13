""" This script services the digest table according to the information in the digest agent."""

# getting the imports
from typing import Optional
import logging
import sys
from pathlib import Path

# getting the path errors sorted and directing the
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# getting the required functions
from app.database.repository import Repository
from app.agent.digest_agent import DigestAgent

# Defining the format of logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%y-%m-%d %H:%M:%S'
)

# creating a logger object
logger = logging.getLogger(__name__)

# defining the process to format an article for the digest table
def process_digest(limit: Optional[int] = None) -> dict:
    agent = DigestAgent() # initializing the agent from digest_agent.py
    repo = Repository() # initializing the repo to refer to the articles

    articles = repo.get_articles_without_digest(limit=limit) # getting the articles from the repo without having a digest entry
    total = len(articles) # calculating the total length of the list
    processed = 0 # initializing the processed counter
    failed = 0 # initializing the failed counter

    logger.info(f"Starting the digest processing for {total} articles...") # logging the start of the process
    for idx, article in enumerate(articles, 1): # looping over the article and its index
        article_type = article["type"] 
        article_id = article["id"]
        article_title = article["title"][:60] + "..." if len(article["title"]) > 60 else article["title"] # capping the article title to 60 characters for brevity

        logger.info(f"[{idx}/{total}] Processing {article_type}: {article_title} (ID: {article_id})") # logging the progress

        try: # wrapping the digest functionality to catch any errors
            digest_result = agent.generate_digest( 
                title=article["title"],
                content=article["content"],
                article_type=article_type
            )
            if digest_result: # if the digest agent creates a result, adding it to the repo in the digest table
                repo.create_digest(
                    article_type=article_type,
                    article_id=article_id,
                    url=article["url"],
                    title=digest_result.title,
                    summary=digest_result.summary,
                    published_at=article.get("published_at")
                )
                processed += 1 # updating the counter
                logger.info(f"Successfully created digest for {article_type} {article_id}") # logging the success of the agent
            else:
                failed += 1 # updating the failed counter
                logger.warning(f"Failed to generate digest for {article_type} {article_id}")
        except Exception as e: # catching the error
            failed += 1
            print(f"Error while generating digest for {article_type} {article_id}: {e}")

    logger.info(f"Processing complete: {processed} processed, {failed} failed out of {total} total")

    return {
        "total": total,
        "processed": processed,
        "failed": failed
    }

if __name__ == "__main__":
    result = process_digest() 
    print(f"Total articles: {result["total"]}")
    print(f"Processed: {result["processed"]}")
    print(f"Failed: {result["failed"]}")
