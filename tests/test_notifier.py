import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path so we can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import notifier


# Fixtures 
@pytest.fixture
def sample_alerts():
    """Sample alert list for testing."""
    return [
        {
            "alert_type": "DAILY_SPEND",
            "message": "Daily spend of $73.42 exceeded threshold of $50.00.",
            "daily_spend": 73.42,
            "threshold": 50.0
        }
    ]


@pytest.fixture
def sample_top_services():
    """Sample top services list for testing."""
    return [
        {"service": "Amazon EC2", "cost": 41.20},
        {"service": "Amazon RDS", "cost": 18.90},
        {"service": "AWS Lambda", "cost": 13.32}
    ]


# Build_message
class TestBuildMessage:

    # Should include daily spend in the message body
    def test_includes_daily_spend(self, sample_alerts, sample_top_services):
        message = notifier.build_message(sample_alerts, 73.42, 2202.60, sample_top_services)
        assert "73.42" in message

    # Should include projected spend in the message body
    def test_includes_projected_spend(self, sample_alerts, sample_top_services):
        message = notifier.build_message(sample_alerts, 73.42, 2202.60, sample_top_services)
        assert "2202.60" in message

    # Should include alert message text in the body
    def test_includes_alert_message(self, sample_alerts, sample_top_services):
        message = notifier.build_message(sample_alerts, 73.42, 2202.60, sample_top_services)
        assert "Daily spend of $73.42" in message

    # Should include top services in the message body
    def test_includes_top_services(self, sample_alerts, sample_top_services):
        message = notifier.build_message(sample_alerts, 73.42, 2202.60, sample_top_services)
        assert "Amazon EC2" in message

    # Should handle empty top services list without crashing
    def test_handles_empty_services(self, sample_alerts):
        message = notifier.build_message(sample_alerts, 73.42, 2202.60, [])
        assert "73.42" in message


# Send_alert 
class TestSendAlert:

    # Should call SNS publish once with correct topic ARN
    @patch("notifier.get_client")
    def test_calls_sns_publish(self, mock_get_client, sample_alerts, sample_top_services):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:123456789:test-topic"}):
            notifier.send_alert(sample_alerts, 73.42, 2202.60, sample_top_services)

        mock_client.publish.assert_called_once()

    # Should raise ValueError if SNS_TOPIC_ARN is not set
    @patch("notifier.get_client")
    def test_raises_if_no_topic_arn(self, mock_get_client, sample_alerts, sample_top_services):
        mock_get_client.return_value = MagicMock()

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("SNS_TOPIC_ARN", None)
            with pytest.raises(ValueError, match="SNS_TOPIC_ARN"):
                notifier.send_alert(sample_alerts, 73.42, 2202.60, sample_top_services)

    # Should publish with correct subject line
    @patch("notifier.get_client")
    def test_correct_subject(self, mock_get_client, sample_alerts, sample_top_services):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:123456789:test-topic"}):
            notifier.send_alert(sample_alerts, 73.42, 2202.60, sample_top_services)

        call_kwargs = mock_client.publish.call_args[1]
        assert "Anomaly" in call_kwargs["Subject"]


# Send_daily_summary
class TestSendDailySummary:

    # Should call SNS publish once for daily summary
    @patch("notifier.get_client")
    def test_calls_sns_publish(self, mock_get_client, sample_top_services):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:123456789:test-topic"}):
            notifier.send_daily_summary(20.0, 400.0, sample_top_services)

        mock_client.publish.assert_called_once()

    # Should raise ValueError if SNS_TOPIC_ARN is not set
    @patch("notifier.get_client")
    def test_raises_if_no_topic_arn(self, mock_get_client, sample_top_services):
        mock_get_client.return_value = MagicMock()

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("SNS_TOPIC_ARN", None)
            with pytest.raises(ValueError, match="SNS_TOPIC_ARN"):
                notifier.send_daily_summary(20.0, 400.0, sample_top_services)

    # Should include "No anomalies detected" in daily summary message
    @patch("notifier.get_client")
    def test_summary_message_content(self, mock_get_client, sample_top_services):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {"SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:123456789:test-topic"}):
            notifier.send_daily_summary(20.0, 400.0, sample_top_services)

        call_kwargs = mock_client.publish.call_args[1]
        assert "No anomalies detected" in call_kwargs["Message"]