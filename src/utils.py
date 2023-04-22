import logging
import random
from typing import Tuple

import requests  # type: ignore
import tweepy
from lxml import etree

import constants as c
import settings as s
from camera import Camera
from exceptions import FetchCamerasException, SaveImageException
from shared import exponential_backoff

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authenticate_twitter() -> tweepy.API:
    """Authenticates with the Twitter API and returns a tweepy.API instance."""
    auth = tweepy.OAuthHandler(c.CONSUMER_KEY, c.CONSUMER_SECRET)
    auth.set_access_token(c.ACCESS_TOKEN, c.ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


@exponential_backoff(
    attempts=s.CAMERA_FETCH_ATTEMPTS,
    initial_delay=s.INITIAL_RETRY_DELAY,
    factor=s.RETRY_DELAY_FACTOR,
    exception_types=(FetchCamerasException, SaveImageException),
)
def load_cameras() -> Tuple[str, ...]:
    """Fetches the camera links and returns them as a tuple."""
    r = requests.get(c.SITEMAP_URL)
    r.raise_for_status()

    loc_elements = tuple(link for link in etree.fromstring(r.content).iter("{*}loc"))
    camera_links = tuple(link.text for link in loc_elements)

    logger.info(f"fetched {len(camera_links)} camera links.")
    return camera_links


def get_random_valid_camera(available_cameras: list[str], camera_constructor) -> Camera:
    """Returns a random valid Camera object."""
    while True:
        random_camera_url = random.choice(available_cameras)
        camera = camera_constructor(random_camera_url)
        if not camera.page_content or not camera.stream_url or not camera._url_is_valid():
            logger.info(f"camera rejected: {camera.id}")
            continue

        logger.info(f"camera accepted: {camera.id}")
        return camera


def create_tweet_text(camera_info: dict[str, str], flag: str) -> str:
    """Generates a tweet text based on the camera information and flag."""
    city = camera_info["city"] if camera_info["city"] != "-" else "Unknown"
    region = camera_info["region"] if camera_info["region"] != "-" else "Unknown"
    country = (
        camera_info["country"]
        .replace(", Province Of", "")
        .replace(", Republic Of", "")
        .replace(", Islamic Republic", "")
        .replace("n Federation", "")
        .replace("ian, State Of", "e")
        if camera_info["country"] != "-"
        else "Unknown"
    )

    if country == "United States":
        location = f"{city}, {region}"
    elif country == "Canada":
        location = f"{city}, {region}, {country}"
    else:
        location = f"{city}, {country}"

    if city == "Unknown" and region == "Unknown" and country == "United States":
        return f"Unknown, United States {flag}"
    elif location == "Unknown, Unknown":
        return "Unknown Location"
    else:
        return f"{location} {flag}"


def assemble_flag_emoji(country_code: str) -> str:
    """Converts a country code into a flag emoji."""
    return "".join(c.REGIONAL_INDICATOR_SYMBOLS.get(char, char) for char in country_code)


def post_to_twitter(twitter_api: tweepy.API, tweet_status: str, image_file_path: str) -> bool:
    """
    Posts a tweet with an image to Twitter.
    Returns True if the post is successful, False otherwise.
    """
    try:
        logger.info("posting to twitter...")
        twitter_api.update_status_with_media(status=tweet_status, filename=image_file_path)
        bot_username = twitter_api.me().screen_name
        latest_tweet_id = twitter_api.user_timeline(count=1)[0].id
        tweet_url = f"{c.TWITTER_BASE_URL}{bot_username}/status/{latest_tweet_id}"
        logger.info(f"post successful: {tweet_url}")
        return True
    except tweepy.TweepyException as e:
        logger.error(f"post failed: {e}")
        return False
