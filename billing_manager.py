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
        print("\n" + "="*60)
        print("AWS BILLING REPORT")
        print("="*60)
        
        period = report.get('period', {})
        print(f"Period: {period.get('start_date', 'N/A')} to {period.get('end_date', 'N/A')}")
        print(f"Total Cost: {report.get('currency', 'USD')} {report.get('total_cost', 0):.2f}")
        print()
        
        # Display costs by service
        costs_by_service = report.get('costs_by_service', {})
        if costs_by_service:
            print("COSTS BY SERVICE:")
            print("-" * 30)
            sorted_services = sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True)
            
            for service, cost in sorted_services:
                total_cost = report.get('total_cost', 0)
                percentage = (cost / total_cost * 100) if total_cost > 0.01 else 0
                print(f"{service:<30} {report.get('currency', 'USD')} {cost:>8.2f} ({percentage:>5.1f}%)")
        else:
            print("No significant costs found for this period.")
        
        print()
        
        # Display costs by usage type
        costs_by_usage = report.get('costs_by_usage_type', {})
        if costs_by_usage:
            print("COSTS BY USAGE TYPE:")
            print("-" * 30)
            sorted_usage = sorted(costs_by_usage.items(), key=lambda x: x[1], reverse=True)
            
            for usage_type, cost in sorted_usage[:10]:  # Show top 10
                total_cost = report.get('total_cost', 0)
                percentage = (cost / total_cost * 100) if total_cost > 0.01 else 0
                print(f"{usage_type:<30} {report.get('currency', 'USD')} {cost:>8.2f} ({percentage:>5.1f}%)")
        
        print()
        
        # Display daily costs
        daily_costs = report.get('daily_costs', [])
        if daily_costs:
            print("DAILY COST TREND:")
            print("-" * 30)
            for day in daily_costs:
                date = day.get('date', 'N/A')
                cost = day.get('cost', 0)
                print(f"{date:<12} {report.get('currency', 'USD')} {cost:>8.2f}")
        
        print("="*60)
        print(f"Report generated at: {report.get('generated_at', 'N/A')}")
        print("="*60)
    
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