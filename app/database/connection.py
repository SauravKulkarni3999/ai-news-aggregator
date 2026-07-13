import os # To work with the operating system
from sqlalchemy import create_engine # connecting python with the database
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Loading configs from dotenv file
load_dotenv()

# defining a function to get the database url from the configs in .env file
def get_database_url() -> str:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autoflush=False, bind=engine)

def get_session():
    return SessionLocal()