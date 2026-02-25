import os
import time
import requests
from playwright.sync_api import sync_playwright

class ProBrowserSaver:
    def __init__(self, save_path, delay=2.0, callback=None):
        self.save_path = save_path
        self.delay = delay
        self.callback = callback
        self.is_running = True
        self.profile_dir = os.path.join(os.getcwd(), "fb_automation_profile")
        
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)

    def stop(self):
        self.is_running = False

    def _safe_query(self, page, selector):
        """Safely query selector, handling context destruction errors."""
        try:
            # We skip wait_for_load_state here because FB network traffic is infinite
            # The polling loop in run() handles the retry logic.
            return page.query_selector(selector)
        except Exception:
            return None

    def log(self, message):
        if self.callback:
            self.callback(0, 0, message)

    def run(self, post_url=None):
        try:
            with sync_playwright() as p:
                self.log("Launching browser...")
                # Use a persistent context so the user only has to log in once
                context = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_dir,
                    headless=False,
                    args=["--start-maximized", "--no-sandbox"]
                )
                
                page = context.new_page()
                
                if post_url:
                    self.log(f"Navigating to post...")
                    try:
                        # Use 'load' instead of 'networkidle' as FB has constant background traffic
                        page.goto(post_url, wait_until="load", timeout=30000)
                    except Exception as e:
                        self.log("Navigation timeout (this is normal for FB). Proceeding...")
                
                self.log("WINDOW IS READY.")
                self.log("1. Log in if needed.")
                self.log("2. Open the image gallery (Theater Mode).")
                self.log("Waiting for Theater Mode detection...")
                
                # Main Loop
                poll_count = 0
                while self.is_running:
                    if page.is_closed():
                        self.log("Browser window closed by user.")
                        break

                    poll_count += 1
                    if poll_count % 5 == 0:
                        self.log("Scanning for theater mode elements...")
                        # Diagnostics: How many images/buttons can we see?
                        imgs = page.query_selector_all('img')
                        btns = page.query_selector_all('div[role="button"]')
                        self.log(f"Diagnostics: Visible Imgs: {len(imgs)}, Buttons: {len(btns)}")

                    # Detect Theater Mode via indicators (Image OR Buttons)
                    indicators = [
                        'img[data-visual-completion="media-vc-image"]',
                        'div[role="dialog"] img[contenteditable="false"]',
                        'img.spotlight',
                        'div[aria-label="Next photo"]',
                        'div[aria-label="Next"]',
                        'div[aria-label="Close"]',
                        'div[data-theater-id]'
                    ]
                    
                    found_indicator = None
                    # URL Check (Newest, very stable indicator)
                    current_url = page.url.lower()
                    if "/photo" in current_url or "fbid=" in current_url or "set=" in current_url:
                        self.log("URL indicates theater mode/photo view.")
                        # Proceed if URL looks right
                        found_indicator = True 
                    else:
                        for selector in indicators:
                            found_indicator = self._safe_query(page, selector)
                            if found_indicator and found_indicator.is_visible():
                                self.log(f"System Check: Theater component found ({selector})")
                                break
                    
                    if found_indicator:
                        self.log("Theater Mode confirmed! Starting auto-save...")
                        try:
                            self._process_gallery(page)
                        except Exception as e:
                            if "context was destroyed" in str(e).lower():
                                self.log("Navigation detected, waiting for page to settle...")
                                time.sleep(2)
                                continue 
                            else:
                                raise e
                        break
                    
                    time.sleep(0.5) 
                
                if self.is_running:
                    self.log("Process finished/idle. Closing in 5 seconds...")
                    time.sleep(5)
                context.close()
        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")
            self.log("The browser may have closed due to an internal error.")

    def _process_gallery(self, page):
        self.log("Starting fast capture with loop protection...")
        saved_count = 0
        last_image_src = ""
        session_urls = set() # Track all URLs in this run to prevent circular loops
        
        while self.is_running:
            if page.is_closed(): break
            
            # Find current image using extremely broad safe query
            img_selectors = [
                'img[data-visual-completion="media-vc-image"]', # Modern FB media selector
                'img.spotlight', # Legacy spotlight
                'div[role="dialog"] img[contenteditable="false"]',
                'div[aria-label="Carousel"] img', # Newer multi-post layout
                'div[role="dialog"] img',
                'img[src*="scontent"]', # Common FB CDN
                'img[role="presentation"]', # Common FB theater image role
                'img[alt^="No photo description"]'
            ]
            
            img_element = None
            # Quick check for images
            for selector in img_selectors:
                img_element = self._safe_query(page, selector)
                if img_element and img_element.is_visible():
                    # Sanity check: Size based filter
                    try:
                        box = img_element.bounding_box()
                        if box and box['width'] > 150:
                            break
                    except:
                        continue
                img_element = None
            
            if img_element:
                try:
                    src = img_element.get_attribute('src')
                except Exception:
                    time.sleep(1)
                    continue
                
                # LOOP PROTECTION:
                # Clean URL (strip query params which are often dynamic)
                clean_src = src.split('?')[0] if '?' in src else src
                
                # Get unique ID from Page URL if possible (fbid is very stable)
                current_page_url = page.url
                fbid = None
                if "fbid=" in current_page_url:
                    parts = current_page_url.split("fbid=")
                    if len(parts) > 1:
                        fbid = parts[1].split("&")[0]

                # 1. Simple sequential repeat check
                if clean_src == last_image_src:
                    self.log("Identified exact sequential repeat. Gallery end reached.")
                    break
                
                # 2. History-based circular check (Crucial for FB)
                # We check both the clean source AND the fbid
                if clean_src in session_urls or (fbid and fbid in session_urls):
                    self.log("Detected circular loop (encountered previously saved image). Finishing.")
                    break
                
                # Download
                file_name = f"pro_{saved_count + 1}.jpg"
                full_path = os.path.join(self.save_path, file_name)
                
                # Unique filename (Duplicate protection)
                counter = 1
                while os.path.exists(full_path):
                    full_path = os.path.join(self.save_path, f"pro_{saved_count + 1}_{counter}.jpg")
                    counter += 1

                try:
                    self.log(f"Saving image {saved_count + 1}...")
                    response = requests.get(src, timeout=15)
                    if response.status_code == 200:
                        with open(full_path, 'wb') as f:
                            f.write(response.content)
                        saved_count += 1
                        self.log(f"Successfully saved: {os.path.basename(full_path)}")
                        last_image_src = clean_src
                        session_urls.add(clean_src)
                        if fbid: session_urls.add(fbid)
                except Exception as e:
                    self.log(f"Download error: {e}")

                # Next button logic
                # FB uses many different selectors, we try the most common ones
                next_selectors = [
                    'div[aria-label="Next photo"]',
                    'div[aria-label="Next"]',
                    'div[aria-label="View next photo"]',
                    'a[aria-label="Next photo"]',
                    'div[role="button"][aria-label*="Next"]',
                    'a.next',
                    '[data-testid="keylogger_next_button"]'
                ]
                
                clicked = False
                for selector in next_selectors:
                    try:
                        btn = self._safe_query(page, selector)
                        if btn and btn.is_visible():
                            btn.click()
                            clicked = True
                            self.log(f"Clicked 'Next' via: {selector}")
                            break
                    except Exception:
                        continue
                
                if not clicked:
                    # Keyboard Fallback: Press Right Arrow
                    try:
                        self.log("No 'Next' button found, trying keyboard fallback (Right Arrow)...")
                        page.keyboard.press("ArrowRight")
                        clicked = True
                    except Exception as e:
                        self.log(f"Keyboard fallback failed: {e}")
                
                if not clicked:
                    self.log("Could not navigate further. Stopping.")
                    break
                    
                time.sleep(self.delay)
            else:
                self.log("Lost track of image element.")
                break

