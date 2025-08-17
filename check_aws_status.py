#!/usr/bin/env python3
"""
Simple script to check AWS account status and understand billing.
"""
import os
import subprocess
import sys

def check_aws_cli():
    """Check if AWS CLI is available and configured."""
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ AWS CLI is configured and working")
            return True
        else:
            print("❌ AWS CLI error:", result.stderr)
            return False
    except FileNotFoundError:
        print("❌ AWS CLI not found. Install it first.")
        return False
    except Exception as e:
        print(f"❌ Error checking AWS CLI: {e}")
        return False

def check_environment_variables():
    """Check if AWS environment variables are set."""
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    optional_vars = ['AWS_REGION', 'AWS_SESSION_TOKEN']
    
    print("\n🔍 Checking AWS Environment Variables:")
    print("-" * 40)
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (configured)")
        else:
            print(f"❌ {var}: Not configured")
            all_good = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (configured)")
        else:
            print(f"⚠️  {var}: Not configured (optional)")
    
    return all_good

def explain_zero_charges():
    """Explain possible reasons for zero charges."""
    print("\n🤔 Why might your charges be $0.00?")
    print("-" * 40)
    
    reasons = [
        "1. 🆓 AWS Free Tier Active - New accounts get 12 months free",
        "2. 🚫 No Active Services - No EC2, S3, Lambda, etc. running",
        "3. 💳 Credits Covering Charges - Your $146.26 credit covers everything",
        "4. ⏰ Timing - Current month charges not yet processed",
        "5. 🧪 Test Account - Minimal or no usage of paid services",
        "6. 🎯 Free Tier Limits - Staying within free service limits"
    ]
    
    for reason in reasons:
        print(f"   {reason}")

def suggest_investigation():
    """Suggest ways to investigate further."""
    print("\n🔍 How to investigate further:")
    print("-" * 40)
    
    suggestions = [
        "1. Check AWS Console Billing Dashboard",
        "2. Look at Cost Explorer in AWS Console",
        "3. Check if you have any running services",
        "4. Review your AWS Free Tier usage",
        "5. Check if you're in a new account period",
        "6. Look at your credit sources in AWS Console"
    ]
    
    for suggestion in suggestions:
        print(f"   {suggestion}")

def main():
    """Main function to check AWS status."""
    print("AWS Account Status Check")
    print("=" * 50)
    
    # Check AWS CLI
    aws_working = check_aws_cli()
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Explain zero charges
    explain_zero_charges()
    
    # Suggest investigation
    suggest_investigation()
    
    print("\n" + "=" * 50)
    if aws_working and env_ok:
        print("✅ Your AWS setup looks good!")
        print("💡 The $0.00 charges are likely due to Free Tier or credits.")
    else:
        print("⚠️  Some AWS configuration issues detected.")
        print("💡 Fix the issues above before running billing analysis.")

if __name__ == "__main__":
    main() 