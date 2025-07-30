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
        currency = billing_report['currency']
        costs_by_service = billing_report['costs_by_service']
        
        # Format the message
        message = f"*AWS Billing Report*\n"
        message += f"Period: {period['start_date']} to {period['end_date']}\n"
        message += f"Total Cost: {currency} {total_cost:.2f}\n\n"
        
        if costs_by_service:
            message += "*Costs by Service:*\n"
            # Sort services by cost (highest first)
            sorted_services = sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True)
            
            for service, cost in sorted_services:
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                message += f"• {service}: {currency} {cost:.2f} ({percentage:.1f}%)\n"
        else:
            message += "*No significant costs found for this period.*\n"
        
        # Add daily cost trend if available
        daily_costs = billing_report.get('daily_costs', [])
        if daily_costs:
            message += f"\n*Daily Cost Trend:*\n"
            for day in daily_costs[-5:]:  # Show last 5 days
                date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%m/%d')
                message += f"• {date}: {currency} {day['cost']:.2f}\n"
        
        message += f"\n_Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
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