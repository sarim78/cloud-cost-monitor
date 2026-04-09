import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path so we can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import cost_explorer


# Helpers 
def mock_cost_response(amount):
    """Helper to build a fake Cost Explorer API response."""
    return {
        "ResultsByTime": [
            {
                "Total": {
                    "UnblendedCost": {
                        "Amount": str(amount)
                    }
                },
                "Groups": []
            }
        ]
    }


def mock_grouped_cost_response(services):
    """Helper to build a fake grouped Cost Explorer response for top services."""
    groups = [
        {
            "Keys": [name],
            "Metrics": {
                "UnblendedCost": {
                    "Amount": str(cost)
                }
            }
        }
        for name, cost in services
    ]
    return {
        "ResultsByTime": [
            {
                "Total": {},
                "Groups": groups
            }
        ]
    }


# Get_daily_spend 
class TestGetDailySpend:

    # Should return correct daily spend from API response
    @patch("cost_explorer.get_client")
    def test_returns_correct_amount(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_cost_response(73.42)
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_daily_spend()
        assert result == 73.42

    # Should return 0.0 when spend is zero
    @patch("cost_explorer.get_client")
    def test_returns_zero_spend(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_cost_response(0.0)
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_daily_spend()
        assert result == 0.0

    # Should round to 2 decimal places
    @patch("cost_explorer.get_client")
    def test_rounds_to_two_decimals(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_cost_response(12.3456789)
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_daily_spend()
        assert result == 12.35


# Get_monthly_spend
class TestGetMonthlySpend:

    # Should return correct monthly spend from API response
    @patch("cost_explorer.get_client")
    def test_returns_correct_amount(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_cost_response(320.50)
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_monthly_spend()
        assert result == 320.50

    # Should return 0.0 at the start of a billing cycle
    @patch("cost_explorer.get_client")
    def test_returns_zero_at_start_of_month(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_cost_response(0.0)
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_monthly_spend()
        assert result == 0.0


# Get_top_services
class TestGetTopServices:

    # Should return services sorted by cost descending
    @patch("cost_explorer.get_client")
    def test_returns_sorted_by_cost(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_grouped_cost_response([
            ("AWS Lambda", 10.0),
            ("Amazon EC2", 50.0),
            ("Amazon RDS", 25.0)
        ])
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_top_services()
        assert result[0]["service"] == "Amazon EC2"
        assert result[1]["service"] == "Amazon RDS"
        assert result[2]["service"] == "AWS Lambda"

    # Should return only the top N services
    @patch("cost_explorer.get_client")
    def test_returns_correct_limit(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_grouped_cost_response([
            ("Service A", 10.0),
            ("Service B", 20.0),
            ("Service C", 30.0),
            ("Service D", 40.0),
            ("Service E", 50.0),
            ("Service F", 60.0),
        ])
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_top_services(limit=3)
        assert len(result) == 3

    # Should exclude services with zero cost
    @patch("cost_explorer.get_client")
    def test_excludes_zero_cost_services(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cost_and_usage.return_value = mock_grouped_cost_response([
            ("Amazon EC2", 50.0),
            ("AWS Glue", 0.0),
        ])
        mock_get_client.return_value = mock_client

        result = cost_explorer.get_top_services()
        names = [s["service"] for s in result]
        assert "AWS Glue" not in names