#!/usr/bin/env python3
"""
Security test script to demonstrate anti-spoofing measures
"""
import requests
import json

BASE_URL = "http://localhost:5000"
API_KEY = "default_api_key_12345"

def test_request(description, headers, expected_status=401):
    """Test a request with specific headers"""
    print(f"\n🧪 {description}")
    
    try:
        response = requests.get(f"{BASE_URL}/health", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code != expected_status:
            print(f"⚠️  Expected {expected_status}, got {response.status_code}")
        
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    print("🔒 Security Anti-Spoofing Test Suite")
    print("="*50)
    
    # Test 1: No API key (should fail)
    test_request(
        "Test 1: No API key",
        {"Host": "replit.dev"},
        expected_status=401
    )
    
    # Test 2: Valid request (should succeed)  
    test_request(
        "Test 2: Valid request",
        {"X-API-Key": API_KEY, "Host": "replit.dev"},
        expected_status=200
    )
    
    # Test 3: Spoofed hostname (should fail)
    test_request(
        "Test 3: Spoofed hostname (google.com pretending to be replit.dev)",
        {"X-API-Key": API_KEY, "Host": "google.com"},
        expected_status=403
    )
    
    # Test 4: Inconsistent headers (should warn but might allow)
    test_request(
        "Test 4: Inconsistent headers",
        {
            "X-API-Key": API_KEY, 
            "Host": "replit.dev",
            "Origin": "https://google.com",
            "Referer": "https://facebook.com"
        },
        expected_status=200  # Might succeed but with warnings
    )
    
    # Test 5: Missing User-Agent (should warn)
    test_request(
        "Test 5: Missing User-Agent header",
        {"X-API-Key": API_KEY, "Host": "replit.dev"},
        expected_status=200
    )
    
    # Test 6: Suspicious User-Agent
    test_request(
        "Test 6: Suspicious User-Agent (curl)",
        {
            "X-API-Key": API_KEY, 
            "Host": "replit.dev",
            "User-Agent": "curl/7.68.0"
        },
        expected_status=200  # Allowed but logged
    )

if __name__ == "__main__":
    main()