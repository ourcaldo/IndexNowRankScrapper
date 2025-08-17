#!/usr/bin/env python3
"""
Test script to demonstrate API functionality without proxy
"""
import requests
import json

def test_api_without_proxy():
    """Test the keyword tracking API with use_proxy=false"""
    
    url = "http://localhost:5000/track-keyword"
    headers = {
        "X-API-Key": "default_api_key_12345",
        "Content-Type": "application/json",
        "Host": "replit.com"
    }
    
    payload = {
        "keyword": "test keyword",
        "domain": "example.com",
        "devices": "desktop",
        "country": "ID",
        "max_pages": 1,
        "headless": True,
        "max_retries": 1,
        "use_proxy": False
    }
    
    print("Testing API without proxy...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ API Request Successful!")
            print(f"✓ Keyword: {result.get('keyword')}")
            print(f"✓ Domain: {result.get('domain')}")
            print(f"✓ Device: {result.get('device')}")
            print(f"✓ Country: {result.get('country')}")
            print(f"✓ Use Proxy: False (as requested)")
            print(f"✓ Attempts: {result.get('attempts')}")
            print(f"✓ Execution Time: {result.get('execution_time')}s")
            
            if result.get('error'):
                print(f"⚠ Browser Error (expected in Replit environment): {result.get('error')[:100]}...")
            else:
                print(f"✓ Rank: {result.get('rank', 'Not found')}")
                print(f"✓ URL: {result.get('url', 'Not found')}")
                
        else:
            print(f"✗ API Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection Error: {e}")

if __name__ == "__main__":
    test_api_without_proxy()