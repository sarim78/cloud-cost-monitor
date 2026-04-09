import pytest
import sys
import os

# Add src to path so we can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from anomaly_detector import (
    check_daily_spend,
    check_projected_spend,
    check_ec2_cpu,
    check_lambda_errors,
    run_all_checks
)


# Check_daily_spend
class TestCheckDailySpend:

    # Should return None when spend is under threshold
    def test_no_alert_under_threshold(self):
        result = check_daily_spend(30.0)
        assert result is None

    # Should return None when spend is exactly at threshold
    def test_no_alert_at_threshold(self):
        result = check_daily_spend(50.0)
        assert result is None

    # Should trigger alert when spend exceeds threshold
    def test_alert_over_threshold(self):
        result = check_daily_spend(75.0)
        assert result is not None
        assert result["alert_type"] == "DAILY_SPEND"
        assert "75.00" in result["message"]

    # Alert dict should contain daily_spend and threshold values
    def test_alert_contains_correct_values(self):
        result = check_daily_spend(99.99)
        assert result["daily_spend"] == 99.99
        assert result["threshold"] == 50.0


# Check_projected_spend
class TestCheckProjectedSpend:

    # Should return None when projected spend is within expected range
    def test_no_alert_normal_projected(self):
        result = check_projected_spend(500.0)
        assert result is None

    # Should trigger alert when projected spend far exceeds expected monthly limit
    def test_alert_high_projected(self):
        result = check_projected_spend(99999.0)
        assert result is not None
        assert result["alert_type"] == "PROJECTED_SPEND"

    # Alert dict should contain projected spend value
    def test_alert_contains_projected_value(self):
        result = check_projected_spend(99999.0)
        assert result["projected"] == 99999.0


# Check_ec2_cpu 
class TestCheckEc2Cpu:

    # Should return None when CPU is under threshold
    def test_no_alert_normal_cpu(self):
        result = check_ec2_cpu(60.0)
        assert result is None

    # Should return None when CPU is exactly at threshold
    def test_no_alert_at_threshold(self):
        result = check_ec2_cpu(85.0)
        assert result is None

    # Should trigger alert when CPU exceeds threshold
    def test_alert_high_cpu(self):
        result = check_ec2_cpu(95.0)
        assert result is not None
        assert result["alert_type"] == "EC2_CPU"
        assert "95.0" in result["message"]

    # Should return None when no EC2 instances are running
    def test_no_alert_zero_cpu(self):
        result = check_ec2_cpu(0.0)
        assert result is None


# Check_lambda_errors
class TestCheckLambdaErrors:

    # Should return None when errors are under threshold
    def test_no_alert_low_errors(self):
        result = check_lambda_errors(10)
        assert result is None

    # Should return None when errors are exactly at threshold
    def test_no_alert_at_threshold(self):
        result = check_lambda_errors(50)
        assert result is None

    # Should trigger alert when errors exceed threshold
    def test_alert_high_errors(self):
        result = check_lambda_errors(100)
        assert result is not None
        assert result["alert_type"] == "LAMBDA_ERRORS"
        assert "100" in result["message"]

    # Should return None when there are zero errors
    def test_no_alert_zero_errors(self):
        result = check_lambda_errors(0)
        assert result is None


# Run_all_checks 
class TestRunAllChecks:

    # Should return empty list when everything is within normal range
    def test_no_alerts_all_normal(self):
        metrics = {
            "ec2_cpu_utilization": 40.0,
            "lambda_errors": 5,
            "lambda_invocations": 100,
            "rds_connections": 3.0
        }
        alerts = run_all_checks(20.0, 400.0, metrics)
        assert alerts == []

    # Should return multiple alerts when multiple thresholds are exceeded
    def test_multiple_alerts_triggered(self):
        metrics = {
            "ec2_cpu_utilization": 95.0,
            "lambda_errors": 200,
            "lambda_invocations": 100,
            "rds_connections": 3.0
        }
        alerts = run_all_checks(999.0, 99999.0, metrics)
        assert len(alerts) >= 2

    # Should return exactly one alert when only daily spend is exceeded
    def test_single_alert_daily_spend(self):
        metrics = {
            "ec2_cpu_utilization": 40.0,
            "lambda_errors": 5,
            "lambda_invocations": 100,
            "rds_connections": 3.0
        }
        alerts = run_all_checks(999.0, 400.0, metrics)
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "DAILY_SPEND"