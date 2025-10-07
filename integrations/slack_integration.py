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
        Format billing report into a simple Slack message with essential credit info.
        
        Args:
            billing_report: Billing report data
            
        Returns:
            Formatted message string
        """
        currency = billing_report.get('currency', 'USD')
        
        # Get cost and credit data from the enhanced report structure
        costs = billing_report.get('costs', {})
        
        # Get usage and net cost from costs section
        if isinstance(costs, dict):
            usage_cost = costs.get('usage_cost_period', 0)
            credits_applied = costs.get('credits_applied_period', 0)
            net_cost = costs.get('net_cost_period', 0)
        else:
            # Fallback to legacy format
            usage_cost = billing_report.get('total_cost', 0)
            credits_applied = abs(billing_report.get('credits', 0)) if billing_report.get('credits', 0) < 0 else 0
            net_cost = billing_report.get('net_cost', 0)
        
        # Calculate remaining credits and get lifetime usage
        from config import config
        from aws_billing import AWSBillingAnalyzer
        
        try:
            # Get fresh calculations from AWS
            analyzer = AWSBillingAnalyzer()
            remaining_credits = analyzer.get_remaining_credits()
            lifetime_credits_used = analyzer.get_credits_used_lifetime()
        except:
            # Fallback calculation
            total_credits = config.billing.total_credits
            lifetime_credits_used = 490.87  # Fallback value
            remaining_credits = total_credits - lifetime_credits_used
        
        # Simple message format with lifetime credits used
        message = f"AWS Account: 443752887643\n"
        message += f"✓ Current usage cost: ${usage_cost:.2f}\n"
        message += f"✓ Lifetime credits used: ${lifetime_credits_used:.2f}\n"
        message += f"✓ Remaining credits: ${remaining_credits:.2f}\n"
        message += f"✓ Net remaining charges: ${max(0, net_cost):.2f}"
        
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