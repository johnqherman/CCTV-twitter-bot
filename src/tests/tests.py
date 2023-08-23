import os
import sys
from typing import Dict

import pytest
from test_constants import DETAILS_GERMANY, DETAILS_JAPAN, DETAILS_TURKEY

from utils import assemble_flag_emoji, create_tweet_text, replace_substrings

src_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(src_directory)

from camera import Camera  # noqa: E402


class TestCamera:
    @pytest.fixture
    def sample_class(self):
        return Camera()

    @pytest.mark.parametrize(
        "camera_info, flag, expected_output",
        [
            (
                {"city": "New York", "region": "New York", "country": "United States"},
                "🇺🇸",
                "New York, New York 🇺🇸",
            ),
            (
                {"city": "Toronto", "region": "Ontario", "country": "Canada"},
                "🇨🇦",
                "Toronto, Ontario, Canada 🇨🇦",
            ),
            (
                {"city": "Berlin", "region": "Berlin", "country": "Germany"},
                "🇩🇪",
                "Berlin, Germany 🇩🇪",
            ),
            (
                {"city": "-", "region": "Texas", "country": "United States"},
                "🇺🇸",
                "Unknown, Texas 🇺🇸",
            ),
            (
                {"city": "Unknown", "region": "Unknown", "country": "United States"},
                "🇺🇸",
                "Unknown, United States 🇺🇸",
            ),
            ({"city": "-", "region": "-", "country": "-"}, "", "Unknown Location"),
            (
                {"city": "Unknown", "region": "Unknown", "country": "Canada"},
                "🇨🇦",
                "Unknown Location",
            ),
        ],
    )
    def test_create_tweet_text_formats_correctly(self, camera_info, flag, expected_output):
        """Test whether the create_tweet_text function formats the string correctly."""
        assert create_tweet_text(camera_info, flag) == expected_output

    @pytest.mark.parametrize(
        "country_code, expected_flag_emoji",
        [
            ("US", "🇺🇸"),
            ("CA", "🇨🇦"),
            ("DE", "🇩🇪"),
            ("", ""),
            (None, ""),
        ],
    )
    def test_assemble_flag_emoji_generates_correct_emoji(self, country_code, expected_flag_emoji):
        """Test whether the assemble_flag_emoji function generates the correct emoji for each country code."""
        assert assemble_flag_emoji(country_code) == expected_flag_emoji

    def test_replace_substrings_removes_all_occurrences(self):
        """Test whether the replace_substrings function correctly removes all occurrences of specified substrings."""
        test_string = "H1E2L3L4O5 W6O7R8L9D0"
        mappings = {str(i): "" for i in range(10)}
        expected_output = "HELLO WORLD"
        assert replace_substrings(test_string, mappings) == expected_output

    @pytest.mark.parametrize(
        "details, expected_output",
        [
            (
                DETAILS_JAPAN,
                {
                    "city": " Tanabe",
                    "region": "Wakayama",
                    "country": "Japan",
                    "country_code": "JP",
                },
            ),
            (
                DETAILS_GERMANY,
                {
                    "city": " Deggendorf",
                    "region": "Bayern",
                    "country": "Germany",
                    "country_code": "DE",
                },
            ),
            (
                DETAILS_TURKEY,
                {
                    "city": " Ankara",
                    "region": "Ankara",
                    "country": "Turkey",
                    "country_code": "TR",
                },
            ),
        ],
    )
    def test_parse_camera_details_returns_correct_output(
        self,
        mocker,
        sample_class: Camera,
        details: str,
        expected_output: Dict[str, str],
    ) -> None:
        """Test whether the _parse_camera_details function returns the correct output."""
        sample_class.details = details
        spy = mocker.spy(sample_class, "_parse_camera_details")
        assert sample_class._parse_camera_details() == expected_output
        spy.assert_called_once()

    def test_parse_camera_details_returns_none_when_no_details(self, sample_class: Camera) -> None:
        """Test whether the _parse_camera_details function returns None when no details are provided."""
        sample_class.details = None
        assert sample_class._parse_camera_details() is None

    def test_parse_camera_details_returns_none_when_empty_string(self, sample_class: Camera) -> None:
        """Test whether the _parse_camera_details function returns None when an empty string is provided as details."""
        sample_class.details = ""
        assert sample_class._parse_camera_details() is None
