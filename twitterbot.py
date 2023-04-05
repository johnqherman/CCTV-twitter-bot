import csv
import os
import random
import time

import cv2
import requests
import tweepy
from lxml import etree, html
from requests.exceptions import ReadTimeout, RequestException, Timeout


def load_credentials():
    with open('credentials.csv', 'r') as f:
        return list(csv.reader(f))


def load_cameras():
    r = requests.get("http://www.insecam.org/static/sitemap.xml")

    if r.status_code == 200:
        loc_elements = [link for link in etree.fromstring(
            r.content).iter('{*}loc')]
        camera_links = [link.text for link in loc_elements]
        print(f"fetched {len(camera_links)} camera links.")
    else:
        print("failed to fetch camera links.")
        return None

    return camera_links


def get_random_camera_url(camera_links):
    random_camera_url = random.choice(camera_links)
    return random_camera_url


def get_camera_id(random_camera_url):
    return ''.join(c for c in random_camera_url if c.isdigit())


def get_camera_page(random_camera_url, headers):
    try:
        r = requests.get(random_camera_url, headers=headers)
        return r.content
    except (requests.exceptions.RequestException, OSError) as e:
        print("error capturing image: " + str(e))
        return None


def find_camera_url(tree):
    camera_url = tree.xpath('//img/@src')
    return camera_url[0].replace("?COUNTER", "") if camera_url else None


def is_valid_camera(camera_url):
    return camera_url != "/static/no.jpg" \
        and "?stream" not in camera_url \
        and ".jpg" in camera_url


def get_camera_details(tree):
    details = tree.xpath('//div[@class="camera-details"]')
    details_array = [detail.text_content() for detail in details]
    details = ''.join(detail.replace('\n', '').replace(
        '\t', '').strip() for detail in details_array)
    return details


def parse_camera_details(details):
    camera_info = {
        "city": details[details.find("City: ") + len("City: "):details.find("Latitude:")],
        "region": details[details.find("Region:") + len("Region:"):details.find("City:")],
        "country": details[details.find("Country:") + len("Country:"):details.find("Country code:")],
        "country_code": details[details.find("Country code:") + len("Country code:"):details.find("Region:")]
    }
    return camera_info


def shorten_country_name(country):
    return (country
            .replace(", Province Of", "")
            .replace(", Republic Of", "")
            .replace(", Islamic Republic", "")
            .replace("n Federation", "")
            .replace("ian, State Of", "e"))


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


def save_image(image_path, camera_url, headers, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(camera_url, headers=headers, timeout=10)
            if r.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(r.content)
                return True
        except (RequestException, ReadTimeout, Timeout) as e:
            print(f"error downloading image: {e}")
            if attempt < retries - 1:
                print(f"retrying... (attempt {attempt + 1})")
            else:
                print("download failed after multiple attempts.")
                return False
    return False


def image_is_solid_grey(image_path):
    img = cv2.imread(image_path)
    if (img == [16, 16, 16]).all():
        os.remove(image_path)
        return True
    return False


def create_tweet_text(camera_info, flag):
    city = camera_info['city'] if camera_info['city'] != "-" else "Unknown"
    region = camera_info['region'] if camera_info['region'] != "-" else "Unknown"
    country = camera_info['country'] if camera_info['country'] != "-" else "Unknown"

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


def post_to_twitter(api, status, image_path):
    try:
        print("posting to twitter...")
        api.update_status_with_media(status=status, filename=image_path)
        latest_tweet_id = api.user_timeline(count=1)[0].id
        tweet_url = f"https://twitter.com/Unsecured_CCTV/status/{latest_tweet_id}"
        print(f"post successful: {tweet_url}")
        return True
    except tweepy.TweepError as e:
        print("post failed: " + str(e))
        return False


def main():

    # twitter credentials
    credentials = load_credentials()
    auth = tweepy.OAuthHandler(credentials[0][0], credentials[0][1])
    auth.set_access_token(credentials[0][2], credentials[0][3])
    api = tweepy.API(auth)

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'}

    cameras_list = load_cameras()

    while True:
        random_camera_url = get_random_camera_url(cameras_list)
        random_camera_id = get_camera_id(random_camera_url)
        camera_page_content = get_camera_page(random_camera_url, headers)

        if not camera_page_content:
            continue

        camera_page_tree = html.fromstring(camera_page_content)
        camera_stream_url = find_camera_url(camera_page_tree)

        if not camera_stream_url or not is_valid_camera(camera_stream_url):
            print(f'camera rejected: {random_camera_id}')
            continue

        print(f'camera accepted: {random_camera_id}')

        details = get_camera_details(camera_page_tree)
        camera_info = parse_camera_details(details)
        camera_info['country'] = shorten_country_name(camera_info['country'])
        flag = assemble_flag_emoji(camera_info['country_code'])

        image_path = f"{random_camera_id}_{int(time.time())}.jpg"
        saved_successfully = save_image(image_path, camera_stream_url, headers)

        if not saved_successfully:
            print("failed to save the image. skipping...")
            continue

        if image_is_solid_grey(image_path):
            print("image is solid grey. skipping...")
            continue

        status = create_tweet_text(camera_info, flag)
        posted_successfully = post_to_twitter(api, status, image_path)

        if posted_successfully:
            print("waiting for an hour...")
            time.sleep(60 * 60)


if __name__ == "__main__":
    main()
