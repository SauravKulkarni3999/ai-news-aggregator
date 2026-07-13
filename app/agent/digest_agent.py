""" This script defines the digest agent that summarizes the articles to create the daily digest."""

import os
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Loading the dotenv file
load_dotenv()

# Creating the digest output class as per the pydantic base model
class DigestOutput(BaseModel):
    title: str
    summary: str

# Defining the system prompt to guide agent behavior
PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance"""

# Creating the digest agent
class DigestAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # getting the API key
        self.model = "gpt-4o-mini" # defining the model of choice
        self.system_prompt = PROMPT # storing the prompt into a system prompt object

    # defining the function that generates the daily digest
    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        try:
            user_prompt = f"Create a digest for this {article_type}: \n Title: {title} \n Content: {content[:8000]}"

            response = self.client.responses.parse(
                model=self.model,
                instructions=self.system_prompt,
                temperature=0.7,
                input=user_prompt,
                text_format=DigestOutput
            )

            return response.output_parsed
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None

