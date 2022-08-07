# Unsecured CCTV camera bot
A Python bot that crawls random unsecured CCTV cameras and posts them to a Twitter account.

You can see the bot in action here: https://twitter.com/Unsecured_CCTV

<img src="https://user-images.githubusercontent.com/95893344/166120138-fb6bd3eb-7243-4c92-83d4-86c8fc66bda6.jpg" alt="Tehran, Iran" width="400"/> <img src="https://user-images.githubusercontent.com/95893344/166120172-403e4f28-5d1e-42b0-b11c-f119409a38fc.jpg" alt="Olomouc, Czech Republic" width="330"/>

#
## How to use the bot

1. Generate your own `credentials.csv` file following the format in the `credentials.csv.example` file.

    ```
    CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET
    ```

2. Install dependencies.

    ```
    pip install -r requirements.txt
    ```
3. Run the bot.

    ```bash
    python twitterbot.py
    ```
# 
## Citations

`cities.csv` taken from [Simplemaps.com](https://simplemaps.com/data/us-cities)

`cams.csv` generated from [Insecam.org](http://www.insecam.org/static/sitemap.xml)
