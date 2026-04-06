import boto3
import os
from datetime import datetime, timedelta

# Initialize boto3 CloudWatch client using AWS_REGION from environment
def get_client():
    """Create and return a CloudWatch boto3 client."""
    return boto3.client("cloudwatch", region_name=os.getenv("AWS_REGION", "us-east-1"))
 
# Fetch average EC2 CPU usage: high CPU may indicate runaway instances driving up cost
def get_ec2_cpu_utilization():
    """Get the average EC2 CPU utilization over the last 24 hours."""
    client = get_client()
 
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
 
    response = client.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Average"]
    )
 
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0.0
 
    avg = sum(d["Average"] for d in datapoints) / len(datapoints)
    return round(avg, 2)
 
# Count total Lambda invocations: spike in calls can signal unexpected usage or abuse
def get_lambda_invocations():
    """Get total Lambda invocations over the last 24 hours."""
    client = get_client()
 
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
 
    response = client.get_metric_statistics(
        Namespace="AWS/Lambda",
        MetricName="Invocations",
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Sum"]
    )
 
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0
 
    return int(sum(d["Sum"] for d in datapoints))
 
# Count total Lambda errors: high error rate may indicate broken functions burning retries
def get_lambda_errors():
    """Get total Lambda errors over the last 24 hours."""
    client = get_client()
 
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
 
    response = client.get_metric_statistics(
        Namespace="AWS/Lambda",
        MetricName="Errors",
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Sum"]
    )
 
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0
 
    return int(sum(d["Sum"] for d in datapoints))
 
# Fetch average RDS connections: unusually high connections can signal connection leaks
def get_rds_connections():
    """Get the average number of active RDS database connections over the last 24 hours."""
    client = get_client()
 
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
 
    response = client.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName="DatabaseConnections",
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=["Average"]
    )
 
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0.0
 
    avg = sum(d["Average"] for d in datapoints) / len(datapoints)
    return round(avg, 2)
 
# Aggregate all metrics into a single dict for the anomaly detector to consume
def get_all_metrics():
    """Return a summary dictionary of all CloudWatch metrics."""
    return {
        "ec2_cpu_utilization": get_ec2_cpu_utilization(),
        "lambda_invocations": get_lambda_invocations(),
        "lambda_errors": get_lambda_errors(),
        "rds_connections": get_rds_connections()
    }