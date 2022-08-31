import csv
import os
import random
import time

import requests
import tweepy
from bs4 import BeautifulSoup

# twitter api credentials
with open('data/credentials.csv', 'r') as f:
    credentials = list(csv.reader(f))
    auth = tweepy.OAuthHandler(credentials[0][0], credentials[0][1])
    auth.set_access_token(credentials[0][2], credentials[0][3])
    api = tweepy.API(auth)

while True:
    # get cameras from db file
    with open('data/cams.csv', 'r') as f:
        cams = list(csv.reader(f))

    url = random.choice(cams)[0] # pick a random camera
    camera_id = ''.join(c for c in url if c.isdigit()) # assign unique camera id
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'} # spoof user agent
    r = requests.get(url, headers=headers) # get camera page
    html = r.text # get html as text
    soup = BeautifulSoup(html, 'html.parser') # parse html
    camera_url = soup.find('img') # find camera feed

    # make sure url isn't NoneType object
    if camera_url is not None:
            camera_url = camera_url.get('src').replace("?COUNTER", "")
    else:
        print("camera URL is None. skipping...")
        continue

    # check camera format
    if camera_url != "/static/no.jpg" \
        and ".mjpg" not in camera_url \
        and "?action=stream" not in camera_url \
        and "wvhttp" not in camera_url \
        and ".cgi" not in camera_url \
        and "?stream" not in camera_url \
        and ".jpg" in camera_url:
        print('camera accepted: ' + camera_id)
    else:
        print('camera rejected: ' + camera_id)
        continue

    # grab detailed camera info
    details = soup.find_all('div', class_='camera-details')
    details_array = []
    for detail in details:
        details_array.append(detail.text)

    # remove extra newlines, tabs, and whitespace
    details = str([detail.replace('\n', '').replace('\t', '').strip() for detail in details_array])

    # store camera details
    camera_info = {
        "city": details[details.find("City: ") + len("City: "):details.find("Latitude:")],
        "region": details[details.find("Region:") + len("Region:"):details.find("City:")],
        "country": details[details.find("Country:") + len("Country:"):details.find("Country code:")],
        "country_code": details[details.find("Country code:") + len("Country code:"):details.find("Region:")]
    }

    # shorten country names
    country = camera_info['country']\
        .replace(", Province Of", "")\
        .replace(", Republic Of", "")\
        .replace(", Islamic Republic", "")\
        .replace("n Federation", "")\
        .replace("ian, State Of", "e")

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

    # assemble flag emoji from regional indicator symbols
    flag = camera_info["country_code"]
    for char, replacement in symbols.items():
        flag = flag.replace(char, replacement)

    # save image to disk
    image_path = str(camera_id) + "_" + str(int(time.time())) + ".jpg"
    with open(image_path, 'wb') as f:
        try:
            print("attempting to capture image...")
            r = requests.get(camera_url, headers=headers, timeout=5)
            f.write(r.content)
        except(ConnectionError, TimeoutError, OSError) as e:
            print("error capturing image: " + str(e))
            os.remove(image_path)
            continue
    if os.stat(image_path).st_size == 0:
        print("image is empty")
        os.remove(image_path)
        continue

    # assemble location string
    if country == "United States":
        location = camera_info['city'] + ", " + camera_info['region']
    elif country == "Canada":
        location = camera_info['city'] + ", " + camera_info['region'] + ", " + country
    else:
        location = camera_info['city'] + ", " + country

    # set tweet text
    if location == "-, -" or "," not in location:
        status = "Unknown Location"
    else:
        status = location + " " + flag

    # post to twitter
    try:
        print("posting to twitter...")
        api.update_status_with_media(status=status, filename=image_path)
    except tweepy.TweepyException as e:
        print("post failed: " + str(e))
        continue

    # delete image, wait an hour, and repeat
    print("post successful: https://twitter.com/Unsecured_CCTV/status/" + str(api.user_timeline(count=1)[0].id) + "\n" + "waiting an hour...")
    os.remove(image_path)
    time.sleep(3600)
    continue
