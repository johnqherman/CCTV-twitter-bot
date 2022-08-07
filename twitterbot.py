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

    # open valid camera list
    with open('data/cams.csv', 'r') as f:
        cams = list(csv.reader(f))

    # set up scraper
    url = random.choice(cams)[0]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    camera_url = soup.find('img')

    if camera_url is None:
        continue

    # test page & camera validity
    camera_url = camera_url.get('src')

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
        .replace("n Federation", "")

    if city_country == "-, -" or city_country == "line camera" or city_country == "watch online":
        city_country = "Unknown Location"

    def get_state(city):
        with open('data/cities.csv', 'r') as csvfile:
            file = csv.reader(csvfile)
            for row in file:
                if row[1] == city:
                    return row[3]
                
    if "United States" in city_country:
        city = city_country[:city_country.find(",")].strip()
        state = get_state(city)

        if state == "Georgia":
            city_country = city + ", " + state + ", United States"
        else:
            city_country = city + ", " + state
    
    camera_id = ''.join(c for c in url if c.isdigit())
    image_path = "screenshots/" + str(camera_id) + "_" + str(int(time.time())) + ".jpg"
    r = requests.get(camera_url, headers=headers)

    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    with open(image_path, 'wb') as f:
        try:
            print("attempting to capture image: " + camera_url)
            f.write(r.content)
        except requests.exceptions.RequestException as e:
            print(e)
            continue

    # tweet the image
    print("posting to twitter...")
    try:
        api.update_status_with_media(status=city_country, filename=image_path)
    except tweepy.TweepyException as e:
        print("post failed: " + str(e))
        continue
    
    # wait an hour and repeat
    print("post successful; waiting an hour. gn")
    time.sleep(3600)
    continue
