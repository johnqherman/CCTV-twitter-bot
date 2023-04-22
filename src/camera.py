import logging
import os
from typing import Dict, Optional

import cv2
import requests  # type: ignore
from lxml.html import fromstring
from numpy import std
from requests.exceptions import ReadTimeout, RequestException  # type: ignore

import settings as s
from exceptions import FetchCamerasException, SaveImageException
from shared import exponential_backoff

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Camera:
    """Camera class to handle camera-related operations."""

    def __init__(self, url: str):
        self.url = url
        self.id = self._get_camera_id()
        self.page_content = self._get_camera_page(s.REQUEST_HEADERS)
        self.page_tree = fromstring(self.page_content) if self.page_content else None
        self.stream_url = self._find_camera_url() if self.page_tree is not None else None
        self.details = self._get_camera_details() if self.page_tree is not None else None
        self.info = self._parse_camera_details() if self.details is not None else None

    def _get_camera_id(self) -> str:
        """Extracts the camera ID from the URL."""
        return "".join(char for char in self.url if char.isdigit())

    def _get_camera_page(self, request_headers: Dict[str, str]) -> Optional[bytes]:
        """Fetches the camera page content."""
        try:
            r = requests.get(self.url, headers=request_headers)
            return r.content
        except (RequestException, OSError) as e:
            logger.error("error capturing image: " + str(e))
            return None

    def _find_camera_url(self) -> Optional[str]:
        """Finds the camera stream URL."""
        if self.page_tree is not None:
            elems = self.page_tree.xpath("//img/@src")
        if len(elems) > 0:
            return elems[0]
        return None

    def _url_is_valid(self) -> bool:
        """Checks if the stream URL is valid."""
        if self.stream_url is None:
            return False

        return all(
            [
                self.stream_url != "/static/no.jpg",
                "?stream" not in self.stream_url,
                ".jpg" in self.stream_url,
            ]
        )

    def _get_camera_details(self) -> Optional[str]:
        """Extracts the camera details."""
        details = self.page_tree.xpath('//div[@class="camera-details"]')
        details_tuple = tuple(detail.text_content() for detail in details)
        details = "".join(detail.replace("\n", "").replace("\t", "").strip() for detail in details_tuple)
        return details

    def _parse_camera_details(self) -> Optional[Dict[str, str]]:
        """Parses the camera details and returns the camera info as a dictionary."""

        if not self.details:
            return None

        details = self.details

        city_start = details.find("City: ") + len("City: ")
        city_end = details.find("Latitude:")
        city = details[city_start:city_end]

        region_start = details.find("Region:") + len("Region:")
        region_end = details.find("City:")
        region = details[region_start:region_end]

        country_start = details.find("Country:") + len("Country:")
        country_end = details.find("Country code:")
        country = details[country_start:country_end]

        country_code_start = details.find("Country code:") + len("Country code:")
        country_code_end = details.find("Region:")
        country_code = details[country_code_start:country_code_end]

        return {
            "city": city,
            "region": region,
            "country": country,
            "country_code": country_code,
        }

    @exponential_backoff(
        attempts=s.CAMERA_FETCH_ATTEMPTS,
        initial_delay=s.INITIAL_RETRY_DELAY,
        factor=s.RETRY_DELAY_FACTOR,
        exception_types=(SaveImageException, FetchCamerasException),
    )
    def _save_image(self, image_file_path: str, camera_url: str, request_headers: Dict[str, str]) -> bool:
        """Saves the image from the camera stream URL."""
        try:
            r = requests.get(camera_url, headers=request_headers, timeout=s.IMAGE_SAVE_TIMEOUT)
            r.raise_for_status()

            with open(image_file_path, "wb") as f:
                f.write(r.content)
            return True
        except (RequestException, ReadTimeout) as e:
            logger.error(f"error saving image: {e}")
            raise SaveImageException(f"error saving image: {e}")

    def _image_is_solid_color(self, image_file_path: str) -> bool:
        """Checks if the image consists of a single color."""
        image = cv2.imread(image_file_path)

        if image is None:
            logging.error("image is empty. skipping...")
            return True

        standard_deviation = std(image)

        if standard_deviation == 0:
            logging.info("image consists of a single color. skipping...")
            return True

        return False

    def save_and_validate_image(self, image_file_path: str, request_headers: Dict[str, str]) -> bool:
        """
        Saves the image and validates that it is not a solid color.
        Returns True if the image is saved and validated, False otherwise.
        """
        saved_successfully = self._save_image(image_file_path, self.stream_url, request_headers)

        if saved_successfully:
            if not self._image_is_solid_color(image_file_path=image_file_path):
                return True
            else:
                os.remove(image_file_path)
                return False
        else:
            return False
