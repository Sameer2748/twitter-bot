"""
Twitter/X Bot with Multiple Cookie Support - INFINITE LOOP

This bot uses multiple cookie files and posts in an infinite loop.
Put your cookie JSON files in the cookies/ folder.
"""

from playwright.async_api import async_playwright
import os
import asyncio
from random import choice, uniform
from dotenv import load_dotenv
import logging
import json
import glob

# Tweet messages array - YOU CAN UPDATE THIS
# Hashtag #jansuraajonline is automatically added to all tweets
BASE_MESSAGES = [
    "जाति और धर्म बिहार की राजनीति के सच हैं, लेकिन यह भी तय है कि ये अंतिम सच नहीं हैं।",
    "आप सभी को इतनी जोर से ‘जय बिहार’ कहना चाहिए कि कोई आपको और आपके बच्चों को ‘बिहारी’ न कह सके। आपकी आवाज दिल्ली तक पहुंचनी चाहिए।",
    "शराबबंदी हटेगी तो वह पैसा बजट में नहीं जाएगा और न ही नेताओं की सुरक्षा के लिए इस्तेमाल होगा … उसको सिर्फ बिहार में नई शिक्षा व्यवस्था बनाने में होगा।",
    "हमारा विश्वास है कि समाज मानेगा हो मानेगा। बिहार में जो सही सोच वाले लोग हैं, जिनके पास क्षमता और जज़्बा है … वह धीरे-धीरे राजनीति से किनारे हो गए हैं।"
]

# Add this hashtag to every tweet
HASHTAG = "#SANGHARSH_KE_1280_DIN"

# Images folder path
IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'images')
COOKIES_FOLDER = os.path.join(os.path.dirname(__file__), 'cookies')

def get_random_image():
    """Get a random image from the images folder"""
    if not os.path.exists(IMAGES_FOLDER):
        return None
    
    # Get all image files
    images = glob.glob(os.path.join(IMAGES_FOLDER, '*.jpg')) + \
             glob.glob(os.path.join(IMAGES_FOLDER, '*.jpeg')) + \
             glob.glob(os.path.join(IMAGES_FOLDER, '*.png')) + \
             glob.glob(os.path.join(IMAGES_FOLDER, '*.gif'))
    
    if not images:
        return None
    
    return choice(images)

def load_cookie_files():
    """Load all cookie files from cookies folder"""
    cookie_files = []
    
    if not os.path.exists(COOKIES_FOLDER):
        os.makedirs(COOKIES_FOLDER)
        logging.warning(f"Created cookies folder: {COOKIES_FOLDER}")
        logging.warning("Please add your cookie JSON files to the cookies/ folder")
        return cookie_files
    
    # Get all JSON files from cookies folder
    json_files = glob.glob(os.path.join(COOKIES_FOLDER, '*.json'))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                cookies = json.load(f)
                cookie_files.append(cookies)
                logging.info(f"Loaded cookies from: {os.path.basename(json_file)}")
        except Exception as e:
            logging.error(f"Error loading {json_file}: {e}")
    
    return cookie_files

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

PROFILE_PATH = os.getenv('PROFILE_PATH')
CHROME_PATH = os.getenv('CHROME_PATH')

async def post_tweet_async(page, tweet_data, account_id):
    """Post a tweet from an async context"""
    try:
        # Navigate to compose
        try:
            await page.goto("https://x.com/compose/post")
        except:
            await page.goto("https://twitter.com/compose/tweet")
        await page.wait_for_timeout(200)

        # Add text
        if tweet_data['text']:
            try:
                text_input = page.get_by_role("textbox", name="Post text").first
                await text_input.click()
                await page.wait_for_timeout(100)
                
                for char in tweet_data['text']:
                    await text_input.type(char, delay=uniform(2, 5))
                
                await page.wait_for_timeout(100)
                logging.info(f"[Account {account_id}] Text entered: {tweet_data['text'][:50]}...")
            except Exception as e:
                logging.warning(f"[Account {account_id}] Could not add text: {e}")

        # Add media if provided
        if tweet_data.get('image_path') and os.path.exists(tweet_data['image_path']):
            await page.set_input_files("input[data-testid='fileInput']", tweet_data['image_path'])
            await page.wait_for_timeout(1000)
            logging.info(f"[Account {account_id}] Media attached: {os.path.basename(tweet_data['image_path'])}")
        
        # Click on modal border
        try:
            await page.click("div[role='dialog']", position={"x": 0, "y": 0})
            await page.wait_for_timeout(200)
        except:
            pass
        
        # Click Post button
        try:
            await page.wait_for_selector("span:has-text('Post')", timeout=5000)
            await page.click("span:has-text('Post')", timeout=5000)
            logging.info(f"[Account {account_id}] Clicked Post button")
        except Exception as e1:
            logging.warning(f"[Account {account_id}] First Post click failed: {e1}")
            try:
                await page.wait_for_selector("button[data-testid='tweetButton']", timeout=5000)
                await page.click("button[data-testid='tweetButton']", timeout=5000)
                logging.info(f"[Account {account_id}] Clicked alternate Post button")
            except Exception as e2:
                logging.warning(f"[Account {account_id}] Alternate Post click failed: {e2}")
                await page.keyboard.press('Meta+Enter')
                logging.info(f"[Account {account_id}] Used keyboard shortcut")
        
        await page.wait_for_timeout(2000)
        logging.info(f"[Account {account_id}] ✅ Tweet posted successfully!")
        return True
    except Exception as e:
        logging.error(f"[Account {account_id}] Error posting tweet: {e}")
        return False

async def post_with_cookies(cookies, account_id):
    """Post one tweet using a specific cookie set"""
    async with async_playwright() as p:
        try:
            # Launch browser context
            context = await p.chromium.launch_persistent_context(
                executable_path=CHROME_PATH,
                user_data_dir=f"/tmp/twitter_bot_cookie_{account_id}",
                headless=False,
            )
            
            # Navigate and add cookies
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto('https://x.com')
            await context.add_cookies(cookies)
            
            # Prepare tweet data
            msg = choice(BASE_MESSAGES)
            full_tweet = f"{msg} {HASHTAG}"
            random_image = get_random_image()
            
            tweet_data = {
                'text': full_tweet,
                'image_path': random_image
            }
            
            logging.info(f"[Account {account_id}] Posting tweet with image: {os.path.basename(random_image) if random_image else 'text only'}")
            
            # Post the tweet
            success = await post_tweet_async(page, tweet_data, account_id)
            
            await context.close()
            return success
            
        except Exception as e:
            logging.error(f"[Account {account_id}] Error in post_with_cookies: {e}")
            return False

async def infinite_posting_loop():
    """Infinite loop: 5 parallel posts, each with random cookie, NO WAIT"""
    print("🚀 Starting Twitter bot - 5 parallel windows, infinite loop, NO WAIT")
    
    # Load all cookies
    all_cookies = load_cookie_files()
    
    if not all_cookies:
        logging.error("No cookie files found! Please add JSON files to the cookies/ folder")
        return
    
    logging.info(f"Loaded {len(all_cookies)} cookie files")
    
    post_count = 0
    
    while True:
        try:
            # Pick 5 random cookies (can be duplicates)
            selected_cookies = [choice(all_cookies) for _ in range(5)]
            
            logging.info(f"\n{'='*60}")
            logging.info(f"Round - Starting 5 parallel posts")
            logging.info(f"{'='*60}")
            
            # Post with all 5 accounts in parallel
            tasks = []
            for i, cookies in enumerate(selected_cookies):
                account_id = all_cookies.index(cookies)
                task = asyncio.create_task(post_with_cookies(cookies, f"{account_id}-{i}"))
                tasks.append(task)
            
            # Wait for all 5 to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successes
            successful = sum(1 for r in results if r is True)
            post_count += successful
            
            logging.info(f"✅ Total posts completed: {post_count}")
            
            # NO WAIT - immediately start next round
            logging.info("🚀 Starting next round immediately...\n")
            
        except KeyboardInterrupt:
            logging.info("\n🛑 Stopping bot...")
            break
        except Exception as e:
            logging.error(f"Error in infinite loop: {e}")
            logging.info("Waiting 10 seconds before retrying...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(infinite_posting_loop())

