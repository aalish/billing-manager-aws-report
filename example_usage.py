#!/usr/bin/env python3
"""
Example usage of the Python AWS Billing Monitor.
"""
from datetime import datetime
from config import config
from aws_billing import AWSBillingAnalyzer
from billing_manager import BillingManager

def example_basic_usage():
    """Example of basic usage with the billing manager."""
    print("=== Basic Usage Example ===")
    
    # Initialize the billing manager
    billing_manager = BillingManager()
    
    # Run billing analysis (console output only, no notifications)
    report = billing_manager.run_billing_analysis(send_notifications=False)
    
    if report:
        print(f"\nTotal cost for the period: {report['currency']} {report['total_cost']:.2f}")
    else:
        print("Failed to generate billing report")

def example_custom_period():
    """Example of using custom billing periods."""
    print("\n=== Custom Period Example ===")
    
    # Temporarily change the configuration for last 30 days
    original_period_type = config.billing.period_type
    original_period_count = config.billing.period_count
    
    config.billing.period_type = 'd'
    config.billing.period_count = 30
    
    try:
        analyzer = AWSBillingAnalyzer()
        report = analyzer.generate_billing_report()
        
        print(f"30-day billing report:")
        print(f"Period: {report['period']['start_date']} to {report['period']['end_date']}")
        print(f"Total cost: {report['currency']} {report['total_cost']:.2f}")
        
        # Show top 5 services
        costs_by_service = report['costs_by_service']
        sorted_services = sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True)
        
        print("\nTop 5 services by cost:")
        for i, (service, cost) in enumerate(sorted_services[:5], 1):
            print(f"{i}. {service}: {report['currency']} {cost:.2f}")
    
    finally:
        # Restore original configuration
        config.billing.period_type = original_period_type
        config.billing.period_count = original_period_count

def example_service_analysis():
    """Example of detailed service analysis."""
    print("\n=== Service Analysis Example ===")
    
    analyzer = AWSBillingAnalyzer()
    
    # Get costs by service
    service_costs = analyzer.get_cost_by_service()
    
    if service_costs:
        print("Service cost breakdown:")
        total_cost = sum(service_costs.values())
        
        for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True):
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            print(f"  {service}: {config.billing.currency} {cost:.2f} ({percentage:.1f}%)")
    else:
        print("No service costs found")

def example_usage_type_analysis():
    """Example of usage type analysis."""
    print("\n=== Usage Type Analysis Example ===")
    
    analyzer = AWSBillingAnalyzer()
    
    # Get costs by usage type
    usage_costs = analyzer.get_cost_by_usage_type()
    
    if usage_costs:
        print("Usage type cost breakdown:")
        total_cost = sum(usage_costs.values())
        
        # Show top 10 usage types
        for usage_type, cost in sorted(usage_costs.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            print(f"  {usage_type}: {config.billing.currency} {cost:.2f} ({percentage:.1f}%)")
    else:
        print("No usage type costs found")

def example_daily_trend():
    """Example of daily cost trend analysis."""
    print("\n=== Daily Cost Trend Example ===")
    
    analyzer = AWSBillingAnalyzer()
    
    # Get daily costs
    daily_costs = analyzer.get_daily_costs()
    
    if daily_costs:
        print("Daily cost trend:")
        total_period_cost = sum(day['cost'] for day in daily_costs)
        avg_daily_cost = total_period_cost / len(daily_costs)
        
        print(f"Period total: {config.billing.currency} {total_period_cost:.2f}")
        print(f"Average daily cost: {config.billing.currency} {avg_daily_cost:.2f}")
        print(f"Number of days: {len(daily_costs)}")
        
        print("\nDaily breakdown:")
        for day in daily_costs:
            date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%m/%d/%Y')
            print(f"  {date}: {config.billing.currency} {day['cost']:.2f}")
    else:
        print("No daily cost data found")

def example_configuration():
    """Example of configuration management."""
    print("\n=== Configuration Example ===")
    
    print("Current configuration:")
    print(f"  Period type: {config.billing.period_type}")
    print(f"  Period count: {config.billing.period_count}")
    print(f"  AWS region: {config.billing.aws_region}")
    print(f"  Currency: {config.billing.currency}")
    print(f"  Min cost threshold: {config.billing.min_cost_threshold}")
    print(f"  Slack enabled: {config.integrations.slack_enabled}")
    
    # Calculate billing period
    start_date, end_date = config.get_billing_period()
    print(f"  Billing period: {start_date.date()} to {end_date.date()}")

def main():
    """Run all examples."""
    print("Python AWS Billing Monitor - Usage Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_configuration()
        example_basic_usage()
        example_custom_period()
        example_service_analysis()
        example_usage_type_analysis()
        example_daily_trend()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("\nTo run the full billing analysis:")
        print("  python billing_manager.py")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Configured AWS credentials in .env file")
        print("3. Valid AWS permissions for Cost Explorer")

if __name__ == "__main__":
    main() 