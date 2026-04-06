import boto3
import os


# Initialize boto3 SNS client using AWS_REGION from environment
def get_client():
    """Create and return an SNS boto3 client."""
    return boto3.client("sns", region_name=os.getenv("AWS_REGION", "us-east-1"))


# Build a clean, readable alert email body from the list of triggered alerts
def build_message(alerts, daily_spend, projected_spend, top_services):
    """Format the alert list into a readable SNS message body."""
    lines = []
    lines.append("⚠  Cloud Cost Monitor — Anomaly Detected")
    lines.append("=" * 45)
    lines.append("")

    # Spend summary
    lines.append(f"  Daily Spend     : ${daily_spend:.2f}")
    lines.append(f"  Projected Month : ${projected_spend:.2f}")
    lines.append("")

    # Triggered alerts
    lines.append("  Anomalies Detected:")
    for alert in alerts:
        lines.append(f"    ✗ {alert['message']}")
    lines.append("")

    # Top services by cost
    if top_services:
        lines.append("  Top Services by Cost:")
        for svc in top_services:
            lines.append(f"    {svc['service']:<30} ${svc['cost']:.2f}")
    lines.append("")
    lines.append("=" * 45)

    return "\n".join(lines)


# Send the formatted alert to the configured SNS topic
def send_alert(alerts, daily_spend, projected_spend, top_services):
    """Publish an alert message to the SNS topic."""
    client = get_client()

    topic_arn = os.getenv("SNS_TOPIC_ARN")
    if not topic_arn:
        raise ValueError("SNS_TOPIC_ARN is not set in environment variables.")

    message = build_message(alerts, daily_spend, projected_spend, top_services)

    client.publish(
        TopicArn=topic_arn,
        Subject="⚠ Cloud Cost Monitor — Spending Anomaly Detected",
        Message=message
    )

    print(f"  Alert sent to SNS topic: {topic_arn}")


# Send a daily summary even when no anomalies are detected — for visibility
def send_daily_summary(daily_spend, projected_spend, top_services):
    """Publish a daily cost summary to SNS regardless of anomalies."""
    client = get_client()

    topic_arn = os.getenv("SNS_TOPIC_ARN")
    if not topic_arn:
        raise ValueError("SNS_TOPIC_ARN is not set in environment variables.")

    lines = []
    lines.append("✅  Cloud Cost Monitor — Daily Summary")
    lines.append("=" * 45)
    lines.append("")
    lines.append(f"  Daily Spend     : ${daily_spend:.2f}")
    lines.append(f"  Projected Month : ${projected_spend:.2f}")
    lines.append("")

    if top_services:
        lines.append("  Top Services by Cost:")
        for svc in top_services:
            lines.append(f"    {svc['service']:<30} ${svc['cost']:.2f}")

    lines.append("")
    lines.append("  No anomalies detected.")
    lines.append("=" * 45)

    client.publish(
        TopicArn=topic_arn,
        Subject="✅ Cloud Cost Monitor — Daily Summary",
        Message="\n".join(lines)
    )

    print("  Daily summary sent to SNS topic.")