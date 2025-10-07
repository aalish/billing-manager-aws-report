"""
AWS Billing module for fetching and analyzing billing data.
"""
import boto3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWSBillingAnalyzer:
    """Analyzes AWS billing data using Cost Explorer API."""
    
    def __init__(self):
        """Initialize the AWS billing analyzer using .env credentials."""
        # Get AWS credentials from environment variables
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', config.billing.aws_region)
        
        # Validate required credentials
        if not aws_access_key_id or not aws_secret_access_key:
            raise ValueError("AWS credentials not found in .env file. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        
        # Create boto3 client with explicit credentials from .env
        self.ce_client = boto3.client(
            'ce',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        self.start_date, self.end_date = config.get_billing_period()
        logger.info(f"AWS Cost Explorer client initialized with region: {aws_region}")
    
    def get_cost_by_service(self) -> Dict[str, float]:
        """
        Get costs grouped by AWS service for the configured period.
        
        Returns:
            Dict mapping service names to costs
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': self.start_date.strftime('%Y-%m-%d'),
                    'End': self.end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            service_costs = {}
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service_name = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if service_name not in service_costs:
                        service_costs[service_name] = 0.0
                    service_costs[service_name] += cost
            
            # Filter out services below threshold
            filtered_costs = {
                service: cost for service, cost in service_costs.items()
                if cost >= config.billing.min_cost_threshold
            }
            
            return filtered_costs
            
        except Exception as e:
            logger.error(f"Error fetching AWS billing data: {e}")
            return {}
    
    def get_cost_by_usage_type(self) -> Dict[str, float]:
        """
        Get costs grouped by usage type for more detailed analysis.
        
        Returns:
            Dict mapping usage types to costs
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': self.start_date.strftime('%Y-%m-%d'),
                    'End': self.end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
                ]
            )
            
            usage_costs = {}
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    usage_type = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if usage_type not in usage_costs:
                        usage_costs[usage_type] = 0.0
                    usage_costs[usage_type] += cost
            
            # Filter out usage types below threshold
            filtered_costs = {
                usage: cost for usage, cost in usage_costs.items()
                if cost >= config.billing.min_cost_threshold
            }
            
            return filtered_costs
            
        except Exception as e:
            logger.error(f"Error fetching AWS usage type data: {e}")
            return {}
    
    def get_daily_costs(self) -> List[Dict[str, Any]]:
        """
        Get daily cost breakdown for the period.
        
        Returns:
            List of daily cost data
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': self.start_date.strftime('%Y-%m-%d'),
                    'End': self.end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            
            daily_costs = []
            
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                cost = float(result['Total']['UnblendedCost']['Amount'])
                
                daily_costs.append({
                    'date': date,
                    'cost': cost,
                    'unit': result['Total']['UnblendedCost']['Unit']
                })
            
            return daily_costs
            
        except Exception as e:
            logger.error(f"Error fetching daily cost data: {e}")
            return []
    
    def get_total_cost(self) -> float:
        """
        Get total cost for the period.
        
        Returns:
            Total cost as float
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': self.start_date.strftime('%Y-%m-%d'),
                    'End': self.end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )
            
            total_cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
            return total_cost
            
        except Exception as e:
            logger.error(f"Error fetching total cost: {e}")
            return 0.0
    
    def get_credits(self) -> float:
        """
        Get total credits applied for the period.
        
        Returns:
            Total credits as float (negative value)
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': self.start_date.strftime('%Y-%m-%d'),
                    'End': self.end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}
                ]
            )
            
            total_credits = 0.0
            
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    record_type = group['Keys'][0]
                    if record_type == 'Credit':
                        cost = float(group['Metrics']['UnblendedCost']['Amount'])
                        total_credits += cost  # Credits are already negative
            
            return total_credits
            
        except Exception as e:
            logger.error(f"Error fetching credits: {e}")
            return 0.0
    
    def get_usage_cost(self) -> float:
        """
        Get actual usage cost (before credits) for the period.
        
        Returns:
            Usage cost as float
        """
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': self.start_date.strftime('%Y-%m-%d'),
                    'End': self.end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}
                ]
            )
            
            total_usage = 0.0
            
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    record_type = group['Keys'][0]
                    if record_type == 'Usage':
                        cost = float(group['Metrics']['UnblendedCost']['Amount'])
                        total_usage += cost
            
            return total_usage
            
        except Exception as e:
            logger.error(f"Error fetching usage cost: {e}")
            return 0.0
    
    def get_credits_used_lifetime(self) -> float:
        """
        Get total credits used from account creation until now.
        This calculates cumulative credit usage to determine remaining balance.
        
        Returns:
            Total credits used (positive value)
        """
        try:
            # Get data from maximum safe lookback (400 days = ~13.3 months)
            # This is the maximum we can reliably access via Cost Explorer API
            current_date = datetime.now()
            account_start = current_date - timedelta(days=400)
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': account_start.strftime('%Y-%m-%d'),
                    'End': current_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}
                ]
            )
            
            total_credits_used = 0.0
            
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    record_type = group['Keys'][0]
                    if record_type == 'Credit':
                        cost = float(group['Metrics']['UnblendedCost']['Amount'])
                        total_credits_used += abs(cost)  # Convert to positive
            
            return total_credits_used
            
        except Exception as e:
            logger.error(f"Error fetching lifetime credit usage: {e}")
            return 0.0
    
    def get_remaining_credits(self) -> float:
        """
        Calculate remaining credits based on total credits and actual usage from AWS.
        
        Returns:
            Remaining credits as float
        """
        total_credits = config.billing.total_credits
        credits_used = self.get_credits_used_lifetime()
        remaining = total_credits - credits_used
        return max(0.0, remaining)  # Ensure non-negative
    
    def get_net_cost(self) -> float:
        """
        Get net cost after credits for the period.
        
        Returns:
            Net cost as float
        """
        usage_cost = self.get_usage_cost()
        credits = self.get_credits()
        return usage_cost + credits  # credits are negative, so this subtracts them
    
    def generate_billing_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive billing report.
        
        Returns:
            Dictionary containing all billing data
        """
        logger.info(f"Generating billing report for period: {self.start_date.date()} to {self.end_date.date()}")
        
        # Get all cost and credit data
        usage_cost = self.get_usage_cost()
        credits_applied = self.get_credits()  # negative value
        net_cost = self.get_net_cost()
        
        # Get lifetime credit data
        total_credits_available = config.billing.total_credits
        credits_used_lifetime = self.get_credits_used_lifetime()
        remaining_credits = self.get_remaining_credits()
        
        report = {
            'period': {
                'start_date': self.start_date.strftime('%Y-%m-%d'),
                'end_date': self.end_date.strftime('%Y-%m-%d'),
                'period_type': config.billing.period_type,
                'period_count': config.billing.period_count
            },
            'costs': {
                'usage_cost_period': usage_cost,  # Actual usage for this period
                'credits_applied_period': abs(credits_applied),  # Credits used this period (positive)
                'net_cost_period': net_cost,  # Net cost after credits for period
                'total_cost': usage_cost  # Legacy field for backward compatibility
            },
            'credits': {
                'total_available': total_credits_available,
                'used_lifetime': credits_used_lifetime,
                'remaining': remaining_credits,
                'applied_this_period': abs(credits_applied),
                'expiration_date': config.billing.credit_expiration
            },
            # Legacy fields for backward compatibility
            'total_cost': usage_cost,
            'credits': credits_applied,  # negative value
            'net_cost': net_cost,
            'currency': config.billing.currency,
            'costs_by_service': self.get_cost_by_service(),
            'costs_by_usage_type': self.get_cost_by_usage_type(),
            'daily_costs': self.get_daily_costs(),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
