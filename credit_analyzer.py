#!/usr/bin/env python3
"""
AWS Credit Analyzer - Comprehensive credit tracking and analysis tool.

This script provides detailed analysis of AWS credit usage, remaining balance,
and burn rate projections for the neelcamp profile with $5,000 in credits.
"""

import os
import sys
from datetime import datetime, timedelta
from config import config
from aws_billing import AWSBillingAnalyzer
from billing_manager import BillingManager

def print_header():
    """Print the application header."""
    print("\n" + "=" * 70)
    print("           AWS CREDIT ANALYZER - NEELCAMP PROFILE")
    print("=" * 70)
    print(f"Total Credits: ${config.billing.total_credits:.2f}")
    print(f"Using .env credentials")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def analyze_current_month():
    """Analyze current month's credit usage."""
    print("\n🗓️  CURRENT MONTH ANALYSIS")
    print("-" * 40)
    
    # Set to current month
    config.billing.period_type = 'm'
    config.billing.period_count = 1
    
    analyzer = AWSBillingAnalyzer()
    
    try:
        usage_cost = analyzer.get_usage_cost()
        credits_applied = analyzer.get_credits()
        net_cost = analyzer.get_net_cost()
        
        print(f"Usage Cost:      ${usage_cost:.2f}")
        print(f"Credits Applied: ${abs(credits_applied):.2f}")
        print(f"Net Cost:        ${max(0, net_cost):.2f}")
        
        if usage_cost > 0:
            credit_coverage = min(100, (abs(credits_applied) / usage_cost) * 100)
            print(f"Credit Coverage: {credit_coverage:.1f}%")
    
    except Exception as e:
        print(f"Error analyzing current month: {e}")

def analyze_last_three_months():
    """Analyze last three months trend."""
    print("\n📈 LAST 3 MONTHS TREND")
    print("-" * 40)
    
    # Set to last 3 months
    config.billing.period_type = 'm'
    config.billing.period_count = 3
    
    analyzer = AWSBillingAnalyzer()
    
    try:
        usage_cost = analyzer.get_usage_cost()
        credits_applied = analyzer.get_credits()
        
        print(f"3-Month Usage:   ${usage_cost:.2f}")
        print(f"3-Month Credits: ${abs(credits_applied):.2f}")
        print(f"Monthly Average: ${usage_cost/3:.2f} usage, ${abs(credits_applied)/3:.2f} credits")
        
        # Get service breakdown
        service_costs = analyzer.get_cost_by_service()
        if service_costs:
            print("\nTop Services (3-month total):")
            for i, (service, cost) in enumerate(sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5], 1):
                print(f"  {i}. {service}: ${cost:.2f}")
    
    except Exception as e:
        print(f"Error analyzing 3-month trend: {e}")

def analyze_lifetime_credits():
    """Analyze lifetime credit usage."""
    print("\n💳 LIFETIME CREDIT ANALYSIS")
    print("-" * 40)
    
    analyzer = AWSBillingAnalyzer()
    
    try:
        total_credits = config.billing.total_credits
        credits_used = analyzer.get_credits_used_lifetime()
        remaining_credits = analyzer.get_remaining_credits()
        
        print(f"Total Credits:     ${total_credits:.2f}")
        print(f"Credits Used:      ${credits_used:.2f}")
        print(f"Credits Remaining: ${remaining_credits:.2f}")
        
        if total_credits > 0:
            percent_used = (credits_used / total_credits) * 100
            percent_remaining = 100 - percent_used
            
            print(f"Usage Percentage:  {percent_used:.1f}% used")
            print(f"Remaining:         {percent_remaining:.1f}%")
            
            # Visual progress bar
            bar_length = 50
            filled_length = int(bar_length * percent_used / 100)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"Progress:          [{bar}] {percent_used:.1f}%")
    
    except Exception as e:
        print(f"Error analyzing lifetime credits: {e}")

def project_credit_exhaustion():
    """Project when credits might be exhausted."""
    print("\n⏰ CREDIT EXHAUSTION PROJECTION")
    print("-" * 40)
    
    # Use last month data for projection
    config.billing.period_type = 'm'
    config.billing.period_count = 1
    
    analyzer = AWSBillingAnalyzer()
    
    try:
        monthly_usage = analyzer.get_usage_cost()
        remaining_credits = analyzer.get_remaining_credits()
        
        if monthly_usage > 0 and remaining_credits > 0:
            months_remaining = remaining_credits / monthly_usage
            exhaustion_date = datetime.now() + timedelta(days=months_remaining * 30)
            
            print(f"Monthly Usage Rate: ${monthly_usage:.2f}")
            print(f"Remaining Credits:  ${remaining_credits:.2f}")
            print(f"Months Remaining:   {months_remaining:.1f}")
            print(f"Est. Exhaustion:    {exhaustion_date.strftime('%Y-%m-%d')}")
            
            # Warning levels
            if months_remaining < 1:
                print("🚨 WARNING: Credits will be exhausted within 1 month!")
            elif months_remaining < 3:
                print("⚠️  CAUTION: Credits will be exhausted within 3 months")
            elif months_remaining < 6:
                print("ℹ️  INFO: Credits will be exhausted within 6 months")
            else:
                print("✅ GOOD: Credits should last more than 6 months")
        else:
            print("Unable to calculate projection - insufficient data")
    
    except Exception as e:
        print(f"Error projecting credit exhaustion: {e}")

def show_optimization_suggestions():
    """Show cost optimization suggestions."""
    print("\n💡 OPTIMIZATION SUGGESTIONS")
    print("-" * 40)
    
    analyzer = AWSBillingAnalyzer()
    
    try:
        service_costs = analyzer.get_cost_by_service()
        if service_costs:
            top_service = max(service_costs.items(), key=lambda x: x[1])
            total_cost = sum(service_costs.values())
            
            print(f"Highest Cost Service: {top_service[0]} (${top_service[1]:.2f})")
            print(f"Percentage of Total:  {(top_service[1]/total_cost)*100:.1f}%")
            
            print("\nOptimization Tips:")
            if "Elastic Compute Cloud" in top_service[0]:
                print("• Consider rightsizing EC2 instances")
                print("• Use Spot Instances for non-critical workloads")
                print("• Enable EC2 Instance Savings Plans")
            elif "Relational Database Service" in top_service[0]:
                print("• Review RDS instance sizes and types")
                print("• Consider Aurora Serverless for variable workloads")
                print("• Enable automated backups optimization")
            elif "ElastiCache" in top_service[0]:
                print("• Review cache instance sizes")
                print("• Consider Redis vs Memcached based on use case")
                print("• Monitor cache hit ratios")
            else:
                print("• Review usage patterns for cost optimization")
                print("• Consider AWS Cost Optimization recommendations")
            
            print("• Use AWS Cost Explorer for detailed analysis")
            print("• Set up billing alerts for proactive monitoring")
    
    except Exception as e:
        print(f"Error generating suggestions: {e}")

def main():
    """Main function to run comprehensive credit analysis."""
    print_header()
    
    # Perform comprehensive analysis
    analyze_current_month()
    analyze_last_three_months()
    analyze_lifetime_credits()
    project_credit_exhaustion()
    show_optimization_suggestions()
    
    print("\n" + "=" * 70)
    print("For detailed billing report with full breakdown:")
    print("python billing_manager.py")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError running credit analysis: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in .env file")
        print("2. Check AWS permissions for Cost Explorer")
        print("3. Verify internet connectivity")
        sys.exit(1)