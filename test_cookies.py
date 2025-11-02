"""
Quick test to verify cookies work
"""

from playwright.sync_api import sync_playwright
import json
import time

def test_cookies():
    print("\n🧪 Testing Twitter/X Cookies...\n")
    
    # Load cookies
    try:
        with open('twitter_cookies.json', 'r') as f:
            cookies = json.load(f)
        print(f"✅ Loaded {len(cookies)} cookies from twitter_cookies.json")
    except FileNotFoundError:
        print("❌ twitter_cookies.json not found!")
        return False
    
    # Test with Playwright
    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Add cookies BEFORE navigation
        print("🍪 Adding cookies to browser...")
        context.add_cookies(cookies)
        
        # Try to access Twitter
        print("📍 Opening Twitter/X...")
        page.goto('https://x.com/home')
        
        # Wait a moment
        time.sleep(3)
        
        # Check if logged in
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        if '/home' in current_url or '/home' in page.content():
            print("\n✅ SUCCESS! Cookies are valid and working!")
            print("✅ You are logged in to Twitter/X")
            print("\nPress any key to close browser...")
            input()
            browser.close()
            return True
        else:
            print("\n❌ FAILED! Not logged in or cookies expired")
            print("❌ You need to get fresh cookies from browser")
            print("\nPress any key to close browser...")
            input()
            browser.close()
            return False

if __name__ == "__main__":
    success = test_cookies()
    if success:
        print("\n🎉 Your cookies work! Ready to run the bot.")
        print("Run: python3 X_Bot_Cookie_Login.py")
    else:
        print("\n⚠️  Cookies need to be refreshed.")
        print("Get new cookies from browser and run:")
        print("python3 cookie_parser.py < my_cookies.txt")

