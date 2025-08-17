#!/usr/bin/env python3
"""
Debug script to investigate AWS billing details.
"""
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def debug_billing_details():
    """Debug AWS billing to understand why charges are zero."""
    
    # Initialize Cost Explorer client
    ce_client = boto3.client('ce', region_name='us-east-1')
    
    # Get current date and calculate last month
    end_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_date = (end_date - timedelta(days=1)).replace(day=1)
    
    print(f"Debugging billing for period: {start_date.date()} to {end_date.date()}")
    print("=" * 60)
    
    # 1. Check total cost with different metrics
    print("1. Checking different cost metrics:")
    print("-" * 40)
    
    metrics_to_check = ['UnblendedCost', 'BlendedCost', 'AmortizedCost']
    
    for metric in metrics_to_check:
        try:
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=[metric]
            )
            
            amount = float(response['ResultsByTime'][0]['Total'][metric]['Amount'])
            unit = response['ResultsByTime'][0]['Total'][metric]['Unit']
            print(f"  {metric}: {amount} {unit}")
            
        except Exception as e:
            print(f"  {metric}: Error - {e}")
    
    print()
    
    # 2. Check costs by service
    print("2. Checking costs by service:")
    print("-" * 40)
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )
        
        services_found = False
        for result in response['ResultsByTime']:
            for group in result.get('Groups', []):
                service_name = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                if cost > 0:
                    services_found = True
                    print(f"  {service_name}: {cost}")
        
        if not services_found:
            print("  No services with charges found")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    
    # 3. Check record types (credits, charges, etc.)
    print("3. Checking record types:")
    print("-" * 40)
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}
            ]
        )
        
        for result in response['ResultsByTime']:
            for group in result.get('Groups', []):
                record_type = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                print(f"  {record_type}: {cost}")
                
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    
    # 4. Check if there's any usage in the current month
    print("4. Checking current month usage:")
    print("-" * 40)
    
    current_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_end = datetime.now()
    
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': current_start.strftime('%Y-%m-%d'),
                'End': current_end.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        
        amount = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
        print(f"  Current month charges: {amount}")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    
    # 5. Check account information
    print("5. Account information:")
    print("-" * 40)
    
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"  Account ID: {identity['Account']}")
        print(f"  User ARN: {identity['Arn']}")
        
        # Check if this is a new account
        account_creation = datetime.strptime(identity['Arn'].split('/')[-1], '%Y-%m-%d') if '/' in identity['Arn'] else None
        if account_creation:
            print(f"  Account created: {account_creation.date()}")
            
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    debug_billing_details() 