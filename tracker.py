from camoufox.sync_api import Camoufox
import time
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class KeywordTracker:
    def __init__(self):
        self.logger = logger

    def get_proxy_config(self, country_code):
        """Get proxy configuration for specified country"""
        base_username = "967c95c4fce6f2f55d5a__cr"
        return {
            "server": "http://gw.dataimpulse.com:823",
            "username": f"{base_username}.{country_code.lower()}",
            "password": "16e23110a32ae728"
        }

    def get_device_config(self, device_type):
        """Get device configuration for desktop or mobile"""
        config = {}
        
        if device_type == 'mobile':
            # Set mobile user agent directly in Camoufox config
            mobile_user_agents = [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
            ]
            import random
            selected_ua = random.choice(mobile_user_agents)
            config['user_agent'] = selected_ua
            self.logger.info(f"Using mobile user agent: {selected_ua}")
        
        return config

    def check_captcha(self, page):
        """Check if CAPTCHA is present on the page"""
        if "sorry" in page.url.lower() or "captcha" in page.url.lower() or "denied" in page.url.lower():
            self.logger.warning("CAPTCHA DETECTED - RESTARTING...")
            return True
        try:
            if page.query_selector("div#recaptcha") or page.query_selector("iframe[src*='recaptcha']"):
                self.logger.warning("CAPTCHA DETECTED - RESTARTING...")
                return True
        except:
            pass
        return False

    def track_keyword_rank(self, keyword, domain, device="desktop", country="ID", 
                          max_pages=10, headless=True, max_retries=3):
        """
        Track keyword ranking on Google SERP
        
        Args:
            keyword: Keyword to search for
            domain: Domain to track
            device: Device type (desktop or mobile)
            country: Country code for proxy
            max_pages: Maximum pages to search
            headless: Run browser in headless mode
            max_retries: Maximum retries for captcha detection
            
        Returns:
            Dictionary with tracking results
        """
        start_time = time.time()
        device_config = self.get_device_config(device)
        proxy_config = self.get_proxy_config(country)
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
            'execution_time': None
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
                        self.logger.info("Opening Google...")
                        page.goto("https://www.google.com", timeout=15000)
                        
                        if self.check_captcha(page):
                            retry_count += 1
                            continue
                        
                        # 2. Verify user agent for mobile
                        if device == 'mobile':
                            user_agent = page.evaluate("navigator.userAgent")
                            self.logger.info(f"Current User Agent: {user_agent}")
                        
                        # 3. Handle cookie dialog
                        try:
                            page.click("//button[contains(., 'Accept')]", timeout=5000)
                            self.logger.info("Accepted cookies")
                            time.sleep(1)
                            if self.check_captcha(page):
                                retry_count += 1
                                continue
                        except:
                            self.logger.debug("No cookie dialog found")
                        
                        # 4. Perform search
                        self.logger.info(f"Searching for '{keyword}'...")
                        search_box = page.wait_for_selector("//textarea[@name='q']", timeout=10000)
                        search_box.type(keyword)
                        search_box.press("Enter")
                        time.sleep(2)
                        
                        if self.check_captcha(page):
                            retry_count += 1
                            continue
                        
                        # 5. Search through results
                        current_page = 1
                        found_rank = None
                        found_url = None
                        
                        while current_page <= max_pages:
                            self.logger.info(f"Checking page {current_page}...")
                            
                            if self.check_captcha(page):
                                retry_count += 1
                                break
                            
                            page.wait_for_selector("//*[@id='search']", timeout=10000)
                            if self.check_captcha(page):
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
                                self.logger.info("Clicking next page...")
                                next_btn.click()
                                time.sleep(3)
                                if self.check_captcha(page):
                                    retry_count += 1
                                    break
                                current_page += 1
                            else:
                                self.logger.info("No more pages available")
                                break
                        
                        if found_rank or retry_count >= max_retries:
                            break
                        
                    except Exception as e:
                        output['error'] = str(e)
                        self.logger.error(f"ERROR: {str(e)}")
                        if "timeout" in str(e).lower():
                            retry_count += 1
                        else:
                            break
                    finally:
                        page.close()
            
            except Exception as e:
                output['error'] = str(e)
                self.logger.error(f"BROWSER ERROR: {str(e)}")
                retry_count += 1
                continue
        
        # Calculate execution time
        output['execution_time'] = round(time.time() - start_time, 2)
        
        return output
