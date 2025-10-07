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
        Display billing report in console with comprehensive credit information.
        
        Args:
            report: Billing report data
        """
        period = report.get('period', {})
        costs = report.get('costs', {})
        credits = report.get('credits', {})
        currency = report.get('currency', 'USD')
        
        # Determine period type for display
        period_type = period.get('period_type', 'd')
        period_count = period.get('period_count', 1)
        
        if period_type == 'm':
            period_text = f"month{'s' if period_count > 1 else ''}"
        else:
            period_text = f"day{'s' if period_count > 1 else ''}"
        
        print("\n" + "=" * 60)
        print(f"     AWS BILLING REPORT - {period_count} {period_text.upper()}")
        print("=" * 60)
        
        # Period information
        print(f"Period: {period.get('start_date')} to {period.get('end_date')}")
        print()
        
        # Credit Overview - get accurate remaining credits
        total_credits = 5000
        expiration = 'Unknown'
        
        # Get fresh credit calculations from AWS
        try:
            used_lifetime = self.aws_analyzer.get_credits_used_lifetime()
            remaining_credits = self.aws_analyzer.get_remaining_credits()
        except:
            # Fallback values
            used_lifetime = 0
            remaining_credits = total_credits
        
        print("💳 CREDIT OVERVIEW:")
        print(f"   Total Credits Available: {currency} {total_credits:.2f}")
        print(f"   Credits Used (Lifetime): {currency} {used_lifetime:.2f}")
        print(f"   Credits Remaining:       {currency} {remaining_credits:.2f}")
        print(f"   Credit Expiration:       {expiration}")
        
        # Calculate percentage used
        if total_credits > 0:
            percent_used = (used_lifetime / total_credits) * 100
            percent_remaining = 100 - percent_used
            print(f"   Usage Percentage:        {percent_used:.1f}% used, {percent_remaining:.1f}% remaining")
        print()
        
        # Current Period Costs - handle both dict and legacy formats
        if isinstance(costs, dict):
            usage_cost = costs.get('usage_cost_period', 0)
            net_cost = costs.get('net_cost_period', 0)
        else:
            # Legacy format
            usage_cost = report.get('total_cost', 0)
            net_cost = report.get('net_cost', 0)
            
        if isinstance(credits, dict):
            credits_applied = credits.get('applied_this_period', 0)
        else:
            credits_applied = abs(credits) if credits < 0 else 0
        
        print("📊 CURRENT PERIOD COSTS:")
        print(f"   Actual Usage Cost:       {currency} {usage_cost:.2f}")
        print(f"   Credits Applied:         {currency} {credits_applied:.2f}")
        print(f"   Net Cost (You Pay):      {currency} {max(0, net_cost):.2f}")
        print()
        
        # Credit burn rate estimation
        if period_count > 0 and credits_applied > 0:
            monthly_burn_rate = credits_applied * (30 / (period_count * (30 if period_type == 'm' else 1)))
            if monthly_burn_rate > 0 and remaining_credits > 0:
                months_remaining = remaining_credits / monthly_burn_rate
                print("⏱️  CREDIT BURN RATE ANALYSIS:")
                print(f"   Estimated Monthly Burn:  {currency} {monthly_burn_rate:.2f}")
                print(f"   Est. Months Remaining:   {months_remaining:.1f} months")
                print()
        
        # Status indicators
        if remaining_credits > 1000:
            status = "✅ HEALTHY - Credits are sufficient"
        elif remaining_credits > 500:
            status = "⚠️  MONITOR - Credits getting low"
        elif remaining_credits > 0:
            status = "🚨 CRITICAL - Credits running out soon!"
        else:
            status = "❌ EXHAUSTED - No credits remaining!"
        
        print(f"Status: {status}")
        print("=" * 60)
    
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
        Check if AWS credentials are properly configured in .env file.
        
        Returns:
            True if credentials are available, False otherwise
        """
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"Missing required environment variable in .env file: {var}")
                return False
        
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        logger.info(f"AWS credentials found in .env file (region: {aws_region})")
        return True


def main():
    """Main function to run the billing analysis."""
    billing_manager = BillingManager()
    
    # Check AWS credentials
    if not billing_manager.check_aws_credentials():
        print("ERROR: AWS credentials not found in .env file.")
        print("Please ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in .env")
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