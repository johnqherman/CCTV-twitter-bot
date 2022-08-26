import csv
import os
import random
import time

import requests
import tweepy
from bs4 import BeautifulSoup

# set up twitter api
with open('data/credentials.csv', 'r') as f:
    credentials = list(csv.reader(f))
    auth = tweepy.OAuthHandler(credentials[0][0], credentials[0][1])
    auth.set_access_token(credentials[0][2], credentials[0][3])
    api = tweepy.API(auth)

while True:

    # get cameras from db
    with open('data/cams.csv', 'r') as f:
        cams = list(csv.reader(f))

    # set up scraper
    url = random.choice(cams)[0]
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'}
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    camera_url = soup.find('img')

    if camera_url is None:
        continue

    # test camera validity
    camera_url = camera_url.get('src').replace("?COUNTER", "")
    if camera_url != "/static/no.jpg" \
        and ".mjpg" not in camera_url \
        and "?action=stream" not in camera_url \
        and "wvhttp" not in camera_url \
        and ".cgi" not in camera_url \
        and "?stream" not in camera_url \
        and ".jpg" in camera_url:
        print('camera accepted: ' + url)
    else:
        print('camera rejected: ' + url)
        continue

    # city_country processing
    city_country = soup.find('h1')\
        .text[11:]\
        .strip()\
        .replace(", Province Of", "")\
        .replace(", Republic Of", "")\
        .replace(", Islamic Republic", "")\
        .replace("n Federation", "")\
        .replace("ian, State Of", "e")

    if city_country == "-, -" \
        or city_country == "line camera" \
        or city_country == "watch online":
            city_country = "Unknown Location"

    def get_state(city):
        with open('data/cities.csv', 'r') as csvfile:
            file = csv.reader(csvfile)
            for row in file:
                if row[1] == city:
                    return row[3]
            return "Unknown State"

    def get_flag(city_country):
        with open('data/abbr.csv', 'r') as csvfile:
            file = csv.reader(csvfile)
            if "," in city_country:
                country = city_country.split(',')[1].strip()
            else:
                country = city_country
            for row in file:
                if row[0] == country:
                    return row[1]
            return "🏳"

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

    flag = get_flag(city_country)
    for char, replacement in symbols.items():
        flag = flag.replace(char, replacement)

    if "United States" in city_country:
        city = city_country[:city_country.find(",")].strip()
        state = get_state(city)
        if state == "Georgia":
            city_country = city + ", " + state + ", United States"
        else:
            city_country = city + ", " + state

    # save image
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    camera_id = ''.join(c for c in url if c.isdigit())
    image_path = "screenshots/" + str(camera_id) + "_" + str(int(time.time())) + ".jpg"
    with open(image_path, 'wb') as f:
        try:
            print("attempting to capture image: " + camera_url)
            r = requests.get(camera_url, headers=headers, timeout=5)
            f.write(r.content)
        except(ConnectionError, TimeoutError, OSError) as e:
            print("error: " + str(e))
            continue
    if os.stat(image_path).st_size == 0:
        print("image is empty")
        os.remove(image_path)
        continue

    # post to twitter
    status = city_country + " " + flag if city_country != "Unknown Location" else city_country
    try:
        print("posting to twitter...")
        api.update_status_with_media(status=status, filename=image_path)
    except tweepy.TweepyException as e:
        print("post failed: " + str(e))
        continue
    
    # wait an hour and repeat
    print("post successful, " + status + "\n" + "waiting an hour...")
    time.sleep(3600)
    continue
