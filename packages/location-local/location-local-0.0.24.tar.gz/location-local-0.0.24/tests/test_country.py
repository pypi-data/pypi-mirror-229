import sys
from unittest.mock import Mock
import os
import pytest
from dotenv import load_dotenv
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from src.country import Country
load_dotenv()


class TestCountry:
    @pytest.mark.test
    def test_get_country_name(self):
        
        mock_results = [
            {
                'components': {
                    'country': 'United States',
                    'country_code': 'US'
                }
            }
        ]
        geocoder_mock = Mock(return_value=mock_results)
        Country.geocoder = geocoder_mock
        result = Country.get_country_name("New York")
        assert result == "United States"

    @pytest.mark.test
    def test_get_country_name_no_results(self):

        geocoder_mock = Mock(return_value=[])
        Country.geocoder = geocoder_mock

        result = Country.get_country_name("Invalid Location")
        assert result is None

    @pytest.mark.test
    def test_get_country_name_state(self):

        mock_results = [
            {
                'components': {
                    'country': 'United States',
                    'country_code': 'US'
                }
            }
        ]
        geocoder_mock = Mock(return_value=mock_results)
        Country.geocoder = geocoder_mock
        result = Country.get_country_name("California")
        assert result == "United States"

    @pytest.mark.test
    def test_get_country_name_code(self):

        mock_results = [
            {
                'components': {
                    'country': 'United States',
                    'country_code': 'US'
                }
            }
        ]
        geocoder_mock = Mock(return_value=mock_results)
        Country.geocoder = geocoder_mock
        result = Country.get_country_name("US")
        assert result == "United States"


if __name__ == "__main__":
    pytest.main()
