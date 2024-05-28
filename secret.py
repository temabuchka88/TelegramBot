import os
from dotenv import load_dotenv
load_dotenv()
db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@68.183.79.114:5432/{os.getenv('POSTGRES_DB')}"
os.environ["DATABASE_URL"] = db_url
db_connect = os.getenv("DATABASE_URL")
telegram_token = os.getenv("BOT_TOKEN")