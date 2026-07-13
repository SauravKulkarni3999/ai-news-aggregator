""" The script provides service to get the transcript of the youtube video. """
from typing import Optional

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database.repository import Repository
from app.scrapers.youtube import YoutubeScraper

# Initializing a marker to state where transcript is unavailable
TRANSCRIPT_UNAVAILABLE_MARKER = "__UNAVAILABLE__"

# Defining a function to process the youtube videos
def process_youtube_transcripts(limit: Optional[int] = None) -> dict:
    # Initialize the scrapers and the repo
    scraper = YoutubeScraper()
    repo = Repository()

    # get the videos that dont have a transcript
    videos = repo.get_youtube_video_without_transcript(limit=limit)

    # initialize the processed, unavailable and failed counts
    processed = 0
    unavailable = 0
    failed = 0

    # loop over all the videos 
    for v in videos:
        try:
            transcript_result = scraper.get_transcript(v.video_id) # get the transcript for every video
            if transcript_result: # if the transcript exists update the entry in the youtube video table
                repo.update_youtube_video_transcript(v.video_id, transcript_result.text)
                processed += 1 # update the processed counter
            else: # if the transcript is not available
                repo.update_youtube_video_transcript(v.video_id, TRANSCRIPT_UNAVAILABLE_MARKER) # updating the table with the unavailable marker
                unavailable += 1 # updating the unavailable counter
        except Exception as e:
            repo.update_youtube_video_transcript(v.video_id, TRANSCRIPT_UNAVAILABLE_MARKER)
            failed += 1
            print(f"Error processing video {v.video_id}: {e}")

    return {
        "total": len(videos),
        "processed": processed,
        "unavailable": unavailable,
        "failed": failed
    }

if __name__ == "__main__":
    result = process_youtube_transcripts()
    print(f"Total videos: {result["total"]}")
    print(f"Processed: {result["processed"]}")
    print(f"Unavailable: {result["unavailable"]}")
    print(f"Failed: {result["failed"]}")
        