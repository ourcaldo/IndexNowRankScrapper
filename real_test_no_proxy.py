#!/usr/bin/env python3
"""
Real test of keyword tracking without proxy - standalone script
"""
import os
import sys
import time
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the tracker functions directly
from camoufox.sync_api import Camoufox
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_proxy_config(country_code):
    base_username = "967c95c4fce6f2f55d5a__cr"
    return {
        "server": "http://gw.dataimpulse.com:823",
        "username": f"{base_username}.{country_code.lower()}",
        "password": "16e23110a32ae728"
    }

def get_device_config(device_type):
    config = {}
    # No extension - simplified config
    return config

def check_captcha(page):
    if "sorry" in page.url.lower() or "captcha" in page.url.lower() or "denied" in page.url.lower():
        logger.warning("CAPTCHA DETECTED - RESTARTING...")
        return True
    try:
        if page.query_selector("div#recaptcha") or page.query_selector("iframe[src*='recaptcha']"):
            logger.warning("CAPTCHA DETECTED - RESTARTING...")
            return True
    except:
        pass
    return False

def test_keyword_tracking_no_proxy():
    """Test keyword tracking without proxy"""
    
    print("=" * 60)
    print("REAL TEST: Keyword tracking WITHOUT proxy")
    print("=" * 60)
    
    keyword = "python"
    domain = "python.org"
    device = "desktop"
    country = "ID"
    max_pages = 2
    headless = True
    max_retries = 1
    use_proxy = False
    
    print(f"Keyword: {keyword}")
    print(f"Domain: {domain}")
    print(f"Device: {device}")
    print(f"Use Proxy: {use_proxy}")
    print(f"Max Pages: {max_pages}")
    print("-" * 60)
    
    start_time = time.time()
    device_config = get_device_config(device)
    proxy_config = get_proxy_config(country) if use_proxy else None
    retry_count = 0
    
    output = {
        'keyword': keyword,
        'domain': domain,
        'device': device,
        'country': country,
        'rank': None,
        'url': None,
        'error': None,
        'attempts': 0,
        'use_proxy': use_proxy
    }

    while retry_count < max_retries:
        output['attempts'] += 1
        print(f"\nAttempt {output['attempts']}...")
        
        try:
            camoufox_args = {
                "geoip": True,
                "headless": headless,
                "timeout": 30000,
                **device_config
            }
            if proxy_config:
                camoufox_args["proxy"] = proxy_config
                print("Using proxy configuration")
            else:
                print("NOT using proxy - direct connection")
            
            with Camoufox(**camoufox_args) as browser:
                page = browser.new_page()
                
                try:
                    # Navigate to Google
                    print("Opening Google...")
                    page.goto("https://www.google.com", timeout=15000)
                    
                    if check_captcha(page):
                        retry_count += 1
                        continue
                    
                    # Handle cookie dialog
                    try:
                        page.click("//button[contains(., 'Accept')]", timeout=5000)
                        print("Accepted cookies")
                        time.sleep(1)
                        if check_captcha(page):
                            retry_count += 1
                            continue
                    except:
                        print("No cookie dialog found")
                    
                    # Perform search
                    print(f"Searching for '{keyword}'...")
                    search_box = page.wait_for_selector("//textarea[@name='q']", timeout=10000)
                    search_box.type(keyword)
                    search_box.press("Enter")
                    time.sleep(2)
                    
                    if check_captcha(page):
                        retry_count += 1
                        continue
                    
                    # Search through results
                    current_page = 1
                    found_rank = None
                    found_url = None
                    
                    while current_page <= max_pages:
                        print(f"Checking page {current_page}...")
                        
                        if check_captcha(page):
                            retry_count += 1
                            break
                        
                        page.wait_for_selector("//*[@id='search']", timeout=10000)
                        if check_captcha(page):
                            retry_count += 1
                            break
                            
                        results = page.query_selector_all("//*[@id='search']//a[contains(@href, 'http')]")
                        print(f"Found {len(results)} search results")
                        
                        for idx, result in enumerate(results, 1):
                            href = result.get_attribute("href")
                            if href and domain in href:
                                found_rank = (current_page - 1) * 10 + idx
                                found_url = href.split('&')[0]
                                output['rank'] = found_rank
                                output['url'] = found_url
                                print(f"FOUND! Rank: {found_rank}, URL: {found_url}")
                                break
                        
                        if found_rank:
                            break
                        
                        # Try next page
                        if current_page < max_pages:
                            next_button_xpaths = [
                                "//*[@id='pnnext']/span[2]",
                                "//a[contains(@aria-label, 'Next')]",
                                "//a[contains(@href, 'start=')]"
                            ]
                            
                            next_btn = None
                            for xpath in next_button_xpaths:
                                try:
                                    next_btn = page.query_selector(xpath)
                                    if next_btn:
                                        break
                                except:
                                    continue
                            
                            if next_btn:
                                print("Clicking next page...")
                                next_btn.click()
                                time.sleep(3)
                                if check_captcha(page):
                                    retry_count += 1
                                    break
                                current_page += 1
                            else:
                                print("No more pages available")
                                break
                        else:
                            break
                    
                    if found_rank or retry_count >= max_retries:
                        break
                    
                except Exception as e:
                    output['error'] = str(e)
                    print(f"ERROR: {str(e)}")
                    if "timeout" in str(e).lower():
                        retry_count += 1
                    else:
                        break
                finally:
                    page.close()
        
        except Exception as e:
            output['error'] = str(e)
            print(f"BROWSER ERROR: {str(e)}")
            retry_count += 1
            continue
    
    # Calculate execution time
    output['execution_time'] = round(time.time() - start_time, 2)
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    print(json.dumps(output, indent=2))
    
    return output

if __name__ == "__main__":
    test_keyword_tracking_no_proxy()