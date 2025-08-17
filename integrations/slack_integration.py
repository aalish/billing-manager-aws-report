"""
Slack integration for sending billing reports.
"""
import requests
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Handles Slack integration for billing notifications."""
    
    def __init__(self, webhook_url: str):
        """
        Initialize Slack integration.
        
        Args:
            webhook_url: Slack webhook URL for sending messages
        """
        self.webhook_url = webhook_url
    
    def format_billing_message(self, billing_report: Dict[str, Any]) -> str:
        """
        Format billing report into a readable Slack message.
        
        Args:
            billing_report: Billing report data
            
        Returns:
            Formatted message string
        """
        period = billing_report['period']
        total_cost = billing_report['total_cost']
        credits = billing_report.get('credits', 0)
        net_cost = billing_report.get('net_cost', 0)
        currency = billing_report['currency']
        
        # Determine period type for display
        period_type = period.get('period_type', 'd')
        period_count = period.get('period_count', 7)
        
        if period_type == 'm':
            period_text = f"month{'s' if period_count > 1 else ''}"
        else:
            period_text = f"day{'s' if period_count > 1 else ''}"
        
        # Build message with credits
        message = f"Charges on Credit: {currency} {total_cost:.2f}"
        if credits < 0:
            message += f"\nRemaining Credit: {currency} {abs(credits):.2f}"
        if net_cost >= 0:
            message += f"\nNet Remaining Charges: {currency} {net_cost:.2f}"
        else:
            message += f"\nNet Remaining Charges: {currency} 0.00"
        
        return message
    
    def send_message(self, message: str) -> bool:
        """
        Send message to Slack via webhook.
        
        Args:
            message: Message to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "text": message,
                "mrkdwn": True
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Message sent to Slack successfully")
                return True
            else:
                logger.error(f"Failed to send message to Slack. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to Slack: {e}")
            return False
    
    def send_billing_report(self, billing_report: Dict[str, Any]) -> bool:
        """
        Send billing report to Slack.
        
        Args:
            billing_report: Billing report data
            
        Returns:
            True if successful, False otherwise
        """
        message = self.format_billing_message(billing_report)
        return self.send_message(message)
    
    def send_alert(self, title: str, message: str, color: str = "warning") -> bool:
        """
        Send an alert message to Slack with custom formatting.
        
        Args:
            title: Alert title
            message: Alert message
            color: Color for the alert (good, warning, danger)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "attachments": [
                    {
                        "title": title,
                        "text": message,
                        "color": color,
                        "footer": "AWS Billing Monitor",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Alert sent to Slack: {title}")
                return True
            else:
                logger.error(f"Failed to send alert to Slack. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending alert to Slack: {e}")
            return False 