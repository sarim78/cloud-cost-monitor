import json
from src.cost_explorer import get_daily_spend, get_projected_monthly_spend, get_top_services
from src.cloudwatch import get_all_metrics
from src.anomaly_detector import run_all_checks
from src.notifier import send_alert, send_daily_summary
from src.database import log_alert


# Entry point — AWS Lambda calls this function on the EventBridge 24hr schedule
def lambda_handler(event, context):
    """Main Lambda handler — orchestrates data fetching, detection, alerting, and logging."""
    print("Cloud Cost Monitor starting...")

    # Step 1 — Fetch spend data from Cost Explorer
    print("  Fetching cost data...")
    daily_spend = get_daily_spend()
    projected_spend = get_projected_monthly_spend()
    top_services = get_top_services()

    print(f"  Daily spend     : ${daily_spend:.2f}")
    print(f"  Projected month : ${projected_spend:.2f}")

    # Step 2 — Fetch resource metrics from CloudWatch
    print("  Fetching CloudWatch metrics...")
    metrics = get_all_metrics()

    print(f"  EC2 CPU         : {metrics['ec2_cpu_utilization']}%")
    print(f"  Lambda errors   : {metrics['lambda_errors']}")
    print(f"  Lambda calls    : {metrics['lambda_invocations']}")
    print(f"  RDS connections : {metrics['rds_connections']}")

    # Step 3 — Run anomaly detection across all data points
    print("  Running anomaly checks...")
    alerts = run_all_checks(daily_spend, projected_spend, metrics)

    # Step 4 — Send alerts or daily summary via SNS
    if alerts:
        print(f"  {len(alerts)} anomaly(s) detected — sending alert...")
        send_alert(alerts, daily_spend, projected_spend, top_services)

        # Log each triggered alert to SQLite
        for alert in alerts:
            log_alert(
                alert_type=alert["alert_type"],
                message=alert["message"],
                daily_spend=daily_spend,
                threshold=alert.get("threshold"),
                projected=projected_spend
            )
    else:
        print("  No anomalies detected — sending daily summary...")
        send_daily_summary(daily_spend, projected_spend, top_services)

    print("Cloud Cost Monitor finished.")

    # Return a summary response for Lambda logs
    return {
        "statusCode": 200,
        "body": json.dumps({
            "daily_spend": daily_spend,
            "projected_spend": projected_spend,
            "alerts_triggered": len(alerts),
            "metrics": metrics
        })
    }


# Allow local testing without deploying to Lambda
if __name__ == "__main__":
    result = lambda_handler({}, {})
    print("\nResponse:")
    print(json.dumps(json.loads(result["body"]), indent=2))