# Unsecured CCTV Cameras Bot

A Python bot that scrapes random unsecured CCTV cameras and posts them to a Twitter account.

You can see the bot in action [here on its Twitter page](https://twitter.com/Unsecured_CCTV).

<img src="https://user-images.githubusercontent.com/95893344/229968711-b8198a32-d031-4f5b-acc3-d69823556f51.png" alt="West Des Moines, Iowa" width="400"/> <img src="https://user-images.githubusercontent.com/95893344/229968930-2830ccb5-4cf6-493a-83d8-037cd353add0.png" alt="Trento, Italy" width="400"/>

## 🚀 Usage

1. Clone this repository to your local machine.
2. Run `pip install -r requirements.txt` to install the necessary dependencies.
3. Set up a Twitter Developer account and obtain the necessary API credentials. You can find a guide [here](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html).
4. Rename the `prod.env.example` file to `prod.env` and add your API credentials in the following format:

```env
CONSUMER_KEY=YOUR_CONSUMER_KEY
CONSUMER_SECRET=YOUR_CONSUMER_SECRET
ACCESS_TOKEN=YOUR_ACCESS_TOKEN
ACCESS_TOKEN_SECRET=YOUR_ACCESS_TOKEN_SECRET
BEARER_TOKEN=YOUR_BEARER_TOKEN
```

5. Launch the bot by running `python .\src\main.py`.

## 🙌 Credits

This project was developed by John Q. Herman under the [MIT](https://choosealicense.com/licenses/mit/) license. The camera feeds were originally sourced from [Insecam.org](http://www.insecam.org/static/sitemap.xml). As of writing, the official sitemap is returning a 404 error. However, the project has been adapted to use a local version of the sitemap, which is not included in this repository.
