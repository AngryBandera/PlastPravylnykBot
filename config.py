"""Configuration file for the Telegram bot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables. Please set it in .env file")

# File paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
IMAGES_DIR = BASE_DIR / 'images'
CSV_FILE = DATA_DIR / 'content.csv'
STATS_FILE = DATA_DIR / 'stats.json'

# Bot settings
REQUEST_KWARGS = {
    'connect_timeout': 15.0,
    'read_timeout': 15.0,
}

# Callback data constants
CALLBACK_PREFIX_TOPIC = 'topic_'
CALLBACK_PREFIX_BACK = 'back_'
CALLBACK_RELOAD = 'reload_data'

# Emoji and symbols
BACK_BUTTON_TEXT = '← Назад'

# Keyboard settings
BUTTONS_PER_ROW = 2
