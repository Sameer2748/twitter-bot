"""
Helper script to login to Twitter/X using Google account via Playwright

This script will:
1. Open a browser window
2. Navigate to Twitter login
3. Click "Sign in with Google"
4. Handle Google authentication
5. Save cookies for reuse
"""

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import json
import os
import time

load_dotenv()

CHROME_PATH = os.getenv('CHROME_PATH')
PROFILE_PATH = os.getenv('PROFILE_PATH')

def login_with_google():
    """
    Login to Twitter/X using Google account and save cookies
    """
    with sync_playwright() as p:
        print("🚀 Starting browser...")
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_PATH,
            executable_path=CHROME_PATH,
            headless=False,  # Keep visible so you can interact
        )
        
        page = browser.new_page()
        
        # Navigate to Twitter login
        print("📍 Opening Twitter login page...")
        page.goto("https://twitter.com/i/flow/login")
        time.sleep(3)
        
        # Look for Google sign-in button
        print("🔍 Looking for Google sign-in button...")
        time.sleep(2)
        
        try:
            # Try to find and click Google sign-in button
            google_button = page.locator('text=Continue with Google').first
            if google_button.is_visible():
                print("✅ Found Google sign-in button, clicking...")
                google_button.click()
                time.sleep(5)
                
                print("\n" + "="*60)
                print("⏸️  MANUAL STEP REQUIRED:")
                print("="*60)
                print("1. Complete Google login in the browser window")
                print("2. Authorize Twitter/X if prompted")
                print("3. Wait until you're logged into Twitter/X")
                print("4. Press ENTER in this terminal when done")
                print("="*60 + "\n")
                
                input("Press ENTER after you've logged in successfully...")
                
            else:
                print("❌ Google button not found. Looking for alternative methods...")
                
                # Alternative: Look for any sign-in options
                sign_in_options = page.locator('text=/Continue with|Sign in with|Log in with/').all()
                if sign_in_options:
                    print(f"Found {len(sign_in_options)} sign-in options")
                    for i, option in enumerate(sign_in_options):
                        print(f"{i+1}. {option.text_content()}")
                else:
                    print("⚠️  Could not find Google sign-in button")
                    print("\n🔍 Try manually clicking 'Continue with Google' in the browser")
                    input("Press ENTER when you've completed login...")
        
        except Exception as e:
            print(f"⚠️  Error: {e}")
            print("\n🔍 You may need to manually click 'Continue with Google'")
            input("Press ENTER when you've completed login...")
        
        # Check if logged in
        current_url = page.url
        if "twitter.com/home" in current_url or "twitter.com/i/flow/login" not in current_url:
            print("✅ Successfully logged in!")
            
            # Get cookies
            cookies = browser.cookies()
            
            # Save cookies to file
            cookies_file = "twitter_cookies.json"
            with open(cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            print(f"💾 Cookies saved to: {cookies_file}")
            print("✅ You can now use these cookies for automated login!")
            print("\nTo use saved cookies in the bot:")
            print(f"1. Copy the cookies from {cookies_file}")
            print("2. We'll modify X_Bot.py to load these cookies instead of manual login")
            
        else:
            print("❌ Login may not have completed. Current URL:", current_url)
        
        # Keep browser open for a bit
        print("\n⏳ Keeping browser open for 5 more seconds...")
        time.sleep(5)
        
        browser.close()
        print("✅ Done!")

if __name__ == "__main__":
    login_with_google()

