import csv
import random
import time

import requests
import tweepy
from bs4 import BeautifulSoup

# set up twitter api
with open('credentials.csv', 'r') as f:
    credentials = list(csv.reader(f))
    
auth = tweepy.OAuthHandler(credentials[0][0], credentials[0][1])
auth.set_access_token(credentials[0][2], credentials[0][3])
api = tweepy.API(auth)

while True:

    # set up webscraping
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}
    page = random.randint(1, 999999)
    url = 'http://www.insecam.org/en/view/' + str(page)
    r = requests.get(url, headers=headers)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    camera_url = soup.find('img')['src']

    # test page & camera validity
    if r.status_code == 200 \
        and camera_url is not None \
        and camera_url != "/static/no.jpg" \
        and ".mjpg" not in camera_url \
        and "?action=stream" not in camera_url \
        and "wvhttp" not in camera_url \
        and ".cgi" not in camera_url \
        and "?stream" not in camera_url \
        and ".jpg" in camera_url:
        print('camera captured: ' + url)
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

    if city_country == "-, -" or city_country == "line camera":
        city_country = "Unknown Location"

    def get_state(city):
        with open('uscities.csv', 'r') as csvfile:
            file = csv.reader(csvfile)
            for row in file:
                if row[1] == city:
                    return row[3]

    if "United States" in city_country:
        city = city_country[:city_country.find(",")].strip()
        state = get_state(city)
        city_country = city + ", " + state + ", United States"

    # save screenshot to screenshots folder
    r = requests.get(camera_url, headers=headers)
    image_path = "screenshots/" + str(page) + ".jpg"
    with open(image_path, 'wb') as f:
        f.write(r.content)

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
