"""
Configuration settings for the billing project.
"""
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime, timedelta


class BillingConfig(BaseModel):
    """Configuration for billing period and settings."""
    
    # Billing period: 'd' for days, 'm' for months
    period_type: Literal['d', 'm'] = 'm'
    
    # Number of periods to look back (default: 1 month)
    period_count: int = 1
    
    # AWS region for billing data
    aws_region: str = 'us-east-1'
    
    # Currency for billing (default: USD)
    currency: str = 'USD'
    
    # Minimum cost threshold to report (in currency units)
    min_cost_threshold: float = 0.01


class IntegrationConfig(BaseModel):
    """Configuration for different integrations."""
    
    # Currently supported integrations
    integrations: List[str] = ['slack']
    
    # Slack specific settings
    slack_enabled: bool = True
    slack_channel: str = '#billing-alerts'
    
    # Future integrations can be added here
    # email_enabled: bool = False
    # teams_enabled: bool = False


class Config(BaseModel):
    """Main configuration class."""
    
    billing: BillingConfig = BillingConfig()
    integrations: IntegrationConfig = IntegrationConfig()
    
    def get_billing_period(self) -> tuple[datetime, datetime]:
        """
        Calculate the billing period start and end dates.
        
        Returns:
            tuple: (start_date, end_date) for the billing period
        """
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if self.billing.period_type == 'd':
            start_date = end_date - timedelta(days=self.billing.period_count)
        elif self.billing.period_type == 'm':
            # Approximate month calculation
            start_date = end_date - timedelta(days=self.billing.period_count * 30)
        else:
            raise ValueError(f"Unsupported period type: {self.billing.period_type}")
        
        return start_date, end_date


# Default configuration instance
config = Config() 