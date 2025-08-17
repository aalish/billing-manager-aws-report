"""
AWS Billing module for fetching and analyzing billing data.
"""
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWSBillingAnalyzer:
    """Analyzes AWS billing data using Cost Explorer API."""
    
    def __init__(self):
        """Initialize the AWS billing analyzer."""
        self.ce_client = boto3.client('ce', region_name=config.billing.aws_region)
        self.start_date, self.end_date = config.get_billing_period()
    
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
                Metrics=['AmortizedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}
                ]
            )
            
            total_credits = 0.0
            
            for result in response['ResultsByTime']:
                for group in result.get('Groups', []):
                    record_type = group['Keys'][0]
                    if 'Credit' in record_type:
                        cost = float(group['Metrics']['AmortizedCost']['Amount'])
                        total_credits += cost
            
            return total_credits
            
        except Exception as e:
            logger.error(f"Error fetching credits: {e}")
            return 0.0
    
    def get_net_cost(self) -> float:
        """
        Get net cost after credits for the period.
        
        Returns:
            Net cost as float
        """
        total_cost = self.get_total_cost()
        credits = self.get_credits()
        return total_cost + credits  # credits are negative, so this subtracts them
    
    def generate_billing_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive billing report.
        
        Returns:
            Dictionary containing all billing data
        """
        logger.info(f"Generating billing report for period: {self.start_date.date()} to {self.end_date.date()}")
        
        total_cost = self.get_total_cost()
        credits = self.get_credits()
        net_cost = self.get_net_cost()
        
        report = {
            'period': {
                'start_date': self.start_date.strftime('%Y-%m-%d'),
                'end_date': self.end_date.strftime('%Y-%m-%d'),
                'period_type': config.billing.period_type,
                'period_count': config.billing.period_count
            },
            'total_cost': total_cost,
            'credits': credits,
            'net_cost': net_cost,
            'currency': config.billing.currency,
            'costs_by_service': self.get_cost_by_service(),
            'costs_by_usage_type': self.get_cost_by_usage_type(),
            'daily_costs': self.get_daily_costs(),
            'generated_at': datetime.now().isoformat()
        }
        
        return report 