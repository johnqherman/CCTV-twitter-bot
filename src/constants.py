import os
from typing import Dict

import dotenv

dotenv.load_dotenv("prod.env")

# twitter API credentials from environment variables
CONSUMER_KEY: str = os.getenv("CONSUMER_KEY", "")
CONSUMER_SECRET: str = os.getenv("CONSUMER_SECRET", "")
ACCESS_TOKEN: str = os.getenv("ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET: str = os.getenv("ACCESS_TOKEN_SECRET", "")
BEARER_TOKEN: str = os.getenv("BEARER_TOKEN", "")

# template for the image file path with placeholders for variables
IMG_FILE_PATH_TEMPLATE: str = "{0}{1}_{2}.jpg"

# the root directory where images will be stored
IMG_ROOT: str = "../images/"

# regional indicator symbols used to construct the flag emoji at the end of a tweet
REGIONAL_INDICATOR_SYMBOLS: Dict[str, str] = {
    "A": "🇦",
    "B": "🇧",
    "C": "🇨",
    "D": "🇩",
    "E": "🇪",
    "F": "🇫",
    "G": "🇬",
    "H": "🇭",
    "I": "🇮",
    "J": "🇯",
    "K": "🇰",
    "L": "🇱",
    "M": "🇲",
    "N": "🇳",
    "O": "🇴",
    "P": "🇵",
    "Q": "🇶",
    "R": "🇷",
    "S": "🇸",
    "T": "🇹",
    "U": "🇺",
    "V": "🇻",
    "W": "🇼",
    "X": "🇽",
    "Y": "🇾",
    "Z": "🇿",
}

# dictionary of mappings to shorten country names
COUNTRY_REPLACEMENTS: Dict[str, str] = {
    ", Province Of": "",
    ", Republic Of": "",
    ", Islamic Republic": "",
    "n Federation": "",
    "ian, State Of": "e",
}

# duration in seconds to wait before posting another tweet
SLEEP_DURATION: int = 60 * 60

# the URL of the sitemap for the insecam website
SITEMAP_URL: str = "http://www.insecam.org/static/sitemap.xml"

# the base URL for twitter
TWITTER_BASE_URL: str = "https://twitter.com"
