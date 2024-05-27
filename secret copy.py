import os
from dotenv import load_dotenv
load_dotenv()
db_connect = os.getenv("DATABASE_URL")
telegram_token = os.getenv("TELEGRAM_TOKEN")