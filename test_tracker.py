#!/usr/bin/env python3
"""
Simple test script for the keyword tracker without async issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tracker import KeywordTracker

def test_without_proxy():
    print("Testing keyword tracker without proxy...")
    
    tracker = KeywordTracker()
    
    result = tracker.track_keyword_rank(
        keyword="test search",
        domain="example.com",
        device="desktop",
        country="ID",
        max_pages=1,
        headless=True,
        max_retries=1,
        use_proxy=False
    )
    
    print("Result:", result)
    return result

if __name__ == "__main__":
    test_without_proxy()