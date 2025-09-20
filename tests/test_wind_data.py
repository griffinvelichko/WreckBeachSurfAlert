"""
Unit tests for wind data fetching and parsing.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wind_data import parse_openmeteo, fetch_wind_data


class TestWindData(unittest.TestCase):
    """Test wind data fetching and parsing."""

    def test_parse_openmeteo_valid(self):
        """Test parsing valid Open-Meteo response."""
        data = {
            'hourly': {
                'wind_speed_10m': [15.5, 16.0],
                'wind_direction_10m': [310, 315]
            }
        }
        result = parse_openmeteo(data)
        self.assertEqual(result['speed'], 15.5)
        self.assertEqual(result['direction'], 310)
        self.assertEqual(result['source'], 'open-meteo')

    def test_parse_openmeteo_missing_data(self):
        """Test parsing Open-Meteo response with missing data."""
        data = {
            'hourly': {
                'wind_speed_10m': [],
                'wind_direction_10m': []
            }
        }
        with self.assertRaises(ValueError):
            parse_openmeteo(data)

    def test_parse_openmeteo_null_values(self):
        """Test parsing Open-Meteo response with null values."""
        data = {
            'hourly': {
                'wind_speed_10m': [None],
                'wind_direction_10m': [None]
            }
        }
        with self.assertRaises(ValueError):
            parse_openmeteo(data)

    @patch('wind_data.requests.get')
    def test_fetch_wind_data_success(self, mock_get):
        """Test successful wind data fetch from Open-Meteo."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'hourly': {
                'wind_speed_10m': [25.0],
                'wind_direction_10m': [315.0]
            }
        }
        mock_get.return_value = mock_response

        result = fetch_wind_data()
        self.assertIsNotNone(result)
        self.assertEqual(result['speed'], 25.0)
        self.assertEqual(result['direction'], 315.0)
        self.assertEqual(result['source'], 'open-meteo')

    @patch('wind_data.requests.get')
    def test_fetch_wind_data_fallback(self, mock_get):
        """Test fallback to ECCC when Open-Meteo fails."""
        # First call (Open-Meteo) fails
        mock_get.side_effect = [
            Exception("Connection error"),
            MagicMock(status_code=200, text='<xml><windSpeed>20</windSpeed><windDirection>NW</windDirection></xml>')
        ]

        with patch('wind_data.fetch_eccc_data') as mock_eccc:
            mock_eccc.return_value = {
                'speed': 20.0,
                'direction': 315.0,
                'source': 'eccc'
            }
            result = fetch_wind_data()
            self.assertIsNotNone(result)
            self.assertEqual(result['source'], 'eccc')
            mock_eccc.assert_called_once()

    @patch('wind_data.requests.get')
    def test_fetch_wind_data_all_fail(self, mock_get):
        """Test when all data sources fail."""
        # Both calls fail
        mock_get.side_effect = [
            Exception("Open-Meteo error"),
            Exception("ECCC error")
        ]

        result = fetch_wind_data()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()