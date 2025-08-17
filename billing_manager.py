"""
Main billing manager that orchestrates AWS billing analysis and integrations.
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from aws_billing import AWSBillingAnalyzer
from integrations.slack_integration import SlackIntegration
from config import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BillingManager:
    """Main class for managing billing analysis and notifications."""
    
    def __init__(self):
        """Initialize the billing manager."""
        self.aws_analyzer = AWSBillingAnalyzer()
        self.slack_integration = None
        
        # Initialize Slack integration if enabled
        if config.integrations.slack_enabled:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if webhook_url:
                self.slack_integration = SlackIntegration(webhook_url)
                logger.info("Slack integration initialized")
            else:
                logger.warning("Slack webhook URL not found in environment variables")
    
    def generate_and_display_report(self) -> Dict[str, Any]:
        """
        Generate billing report and display it in console.
        
        Returns:
            Billing report data
        """
        logger.info("Generating billing report...")
        
        try:
            report = self.aws_analyzer.generate_billing_report()
            self._display_report_console(report)
            return report
            
        except Exception as e:
            logger.error(f"Error generating billing report: {e}")
            return {}
    
    def _display_report_console(self, report: Dict[str, Any]) -> None:
        """
        Display billing report in console for development.
        
        Args:
            report: Billing report data
        """
        period = report.get('period', {})
        total_cost = report.get('total_cost', 0)
        credits = report.get('credits', 0)
        net_cost = report.get('net_cost', 0)
        currency = report.get('currency', 'USD')
        
        # Determine period type for display
        period_type = period.get('period_type', 'd')
        period_count = period.get('period_count', 7)
        
        if period_type == 'm':
            period_text = f"month{'s' if period_count > 1 else ''}"
        else:
            period_text = f"day{'s' if period_count > 1 else ''}"
        
        print(f"Charges on Credit: {currency} {total_cost:.2f}")
        if credits < 0:
            print(f"Remaining Credit: {currency} {abs(credits):.2f}")
        if net_cost >= 0:
            print(f"Net Remaining Charges: {currency} {net_cost:.2f}")
        else:
            print(f"Net Remaining Charges: {currency} 0.00")
    
    def send_notifications(self, report: Dict[str, Any]) -> None:
        """
        Send billing report to all configured integrations.
        
        Args:
            report: Billing report data
        """
        logger.info("Sending notifications...")
        
        # Send to Slack if configured
        if self.slack_integration:
            try:
                success = self.slack_integration.send_billing_report(report)
                if success:
                    logger.info("Billing report sent to Slack successfully")
                else:
                    logger.error("Failed to send billing report to Slack")
            except Exception as e:
                logger.error(f"Error sending to Slack: {e}")
        
        # Future integrations can be added here
        # if config.integrations.email_enabled:
        #     # Send email notification
        #     pass
        
        # if config.integrations.teams_enabled:
        #     # Send Teams notification
        #     pass
    
    def run_billing_analysis(self, send_notifications: bool = True) -> Dict[str, Any]:
        """
        Run complete billing analysis workflow.
        
        Args:
            send_notifications: Whether to send notifications to integrations
            
        Returns:
            Billing report data
        """
        logger.info("Starting billing analysis...")
        
        # Generate and display report
        report = self.generate_and_display_report()
        
        if not report:
            logger.error("Failed to generate billing report")
            return {}
        
        # Send notifications if requested
        if send_notifications:
            self.send_notifications(report)
        
        logger.info("Billing analysis completed")
        return report
    
    def check_aws_credentials(self) -> bool:
        """
        Check if AWS credentials are properly configured.
        
        Returns:
            True if credentials are available, False otherwise
        """
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"Missing required environment variable: {var}")
                return False
        
        logger.info("AWS credentials found")
        return True


def main():
    """Main function to run the billing analysis."""
    billing_manager = BillingManager()
    
    # Check AWS credentials
    if not billing_manager.check_aws_credentials():
        print("ERROR: AWS credentials not found. Please check your .env file.")
        return
    
    # Run billing analysis
    # Enable notifications if Slack webhook is configured
    send_notifications = bool(os.getenv('SLACK_WEBHOOK_URL'))
    report = billing_manager.run_billing_analysis(send_notifications=send_notifications)
    
    if report:
        print("\nBilling analysis completed successfully!")
    else:
        print("\nBilling analysis failed!")


if __name__ == "__main__":
    main() 