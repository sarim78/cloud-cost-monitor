import boto3
import os
from datetime import datetime, timedelta

# Cost Explorer helper functions to fetch AWS cost data for the dashboard and alerting.
def get_client():
    """Create and return a Cost Explorer boto3 client."""
    return boto3.client("ce", region_name=os.getenv("AWS_REGION", "us-east-1"))

# Get yesterday's total AWS spend in USD.
def get_daily_spend():
    """Get yesterday's total AWS spend in USD."""
    client = get_client()

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": str(yesterday),
            "End": str(today)
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"]
    )

    amount = response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
    return round(float(amount), 2)

# Get total spend for the current month so far.
def get_monthly_spend():
    """Get the total AWS spend for the current month so far."""
    client = get_client()

    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)

    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": str(start_of_month),
            "End": str(today)
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"]
    )

    amount = response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
    return round(float(amount), 2)

# Estimate total monthly spend based on current daily burn rate.
def get_projected_monthly_spend():
    """Estimate total monthly spend based on current daily burn rate."""
    today = datetime.utcnow().date()
    days_elapsed = today.day
    days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).day

    monthly_so_far = get_monthly_spend()

    if days_elapsed == 0:
        return monthly_so_far

    daily_average = monthly_so_far / days_elapsed
    projected = daily_average * days_in_month
    return round(projected, 2)

# Get top services by cost for the current month.
def get_top_services(limit=5):
    """Get the top AWS services by cost for the current month."""
    client = get_client()

    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)

    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": str(start_of_month),
            "End": str(today)
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
    )

    services = []
    for group in response["ResultsByTime"][0]["Groups"]:
        name = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        if amount > 0:
            services.append({"service": name, "cost": round(amount, 2)})

    services.sort(key=lambda x: x["cost"], reverse=True)
    return services[:limit]