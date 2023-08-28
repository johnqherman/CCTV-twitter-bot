from dotenv import load_dotenv

load_dotenv(dotenv_path="prod.env")

# user agent string for web requests
USER_AGENT: str = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4"

# request headers containing the user agent
REQUEST_HEADERS: dict[str, str] = {"User-Agent": USER_AGENT}

# number of attempts when fetching camera data
CAMERA_FETCH_ATTEMPTS: int = 3

# initial delay in seconds before the first retry
INITIAL_RETRY_DELAY: int = 1

# after each retry, the delay is multiplied by this factor
RETRY_DELAY_FACTOR: int = 2

# amount of time to wait before the selenium driver times out, in seconds
BROWSER_TIMEOUT: int = 30

# amount of time to wait for the camera stream to load, in seconds
CAMERA_LOAD_TIMEOUT: int = 5

# banned countries to exclude from the camera pool (just Korea for now)
BANNED_COUNTRIES: tuple = ("Korea",)
