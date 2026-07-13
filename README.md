# Project Name

## Project Overview
This project is designed to scrape and process articles and videos from various sources such as Anthropic, OpenAI, and YouTube. It utilizes a series of scrapers to gather data and convert it into a structured format for further analysis or display.

## Tech Stack
- **Python**: Core programming language
- **FastAPI**: Web framework for building APIs
- **Pydantic**: Data validation and settings management using Python type annotations
- **Docker**: Containerization for easy deployment
- **WebshareProxyConfig**: Proxy configuration for secure and anonymous web scraping

## Prerequisites
- **Python 3.8+**: Ensure Python is installed on your system.
- **Docker**: Required for containerized setup.
- **Environment Variables**: Set up `.env` file with necessary credentials for proxy access.

## Local Setup

### Docker Setup
1. Build the Docker image:
   ```bash
   docker build -t project-name .
   ```
2. Run the Docker container:
   ```bash
   docker run -d -p 8000:8000 project-name
   ```

### Native Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints
- **GET /articles/anthropic**: Fetch articles from Anthropic sources.
- **GET /articles/openai**: Fetch articles from OpenAI sources.
- **GET /videos/youtube**: Fetch latest videos from specified YouTube channels.

## Architecture
The project follows a modular architecture with separate scrapers for each data source. The LangGraph state flow manages the state transitions and data processing pipeline, ensuring efficient data handling and transformation.
