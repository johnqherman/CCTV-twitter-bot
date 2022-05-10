from bs4 import BeautifulSoup
import requests
import random
import tweepy
import time

# authenticate with twitter
consumer_key = 'CONSUMER_KEY'
consumer_secret = 'CONSUMER_SECRET'
access_token = 'ACCESS_TOKEN'
access_token_secret = 'ACCESS_TOKEN_SECRET'

# set up oauth and tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

while True:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'} # spoof user agent
        page = random.randint(111111, 999999) # generate random page number
        url = 'http://www.insecam.org/en/view/' + str(page) # set url
        r = requests.get(url, headers=headers) # get page
        html = r.text # get html
        soup = BeautifulSoup(html, 'html.parser') # parse html
        camera_url = soup.find('img') # find the image url

        if camera_url is not None: # if the url is not none
            camera_url = camera_url.get('src') # get the image url
        else:
            print("camera_url is None")
            continue

        # test page validity
        print("checking page: " + url)
        if r.status_code == 200: # if the page is valid
            print("valid page found.") # print valid page found and proceed
        else:
            print('invalid page, error ' + str(r.status_code) + '.') # if the page is invalid
            continue

        # test camera availability
        if camera_url == "/static/no.jpg": 
            print('camera found, camera feed unavailable.') 
            continue
        else:
            print('camera feed found! URL: ' + camera_url) # if the camera is available, print the url and proceed

        # reroll on formats that hang the program (i know this is a bad way to do it but it works) 
        if ".mjpg" in camera_url:
            print("camera found, but feed is in unsupported format. finding a new camera...")
            continue

        if "?action=stream" in camera_url:
            print("camera found, but feed is in unsupported format. finding a new camera...")
            continue

        if "wvhttp" in camera_url:
            print("camera found, but feed is in unsupported format. finding a new camera...")
            continue

        if ".cgi" in camera_url:
            print("camera found, but feed is in unsupported format. finding a new camera...")
            continue

        if "?stream" in camera_url:
            print("camera found, but feed is in unsupported format. finding a new camera...")
            continue

        if not ".jpg" in camera_url:
            print("camera found, but feed is in unsupported format. finding a new camera...")
            continue

        # if the location isn't specified, set to unknown location
        if city_country == "-, -":
            city_country = "Unknown Location"

        # try getting the screenshot. if it fails, continue to the next iteration
        print("getting screenshot...")
        try:
            r = requests.get(camera_url, headers=headers) 
        except:
            print("screenshot failed.")
            continue

        # save screenshot to screenshots folder
        image_path = city_country.replace(",", "").replace(" ", "") + "_" + str(int(time.time())) + ".jpg"
        image_path = "screenshots/" + image_path
        print("saving screenshot to " + image_path)
        with open(image_path, 'wb') as f:
            f.write(r.content)

        # post to twitter
        city_country = soup.find('h1').text # find the city and country
        city_country = city_country[11:].strip().replace(", Province Of", "").replace(", Republic Of", "").replace(", Islamic Republic", "").replace("n Federation", "") # pretty up text
        
        tweet = city_country
        print("posting to twitter...")
        try:
            api.update_status_with_media(status=tweet, filename=image_path) # post to twitter with image attached
        except tweepy.TweepyException: # if the tweet fails, print the error and continue to the next iteration
            print("tweepy error.")
            continue

        print("tweet posted!")

        # wait an hour and run again
        print("waiting an hour. gn")
        time.sleep(3600)
        continue
