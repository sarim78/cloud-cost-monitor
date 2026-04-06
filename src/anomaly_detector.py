import os


# Thresholds — pulled from environment variables with sensible defaults
SPEND_THRESHOLD = float(os.getenv("SPEND_THRESHOLD", 50.0))
EC2_CPU_THRESHOLD = float(os.getenv("EC2_CPU_THRESHOLD", 85.0))
LAMBDA_ERROR_THRESHOLD = int(os.getenv("LAMBDA_ERROR_THRESHOLD", 50))
PROJECTED_MULTIPLIER = float(os.getenv("PROJECTED_MULTIPLIER", 1.5))


# Check if daily spend has exceeded the configured threshold
def check_daily_spend(daily_spend):
    """Return an alert dict if daily spend exceeds threshold, else None."""
    if daily_spend > SPEND_THRESHOLD:
        return {
            "alert_type": "DAILY_SPEND",
            "message": f"Daily spend of ${daily_spend:.2f} exceeded threshold of ${SPEND_THRESHOLD:.2f}.",
            "daily_spend": daily_spend,
            "threshold": SPEND_THRESHOLD
        }
    return None


# Check if projected monthly spend is 1.5x higher than expected based on threshold
def check_projected_spend(projected_spend):
    """Return an alert dict if projected monthly spend looks abnormally high."""
    projected_threshold = SPEND_THRESHOLD * 30 * PROJECTED_MULTIPLIER
    if projected_spend > projected_threshold:
        return {
            "alert_type": "PROJECTED_SPEND",
            "message": f"Projected monthly spend of ${projected_spend:.2f} exceeds expected limit of ${projected_threshold:.2f}.",
            "projected": projected_spend,
            "threshold": projected_threshold
        }
    return None


# Check if EC2 CPU is running abnormally high — may indicate a runaway instance
def check_ec2_cpu(cpu_utilization):
    """Return an alert dict if EC2 CPU utilization is above threshold."""
    if cpu_utilization > EC2_CPU_THRESHOLD:
        return {
            "alert_type": "EC2_CPU",
            "message": f"EC2 CPU utilization is at {cpu_utilization:.1f}%, above threshold of {EC2_CPU_THRESHOLD:.1f}%.",
        }
    return None


# Check if Lambda error count is spiking — may indicate broken functions burning retries
def check_lambda_errors(error_count):
    """Return an alert dict if Lambda errors exceed threshold."""
    if error_count > LAMBDA_ERROR_THRESHOLD:
        return {
            "alert_type": "LAMBDA_ERRORS",
            "message": f"Lambda recorded {error_count} errors in the last 24 hours, above threshold of {LAMBDA_ERROR_THRESHOLD}.",
        }
    return None


# Run all checks and return a list of triggered alerts
def run_all_checks(daily_spend, projected_spend, metrics):
    """Run all anomaly checks and return a list of triggered alert dicts."""
    alerts = []

    checks = [
        check_daily_spend(daily_spend),
        check_projected_spend(projected_spend),
        check_ec2_cpu(metrics.get("ec2_cpu_utilization", 0)),
        check_lambda_errors(metrics.get("lambda_errors", 0)),
    ]

    for result in checks:
        if result is not None:
            alerts.append(result)

    return alerts