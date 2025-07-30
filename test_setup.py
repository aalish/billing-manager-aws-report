#!/usr/bin/env python3
"""
Test script to verify the project setup and dependencies.
"""
import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import boto3
        print("✓ boto3 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import boto3: {e}")
        return False
    
    try:
        import requests
        print("✓ requests imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import requests: {e}")
        return False
    
    try:
        import pydantic
        print("✓ pydantic imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pydantic: {e}")
        return False
    
    try:
        from config import config
        print("✓ config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from aws_billing import AWSBillingAnalyzer
        print("✓ aws_billing module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import aws_billing: {e}")
        return False
    
    try:
        from integrations.slack_integration import SlackIntegration
        print("✓ slack_integration module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import slack_integration: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config import config
        
        # Test billing period calculation
        start_date, end_date = config.get_billing_period()
        print(f"✓ Billing period calculated: {start_date.date()} to {end_date.date()}")
        
        # Test configuration values
        print(f"✓ Period type: {config.billing.period_type}")
        print(f"✓ Period count: {config.billing.period_count}")
        print(f"✓ AWS region: {config.billing.aws_region}")
        print(f"✓ Currency: {config.billing.currency}")
        print(f"✓ Slack enabled: {config.integrations.slack_enabled}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_environment():
    """Test environment variables."""
    print("\nTesting environment variables...")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    optional_vars = ['AWS_REGION', 'SLACK_WEBHOOK_URL']
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * len(value)} (configured)")
        else:
            print(f"✗ {var}: Not configured (required)")
            all_good = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * len(value)} (configured)")
        else:
            print(f"⚠ {var}: Not configured (optional)")
    
    return all_good

def main():
    """Run all tests."""
    print("Python AWS Billing Monitor - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Environment Test", test_environment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Configure your .env file with AWS credentials")
        print("2. Set up Slack webhook (optional)")
        print("3. Run: python billing_manager.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file from env.example")
        print("3. Configure AWS credentials in .env")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 