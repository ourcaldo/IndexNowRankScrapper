from camoufox.sync_api import Camoufox
import time
import os
import json
from pathlib import Path
import logging

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
    # Extension part removed - no device-specific config needed
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

class KeywordTracker:
    def track_keyword_rank(self, keyword, domain, device="desktop", country="ID", 
                          max_pages=100, headless=True, max_retries=3):
        start_time = time.time()
        device_config = get_device_config(device)
        proxy_config = get_proxy_config(country)
        retry_count = 0
        output = {
            'keyword': keyword,
            'domain': domain,
            'device': device,
            'country': country,
            'rank': None,
            'url': None,
            'error': None,
            'attempts': 0
        }

        while retry_count < max_retries:
            output['attempts'] += 1
            try:
                with Camoufox(
                    proxy=proxy_config,
                    geoip=True,
                    headless=headless,
                    timeout=30000,
                    **device_config
                ) as browser:
                    page = browser.new_page()
                    
                    try:
                        # 1. Navigate to Google
                        logger.info("Opening Google...")
                        page.goto("https://www.google.com", timeout=15000)
                        
                        if check_captcha(page):
                            retry_count += 1
                            continue
                        
                        # 2. Verify mobile extension (comment kept but no extension used)
                        if device == 'mobile':
                            user_agent = page.evaluate("navigator.userAgent")
                            logger.info(f"Current User Agent: {user_agent}")
                        
                        # 3. Handle cookie dialog
                        try:
                            page.click("//button[contains(., 'Accept')]", timeout=5000)
                            logger.info("Accepted cookies")
                            time.sleep(1)
                            if check_captcha(page):
                                retry_count += 1
                                continue
                        except:
                            logger.debug("No cookie dialog found")
                        
                        # 4. Perform search
                        logger.info(f"Searching for '{keyword}'...")
                        search_box = page.wait_for_selector("//textarea[@name='q']", timeout=10000)
                        search_box.type(keyword)
                        search_box.press("Enter")
                        time.sleep(2)
                        
                        if check_captcha(page):
                            retry_count += 1
                            continue
                        
                        # 5. Search through results
                        current_page = 1
                        found_rank = None
                        found_url = None
                        
                        while current_page <= max_pages:
                            logger.info(f"Checking page {current_page}...")
                            
                            if check_captcha(page):
                                retry_count += 1
                                break
                            
                            page.wait_for_selector("//*[@id='search']", timeout=10000)
                            if check_captcha(page):
                                retry_count += 1
                                break
                                
                            results = page.query_selector_all("//*[@id='search']//a[contains(@href, 'http')]")
                            
                            for idx, result in enumerate(results, 1):
                                href = result.get_attribute("href")
                                if href and domain in href:
                                    found_rank = (current_page - 1) * 10 + idx
                                    found_url = href.split('&')[0]
                                    output['rank'] = found_rank
                                    output['url'] = found_url
                                    break
                            
                            if found_rank:
                                break
                            
                            # 6. Pagination
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
                                logger.info("Clicking next page...")
                                next_btn.click()
                                time.sleep(3)
                                if check_captcha(page):
                                    retry_count += 1
                                    break
                                current_page += 1
                            else:
                                logger.info("No more pages available")
                                break
                        
                        if found_rank or retry_count >= max_retries:
                            break
                        
                    except Exception as e:
                        output['error'] = str(e)
                        logger.error(f"ERROR: {str(e)}")
                        if "timeout" in str(e).lower():
                            retry_count += 1
                        else:
                            break
                    finally:
                        page.close()
            
            except Exception as e:
                output['error'] = str(e)
                logger.error(f"BROWSER ERROR: {str(e)}")
                retry_count += 1
                continue
        
        # Calculate execution time  
        output['execution_time'] = round(time.time() - start_time, 2)
        
        return output
