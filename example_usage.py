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

def example_credit_analysis():
    """Example of comprehensive credit analysis."""
    print("\n=== Credit Analysis Example ===")
    
    analyzer = AWSBillingAnalyzer()
    
    try:
        # Get current period credit data
        usage_cost = analyzer.get_usage_cost()
        credits_applied = analyzer.get_credits()
        
        # Get lifetime credit data
        credits_used_lifetime = analyzer.get_credits_used_lifetime()
        remaining_credits = analyzer.get_remaining_credits()
        
        print(f"Current Period Analysis:")
        print(f"  Usage Cost: {config.billing.currency} {usage_cost:.2f}")
        print(f"  Credits Applied: {config.billing.currency} {abs(credits_applied):.2f}")
        print(f"  Net Cost: {config.billing.currency} {max(0, usage_cost + credits_applied):.2f}")
        
        print(f"\nLifetime Credit Analysis:")
        print(f"  Total Credits: {config.billing.currency} {config.billing.total_credits:.2f}")
        print(f"  Credits Used: {config.billing.currency} {credits_used_lifetime:.2f}")
        print(f"  Credits Remaining: {config.billing.currency} {remaining_credits:.2f}")
        
        # Calculate burn rate
        if abs(credits_applied) > 0:
            days_in_period = (analyzer.end_date - analyzer.start_date).days
            daily_burn = abs(credits_applied) / days_in_period if days_in_period > 0 else 0
            monthly_burn = daily_burn * 30
            
            print(f"\nBurn Rate Analysis:")
            print(f"  Daily Burn Rate: {config.billing.currency} {daily_burn:.2f}")
            print(f"  Monthly Burn Rate: {config.billing.currency} {monthly_burn:.2f}")
            
            if monthly_burn > 0:
                months_remaining = remaining_credits / monthly_burn
                print(f"  Estimated Months Remaining: {months_remaining:.1f}")
        
        # Credit status
        percent_used = (credits_used_lifetime / config.billing.total_credits * 100) if config.billing.total_credits > 0 else 0
        print(f"\nCredit Status: {percent_used:.1f}% used")
        
    except Exception as e:
        print(f"Error in credit analysis: {e}")

def example_monthly_credit_trend():
    """Example of monthly credit usage trend."""
    print("\n=== Monthly Credit Trend Example ===")
    
    # Temporarily change to get last 3 months data
    original_period_type = config.billing.period_type
    original_period_count = config.billing.period_count
    
    config.billing.period_type = 'm'
    config.billing.period_count = 3
    
    try:
        analyzer = AWSBillingAnalyzer()
        report = analyzer.generate_billing_report()
        
        print("3-Month Credit Usage Summary:")
        costs = report.get('costs', {})
        credits_info = report.get('credits', {})
        
        # Handle both new and legacy format
        if isinstance(costs, dict):
            usage_cost = costs.get('usage_cost_period', 0)
        else:
            usage_cost = report.get('total_cost', 0)
            
        if isinstance(credits_info, dict):
            credits_applied = credits_info.get('applied_this_period', 0)
            remaining_credits = credits_info.get('remaining', 0)
        else:
            credits_applied = abs(credits_info) if credits_info < 0 else 0
            remaining_credits = 5000  # Default fallback
        
        print(f"  Period Usage Cost: {report['currency']} {usage_cost:.2f}")
        print(f"  Credits Applied: {report['currency']} {credits_applied:.2f}")
        print(f"  Remaining Credits: {report['currency']} {remaining_credits:.2f}")
        
        # Show service breakdown for credit usage
        service_costs = analyzer.get_cost_by_service()
        if service_costs:
            print("\n  Top Services Using Credits:")
            for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {service}: {report['currency']} {cost:.2f}")
    
    finally:
        # Restore original configuration
        config.billing.period_type = original_period_type
        config.billing.period_count = original_period_count

def main():
    """Run all examples."""
    print("Python AWS Billing Monitor - Usage Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_configuration()
        example_basic_usage()
        example_credit_analysis()  # New credit analysis
        example_monthly_credit_trend()  # New monthly trend
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
        print("4. Configured AWS profile 'neelcamp' in ~/.aws/credentials")

if __name__ == "__main__":
    main() 