import os
import sys
from typing import Dict

import pytest

src_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.append(src_directory)

from camera import Camera  # noqa: E402


@pytest.fixture
def sample_class():
    return Camera()


@pytest.mark.parametrize(
    "details, expected_output",
    [
        (
            "\n\t\n\t\t\n\t\t\tCountry:\n\t\t\n\t\t\n\t\t\tJapan\n\t\t\n\t\n\t\n\t\t\n\t\t\tCountry code:\n\t\t\n\t\t\n\t\t\tJP\n\t\t\n\t\n\t\n\t\t\n\t\t\tRegion:\n\t\t\n\t\t\n\t\t\tWakayama\n\t\t\n\t\n\t\n\t\t\n\t\t\tCity:\n\t\t\n\t\t\n\t\t\t Tanabe\n\t\t\n\t\n\t\n\t\t\n\t\t\tLatitude:\n\t\t\n\t\t\n\t\t\t33.733000\n\t\t\n\t\n\t\n\t\t\n\t\t\tLongitude:\n\t\t\n\t\t\n\t\t\t135.383000\n\t\t\n\t\n\t\n\t\t\n\t\t\tZIP:\n\t\t\n\t\t\n\t\t\t646-0021\n\t\t\n\t\n\t\n\t\t\n\t\t\tTimezone:\n\t\t\n\t\t\n\t\t\t+09:00 \n\t\t\n\t\n\t\n\t\t\n\t\t\tManufacturer:\n\t\t\n\t\t\n\t\t\tCanon\n\t\t\n\t\n",  # noqa: E501
            {
                "city": " Tanabe",
                "region": "Wakayama",
                "country": "Japan",
                "country_code": "JP",
            },
        ),
        (
            "\n\t\n\t\t\n\t\t\tCountry:\n\t\t\n\t\t\n\t\t\tGermany\n\t\t\n\t\n\t\n\t\t\n\t\t\tCountry code:\n\t\t\n\t\t\n\t\t\tDE\n\t\t\n\t\n\t\n\t\t\n\t\t\tRegion:\n\t\t\n\t\t\n\t\t\tBayern\n\t\t\n\t\n\t\n\t\t\n\t\t\tCity:\n\t\t\n\t\t\n\t\t\t Deggendorf\n\t\t\n\t\n\t\n\t\t\n\t\t\tLatitude:\n\t\t\n\t\t\n\t\t\t48.840860\n\t\t\n\t\n\t\n\t\t\n\t\t\tLongitude:\n\t\t\n\t\t\n\t\t\t12.960680\n\t\t\n\t\n\t\n\t\t\n\t\t\tZIP:\n\t\t\n\t\t\n\t\t\t94469\n\t\t\n\t\n\t\n\t\t\n\t\t\tTimezone:\n\t\t\n\t\t\n\t\t\t+01:00 \n\t\t\n\t\n\t\n\t\t\n\t\t\tManufacturer:\n\t\t\n\t\t\n\t\t\tMobotix\n\t\t\n\t\n",  # noqa: E501
            {
                "city": " Deggendorf",
                "region": "Bayern",
                "country": "Germany",
                "country_code": "DE",
            },
        ),
        (
            "\n\t\n\t\t\n\t\t\tCountry:\n\t\t\n\t\t\n\t\t\tTurkey\n\t\t\n\t\n\t\n\t\t\n\t\t\tCountry code:\n\t\t\n\t\n\t\t\n\t\t\tTR\n\t\t\n\t\n\t\n\t\t\n\t\t\tRegion:\n\t\t\n\t\t\n\t\t\tAnkara\n\t\t\n\t\n\t\n\t\t\n\t\t\tCity:\n\t\t\n\t\t\n\t\t\t Ankara\n\t\t\n\t\n\t\n\t\t\n\t\t\tLatitude:\n\t\t\n\t\t\n\t\t\t39.919870\n\t\t\n\t\n\t\n\t\t\n\t\t\tLongitude:\n\t\t\n\t\t\n\t\t\t32.854270\n\t\t\n\t\n\t\n\t\t\n\t\t\tZIP:\n\t\t\n\t\t\n\t\t\t06530\n\t\t\n\t\n\t\n\t\t\n\t\t\tTimezone:\n\t\t\n\t\t\n\t\t\t+03:00 \n\t\t\n\t\n\t\n\t\t\n\t\t\tManufacturer:\n\t\t\n\t\t\n\t\t\tAxis\n\t\t\n\t\n",  # noqa: E501
            {
                "city": " Ankara",
                "region": "Ankara",
                "country": "Turkey",
                "country_code": "TR",
            },
        ),
    ],
)
def test_parse_camera_details(sample_class: Camera, details: str, expected_output: Dict[str, str]) -> None:
    sample_class.details = details
    assert sample_class._parse_camera_details() == expected_output


def test_parse_camera_details_no_details(sample_class: Camera) -> None:
    sample_class.details = None
    assert sample_class._parse_camera_details() is None


def test_parse_camera_details_empty_string(sample_class: Camera) -> None:
    sample_class.details = ""
    assert sample_class._parse_camera_details() is None
