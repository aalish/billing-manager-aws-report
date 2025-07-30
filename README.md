# Python AWS Billing Monitor

A Python-based billing configuration project that analyzes AWS costs and sends notifications through various integrations.

## Features

- **AWS Cost Analysis**: Fetches billing data from AWS Cost Explorer API
- **Flexible Period Configuration**: Support for daily (d) and monthly (m) billing periods
- **Service Breakdown**: Detailed cost analysis by AWS service and usage type
- **Slack Integration**: Send formatted billing reports via Slack webhook
- **Extensible Architecture**: Easy to add new integrations (email, Teams, etc.)
- **Development Mode**: Console output for better development experience

## Project Structure

```
python-billing/
├── aws_billing.py          # AWS Cost Explorer integration
├── billing_manager.py      # Main orchestration logic
├── config.py              # Configuration settings
├── integrations/          # Notification integrations
│   ├── __init__.py
│   └── slack_integration.py
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
└── README.md            # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=us-east-1

# Slack Integration
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
```

### 3. AWS Permissions

Ensure your AWS credentials have the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetDimensionValues"
            ],
            "Resource": "*"
        }
    ]
}
```

### 4. Slack Webhook Setup (Optional)

1. Go to your Slack workspace
2. Create a new app or use an existing one
3. Enable Incoming Webhooks
4. Create a webhook for your desired channel
5. Copy the webhook URL to your `.env` file

## Configuration

### Billing Period

Edit `config.py` to customize the billing period:

```python
# For last 7 days (default)
config.billing.period_type = 'd'  # 'd' for days, 'm' for months
config.billing.period_count = 7

# For last 3 months
config.billing.period_type = 'm'
config.billing.period_count = 3
```

### Integrations

Configure which integrations to use:

```python
# Enable/disable Slack
config.integrations.slack_enabled = True

# Future integrations
# config.integrations.email_enabled = True
# config.integrations.teams_enabled = True
```

## Usage

### Basic Usage

Run the billing analysis:

```bash
python billing_manager.py
```

This will:
1. Fetch AWS billing data for the configured period
2. Display a detailed report in the console
3. Send notifications to configured integrations (if enabled)

### Programmatic Usage

```python
from billing_manager import BillingManager

# Initialize the billing manager
billing_manager = BillingManager()

# Run analysis with notifications
report = billing_manager.run_billing_analysis(send_notifications=True)

# Run analysis without notifications (development mode)
report = billing_manager.run_billing_analysis(send_notifications=False)

# Access the report data
print(f"Total cost: {report['total_cost']}")
print(f"Services: {report['costs_by_service']}")
```

### Custom Period Analysis

```python
from aws_billing import AWSBillingAnalyzer
from config import config

# Temporarily change the period
config.billing.period_type = 'm'
config.billing.period_count = 1

# Create analyzer with custom period
analyzer = AWSBillingAnalyzer()
report = analyzer.generate_billing_report()
```

## Sample Output

```
============================================================
AWS BILLING REPORT
============================================================
Period: 2024-01-01 to 2024-01-08
Total Cost: USD 156.78

COSTS BY SERVICE:
------------------------------
Amazon EC2                    USD    89.45 (57.1%)
Amazon S3                     USD    34.23 (21.8%)
Amazon RDS                    USD    22.10 (14.1%)
AWS Lambda                    USD    11.00  (7.0%)

COSTS BY USAGE TYPE:
------------------------------
EC2: m5.large                 USD    45.67 (29.1%)
S3: StandardStorage           USD    28.90 (18.4%)
RDS: db.t3.micro              USD    22.10 (14.1%)
Lambda: Duration              USD    11.00  (7.0%)

DAILY COST TREND:
------------------------------
2024-01-01     USD    18.45
2024-01-02     USD    22.10
2024-01-03     USD    19.87
2024-01-04     USD    21.34
2024-01-05     USD    20.12
============================================================
Report generated at: 2024-01-08T10:30:00
============================================================
```

## Slack Integration

The Slack integration sends formatted messages with:

- Total cost for the period
- Breakdown by AWS service with percentages
- Daily cost trend
- Timestamp of report generation

### Sample Slack Message

```
AWS Billing Report
Period: 2024-01-01 to 2024-01-08
Total Cost: USD 156.78

Costs by Service:
• Amazon EC2: USD 89.45 (57.1%)
• Amazon S3: USD 34.23 (21.8%)
• Amazon RDS: USD 22.10 (14.1%)
• AWS Lambda: USD 11.00 (7.0%)

Daily Cost Trend:
• 01/04: USD 21.34
• 01/05: USD 20.12
• 01/06: USD 19.87
• 01/07: USD 22.10
• 01/08: USD 18.45

Report generated at 2024-01-08 10:30:00
```

## Future Enhancements

### Planned Integrations

- **Email Integration**: Send reports via SMTP
- **Microsoft Teams**: Teams webhook integration
- **Discord**: Discord webhook integration
- **Web Dashboard**: Web-based dashboard for cost visualization

### LLM Integration

Future plans include LLM integration for:
- Natural language cost analysis
- Automated cost optimization recommendations
- Anomaly detection and alerts
- Cost forecasting

## Development

### Running in Development Mode

For development, notifications are disabled by default. The system will:

1. Fetch AWS billing data
2. Display detailed console output
3. Skip sending notifications

To enable notifications during development, set `send_notifications=True` in the `run_billing_analysis()` call.

### Adding New Integrations

1. Create a new integration class in the `integrations/` directory
2. Implement the required methods (similar to `SlackIntegration`)
3. Add configuration options in `config.py`
4. Update `BillingManager` to use the new integration

Example integration structure:

```python
class NewIntegration:
    def __init__(self, config):
        # Initialize integration
        
    def send_billing_report(self, report):
        # Send report via this integration
        
    def send_alert(self, title, message):
        # Send alert via this integration
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**: Ensure your `.env` file has valid AWS credentials
2. **Permission Denied**: Check that your AWS user has Cost Explorer permissions
3. **Slack Webhook Error**: Verify your Slack webhook URL is correct and active
4. **No Billing Data**: Ensure you have AWS usage in the specified period

### Debug Mode

Enable debug logging by modifying the logging level in `billing_manager.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is open source and available under the MIT License. 