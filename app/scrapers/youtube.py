# Getting the imports
from datetime import datetime, timedelta, timezone # for keeping time and also maintaining the recency of the news
from typing import List, Optional # used as typehints
import os # to control the operating system 
from pydantic import BaseModel # to define the class of agents
import feedparser # converts raw into into python dictionaries
from youtube_transcript_api import YouTubeTranscriptApi # Getting the youtube api class
from youtube_transcript_api.proxies import WebshareProxyConfig # Getting the config using username and password
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound # Error classes defined when transcript disabled or not found

# Creating the class for getting the transcripts with the basemodel from pydantic
class Transcript(BaseModel):
    text: str # collects the entire transcript of the video in the str format

class ChannelVideo(BaseModel):
    title: str # Collects the title of video in str format
    url: str # collects the url of the video in the str format
    video_id: str # collects the id of the video
    published_at: datetime # recording the time the video was published at
    description: str # description of the video 
    transcript: Optional[str] = None # the format might be string or can be none


# Creating a class of the youtube scraper
class YoutubeScraper:
    def __init__(self):
        proxy_config = None # Initialize the variable
        proxy_username = os.getenv("PROXY_USERNAME") # Get the username from the .env file
        proxy_password = os.getenv("PROXY_PASSWORD") # Get the password from the .env file

        # Check if the username and password exists and then get the config
        if proxy_username and proxy_password:
            proxy_config = WebshareProxyConfig(
                proxy_username=proxy_username, # assign the username to get the config
                proxy_password=proxy_password # assign the password to get the config
            )
        
        # assigning the transcript api using the proxy config to an object of the class
        self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)

    # Using the channel id to create the url required for the channel id mentioned
    def _get_rss_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    # extracting the video id whether it is from video, shorts
    def _extract_video_id(self, video_url:str) -> str:
        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0] # splitting the url and getting the video id following the url construction framework (video)
        if "youtube.com/shorts/" in video_url:
            return video_url.split("/shorts/")[1].split("?")[0] # splitting the url and getting the video id following the url construction framework (shorts)
        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0] # splitting the url and getting the video id following the url construction framework (shortened url)
        return video_url

    # Getting the transcript from the video url by hitting the transcript api
    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        try:
            transcript = self.transcript_api.fetch(video_id) # givingthe transcript api the video id to fetch the transcript
            text  = " ".join([snippet.text for snippet in transcript.snippets]) # storing the transcript as text
            return Transcript(text=text) # using the typehint defined in the transcript class to store the transcript in the required format
        except (TranscriptsDisabled, NoTranscriptFound): # defining exceptions such as cases where transcript is disabled or no transcript is found
            return None
        except Exception: # defining or catching other forms of error
            return None
    
    # defining a function to get a list of latest videos from the channel that meet the time limit
    def get_latest_videos(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
        feed = feedparser.parse(self._get_rss_url(channel_id)) # using feedparser to parse the url with the required channel id
        if not feed.entries:
            return [] # return empty list of the feed entries are not present
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours) # Setting cut off time as per the hours parameter defined
        videos = [] # initializing empty list for videos

        for entry in feed.entries: # checking for each entry in the feed to get the ChannelVideo class as per the cutoff time
            if "/shorts/" in entry.link: # if shorts then we skip it by continuing to other videos
                continue
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) # get the published time of the video
            if published_time > cutoff_time: # checking if published time passes the cutoff time (published time more recent than cutoff then consider the video)
                video_id = self._extract_video_id(entry.link) # getting the id for videos that qualify as per the cutoff time
                videos.append(ChannelVideo(  # appending the required entries of the feed to the videos list instantiated above. Utilizing the typehint of the channelvideo class
                    title=entry.title,
                    url=entry.link,
                    video_id=video_id,
                    published_at=published_time,
                    description=entry.get("summary", "")
                ))
        
        return videos

    # defining a function to scrape the entire channel for videos
    def scrape_channel(self, channel_id: str, hours: int = 150) -> List[ChannelVideo]: 
        videos = self.get_latest_videos(channel_id, hours) # using channel id and the hours cutoff to get the videos in a list
        result = [] # initializing an empty list for the results
        for video in videos: # iterating over all the videos in the list
            transcript = self.get_transcript(video.video_id) # getting the transcripts using the get_transcript method defined above by using the video_id
            result.append(video.model_copy(update={"transcript": transcript.text if transcript else None})) # appending the transcripts to the results
        return result # returning the results


if __name__ == "__main__":
    scraper = YoutubeScraper() # Initializing the scraper
    transcript: Transcript = scraper.get_transcript("3u0KeTC7jso") # saving the transcripts to a pydantic model
    print(transcript.text) # printing the transcripts
    channel_videos: List[ChannelVideo] = scraper.scrape_channel("UCPiMR-Ize9p3dgjzZ8bo9ZQ", hours=24) # saving the channel_videos to a list using the pydantic model to include details of the videos
     