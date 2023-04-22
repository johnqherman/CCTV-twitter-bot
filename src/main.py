import logging
import time

import constants as c
import settings as s
from camera import Camera
from utils import (assemble_flag_emoji, authenticate_twitter,
                   create_tweet_text, get_random_valid_camera, load_cameras,
                   post_to_twitter)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    The main function that runs the script. It authenticates with Twitter,
    fetches camera links, and posts images with their locations to Twitter.
    """

    twitter_api = authenticate_twitter()
    available_cameras = load_cameras()

    while True:
        camera = get_random_valid_camera(available_cameras=available_cameras, camera_constructor=Camera)

        image_file_path = c.IMG_FILE_PATH_TEMPLATE.format(c.IMG_ROOT, camera.id, int(time.time()))

        if not camera.save_and_validate_image(image_file_path=image_file_path, request_headers=s.REQUEST_HEADERS):
            continue

        if camera.info is not None:
            tweet_status = create_tweet_text(
                camera.info, assemble_flag_emoji(country_code=camera.info["country_code"])
            )

        tweet_posted_successfully = post_to_twitter(
            twitter_api=twitter_api, tweet_status=tweet_status, image_file_path=image_file_path
        )

        if tweet_posted_successfully:
            logger.info("waiting for an hour...")
            time.sleep(c.SLEEP_DURATION)
        else:
            continue


if __name__ == "__main__":
    main()
