# Cloud Cost Monitor
> 🚧 **Work in Progress** --> This project is actively under development. Core modules are scaffolded and logic is being implemented. AWS deployment and live testing coming soon.
A serverless AWS tool that monitors cloud spending and resource usage, detects anomalies, and sends real-time alerts before costs spiral out of control.

Built with AWS Lambda, Cost Explorer, CloudWatch, and SNS.

---

## Overview

Cloud Cost Monitor runs automatically every 24 hours as a scheduled Lambda function. It pulls your AWS spending and resource usage data, applies threshold-based anomaly detection, and fires an alert via email or SMS if something looks off. Every alert is logged to a local database for historical tracking.

---

## Features

- Queries AWS Cost Explorer for daily and monthly spend data
- Monitors CloudWatch resource metrics (EC2, Lambda, and more)
- Detects spending spikes and projected budget overages
- Sends real-time email and SMS alerts via AWS SNS
- Logs all alerts to a SQLite database for trend tracking over time
- Runs fully serverless; no infrastructure to manage

---

## Architecture

```
EventBridge (24hr schedule)
        ↓
  Lambda Function
     ↙        ↘
Cost Explorer  CloudWatch
     ↘        ↙
  Anomaly Detector
        ↓
     SNS Alert
  (Email / SMS)
        ↓
   SQLite Log
```

---

## Requirements

- Python 3.11+
- AWS account with the following services enabled:
  - AWS Lambda
  - AWS Cost Explorer
  - AWS CloudWatch
  - AWS SNS
- AWS CLI configured locally (`aws configure`)

---

## Setup

1. Clone the repo
```bash
git clone https://github.com/sarim78/cloud-cost-monitor
cd cloud-cost-monitor
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
```bash
cp .env.example .env
```
Then fill in your values in `.env`:
```
AWS_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:your-account-id:your-topic
SPEND_THRESHOLD=50
```

4. Run locally
```bash
python src/lambda_function.py
```

5. Deploy to AWS Lambda
```bash
zip -r function.zip src/ requirements.txt
aws lambda update-function-code --function-name cloud-cost-monitor --zip-file fileb://function.zip
```

---

## Project Structure

```
cloud-cost-monitor/
├── src/
│   ├── lambda_function.py     # Entry point — orchestrates everything
│   ├── cost_explorer.py       # Queries AWS Cost Explorer API
│   ├── cloudwatch.py          # Queries CloudWatch metrics
│   ├── anomaly_detector.py    # Threshold + spike detection logic
│   ├── notifier.py            # Sends SNS alerts
│   └── database.py            # Logs alert history to SQLite
├── tests/
│   ├── test_cost_explorer.py
│   ├── test_anomaly_detector.py
│   └── test_notifier.py
├── data/
│   └── alerts.db              # SQLite database (gitignored)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `AWS_REGION` | Your AWS region (e.g. `us-east-1`) |
| `SNS_TOPIC_ARN` | ARN of your SNS topic for alerts |
| `SPEND_THRESHOLD` | Daily spend threshold in USD before alert fires |

---

## Example Alert

```
Subject: ⚠ Cloud Cost Monitor — Spending Anomaly Detected

Daily spend has exceeded your threshold of $50.00.
Current daily spend: $73.42
Projected monthly spend: $2,202.60

Top services by cost:
  EC2: $41.20
  RDS: $18.90
  Lambda: $13.32

Logged at: 2026-04-05 08:00:00 UTC
```

---

## License
MIT
