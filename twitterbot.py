import logging
import os
import random
import time

import cv2
import numpy as np
import requests
import tweepy
from lxml import etree, html
from requests.exceptions import ReadTimeout, RequestException

from credentials import (ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY,
                         CONSUMER_SECRET)
from settings import REQUEST_HEADERS, RETRIES, SITEMAP_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FetchCamerasError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class Camera:
    def __init__(self, url):
        self.url = url
        self.id = self._get_camera_id()
        self.page_content = self._get_camera_page(REQUEST_HEADERS)
        self.page_tree = html.fromstring(
            self.page_content) if self.page_content else None
        self.stream_url = self._find_camera_url() if self.page_tree is not None else None
        self.details = self._get_camera_details() if self.page_tree is not None else None
        self.info = self._parse_camera_details() if self.details is not None else None

    def _get_camera_id(self):
        return ''.join(char for char in self.url if char.isdigit())

    def _get_camera_page(self, request_headers):
        try:
            r = requests.get(self.url, headers=request_headers)
            return r.content
        except (RequestException, OSError) as e:
            logger.error("error capturing image: " + str(e))
            return None

    def _find_camera_url(self):
        camera_url = self.page_tree.xpath('//img/@src')
        return camera_url[0].replace("?COUNTER", "") if camera_url else None

    def _get_camera_details(self):
        details = self.page_tree.xpath('//div[@class="camera-details"]')
        details_array = [detail.text_content() for detail in details]
        details = ''.join(detail.replace('\n', '').replace(
            '\t', '').strip() for detail in details_array)
        return details

    def _parse_camera_details(self):
        details = self.details
        camera_info = {
            "city": details[details.find("City: ") + len("City: "):details.find("Latitude:")],
            "region": details[details.find("Region:") + len("Region:"):details.find("City:")],
            "country": details[details.find("Country:") + len("Country:"):details.find("Country code:")],
            "country_code": details[details.find("Country code:") + len("Country code:"):details.find("Region:")]
        }
        return camera_info

    def _save_image(self, image_file_path, camera_url, request_headers, retries=RETRIES):
        for attempt in range(1, retries + 1):
            try:
                r = requests.get(
                    camera_url, headers=request_headers, timeout=10)
                if r.status_code == 200:
                    with open(image_file_path, 'wb') as f:
                        f.write(r.content)
                    return True
            except (RequestException, ReadTimeout) as e:
                logger.error(f"error saving image: {e}")
                if attempt < retries:
                    logger.info(f"retrying... (attempt {attempt + 1})")
                else:
                    logger.error(
                        "failed to save image after multiple attempts.")
                    return False
        return False

    def _image_is_solid_color(self, image_file_path):
        image = cv2.imread(image_file_path)

        if image is None:
            logging.error("image is empty. skipping...")
            os.remove(image_file_path)
            return True

        standard_deviation = np.std(image)

        if standard_deviation == 0:
            logging.info("image consists of a single color. skipping...")
            os.remove(image_file_path)
            return True

        return False

    def _url_is_valid(self):
        return all([
            self.stream_url != "/static/no.jpg",
            "?stream" not in self.stream_url,
            ".jpg" in self.stream_url,
        ])

    def save_and_validate_image(self, image_file_path, request_headers, retries=RETRIES):
        saved_successfully = self._save_image(
            image_file_path, request_headers, retries)
        if saved_successfully and not self._image_is_solid_color(image_file_path):
            return True
        return False


def authenticate_twitter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def load_cameras(retries=RETRIES):
    for attempt in range(retries):
        r = requests.get(SITEMAP_URL)

        if r.status_code == 200:
            loc_elements = [link for link in etree.fromstring(
                r.content).iter('{*}loc')]
            camera_links = [link.text for link in loc_elements]
            logger.info(f"fetched {len(camera_links)} camera links.")
            return camera_links
        else:
            error_msg = "failed to fetch camera links after multiple attempts."
            logger.error(error_msg)
            if attempt < retries - 1:
                logger.info(f"retrying... (attempt {attempt + 1})")
            else:
                raise FetchCamerasError(error_msg)


def get_random_valid_camera(available_cameras):
    while True:
        random_camera_url = random.choice(available_cameras)
        camera = Camera(random_camera_url)
        if not camera.page_content or not camera.stream_url or not camera._url_is_valid():
            logger.info(f'camera rejected: {camera.id}')
            continue

        logger.info(f'camera accepted: {camera.id}')
        return camera


def create_tweet_text(camera_info, flag):
    city = camera_info['city'] if camera_info['city'] != "-" else "Unknown"
    region = camera_info['region'] if camera_info['region'] != "-" else "Unknown"
    country = camera_info['country']\
        .replace(", Province Of", "")\
        .replace(", Republic Of", "")\
        .replace(", Islamic Republic", "")\
        .replace("n Federation", "")\
        .replace("ian, State Of", "e") if camera_info['country'] != "-" else "Unknown"

    if country == "United States":
        location = city + ", " + region
    elif country == "Canada":
        location = city + ", " + region + ", " + country
    else:
        location = city + ", " + country

    if city == "Unknown" and region == "Unknown" and country == "United States":
        return "Unknown, United States " + flag
    elif location == "Unknown, Unknown":
        return "Unknown Location"
    else:
        return location + " " + flag


def assemble_flag_emoji(country_code):
    symbols = {
        'A': '🇦',
        'B': '🇧',
        'C': '🇨',
        'D': '🇩',
        'E': '🇪',
        'F': '🇫',
        'G': '🇬',
        'H': '🇭',
        'I': '🇮',
        'J': '🇯',
        'K': '🇰',
        'L': '🇱',
        'M': '🇲',
        'N': '🇳',
        'O': '🇴',
        'P': '🇵',
        'Q': '🇶',
        'R': '🇷',
        'S': '🇸',
        'T': '🇹',
        'U': '🇺',
        'V': '🇻',
        'W': '🇼',
        'X': '🇽',
        'Y': '🇾',
        'Z': '🇿'
    }
    return "".join(symbols.get(char, char) for char in country_code)


def post_to_twitter(twitter_api, tweet_status, image_file_path):
    try:
        logger.info("posting to twitter...")
        twitter_api.update_status_with_media(
            status=tweet_status, filename=image_file_path)
        latest_tweet_id = twitter_api.user_timeline(count=1)[0].id
        tweet_url = f"https://twitter.com/Unsecured_CCTV/status/{latest_tweet_id}"
        logger.info(f"post successful: {tweet_url}")
        return True
    except tweepy.TweepError as e:
        logger.error(f"post failed: {e}")
        return False


def main():
    try:
        os.makedirs('images', exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating the 'images' folder: {e}")
        return

    twitter_api = authenticate_twitter()
    available_cameras = load_cameras()

    while True:
        camera = get_random_valid_camera(available_cameras)
        image_file_path = f"images/{camera.id}_{int(time.time())}.jpg"

        if not camera.save_and_validate_image(image_file_path, REQUEST_HEADERS):
            continue

        tweet_status = create_tweet_text(
            camera.info, assemble_flag_emoji(camera.info['country_code']))

        tweet_posted_successfully = post_to_twitter(
            twitter_api, tweet_status, image_file_path)

        if tweet_posted_successfully:
            logger.info("waiting for an hour...")
            time.sleep(60 * 60)


if __name__ == "__main__":
    main()
