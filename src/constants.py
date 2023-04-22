import os

import dotenv

dotenv.load_dotenv("prod.env")

# twitter API credentials from environment variables
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# template for the image file path with placeholders for variables
IMG_FILE_PATH_TEMPLATE = "{0}{1}_{2}.jpg"

# the root directory where images will be stored
IMG_ROOT = "../images/"

# regional indicator symbols used to construct the flag emoji at the end of a tweet
REGIONAL_INDICATOR_SYMBOLS = {
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

# duration in seconds to wait before posting another tweet
SLEEP_DURATION = 60 * 60

# the URL of the sitemap for the insecam website
SITEMAP_URL = "http://www.insecam.org/static/sitemap.xml"

# the base URL for twitter
TWITTER_BASE_URL = "https://twitter.com"
