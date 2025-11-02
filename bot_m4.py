"""
Twitter/X Bot - Mac M4 Version (10 Parallel Windows)

This bot uses multiple cookie files and posts 10 parallel tweets in an infinite loop.
For Mac M4 - optimized for 10 browser windows.
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
BASE_MESSAGES = [
    "जाति और धर्म बिहार की राजनीति के सच हैं, लेकिन यह भी तय है कि ये अंतिम सच नहीं हैं।",
    "आप सभी को इतनी जोर से 'जय बिहार' कहना चाहिए कि कोई आपको और आपके बच्चों को 'बिहारी' न कह सके। आपकी आवाज दिल्ली तक पहुंचनी चाहिए।",
    "शराबबंदी हटेगी तो वह पैसा बजट में नहीं जाएगा और न ही नेताओं की सुरक्षा के लिए इस्तेमाल होगा … उसको सिर्फ बिहार में नई शिक्षा व्यवस्था बनाने में होगा।",
    "हमारा विश्वास है कि समाज मानेगा हो मानेगा। बिहार में जो सही सोच वाले लोग हैं, जिनके पास क्षमता और जज़्बा है … वह धीरे-धीरे राजनीति से किनारे हो गए हैं।"
]

HASHTAG = "#SANGHARSH_KE_1280_DIN"
WINDOWS_COUNT = 10  # M4: 10 windows

IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'images')
COOKIES_FOLDER = os.path.join(os.path.dirname(__file__), 'cookies')

def get_random_image():
    if not os.path.exists(IMAGES_FOLDER):
        return None
    images = glob.glob(os.path.join(IMAGES_FOLDER, '*.jpg')) + \
             glob.glob(os.path.join(IMAGES_FOLDER, '*.jpeg')) + \
             glob.glob(os.path.join(IMAGES_FOLDER, '*.png')) + \
             glob.glob(os.path.join(IMAGES_FOLDER, '*.gif'))
    return choice(images) if images else None

def load_cookie_files():
    cookie_files = []
    if not os.path.exists(COOKIES_FOLDER):
        os.makedirs(COOKIES_FOLDER)
        logging.warning(f"Created cookies folder: {COOKIES_FOLDER}")
        return cookie_files
    json_files = glob.glob(os.path.join(COOKIES_FOLDER, '*.json'))
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                cookies = json.load(f)
                cookie_files.append(cookies)
                logging.info(f"Loaded: {os.path.basename(json_file)}")
        except Exception as e:
            logging.error(f"Error loading {json_file}: {e}")
    return cookie_files

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CHROME_PATH = os.getenv('CHROME_PATH')

async def post_tweet_async(page, tweet_data, account_id):
    try:
        try:
            await page.goto("https://x.com/compose/post")
        except:
            await page.goto("https://twitter.com/compose/tweet")
        await page.wait_for_timeout(200)
        if tweet_data['text']:
            try:
                text_input = page.get_by_role("textbox", name="Post text").first
                await text_input.click()
                await page.wait_for_timeout(100)
                for char in tweet_data['text']:
                    await text_input.type(char, delay=uniform(2, 5))
                await page.wait_for_timeout(100)
            except Exception as e:
                logging.warning(f"[Account {account_id}] Text error: {e}")
        if tweet_data.get('image_path') and os.path.exists(tweet_data['image_path']):
            await page.set_input_files("input[data-testid='fileInput']", tweet_data['image_path'])
            await page.wait_for_timeout(1000)
        try:
            await page.click("div[role='dialog']", position={"x": 0, "y": 0})
            await page.wait_for_timeout(200)
        except:
            pass
        try:
            await page.wait_for_selector("span:has-text('Post')", timeout=5000)
            await page.click("span:has-text('Post')", timeout=5000)
        except Exception as e1:
            try:
                await page.wait_for_selector("button[data-testid='tweetButton']", timeout=5000)
                await page.click("button[data-testid='tweetButton']", timeout=5000)
            except Exception as e2:
                await page.keyboard.press('Meta+Enter')
        await page.wait_for_timeout(2000)
        logging.info(f"[Account {account_id}] ✅ Posted!")
        return True
    except Exception as e:
        logging.error(f"[Account {account_id}] Error: {e}")
        return False

async def post_with_cookies(cookies, account_id):
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                executable_path=CHROME_PATH,
                user_data_dir=f"/tmp/twitter_bot_cookie_{account_id}",
                headless=False,
            )
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto('https://x.com')
            await context.add_cookies(cookies)
            msg = choice(BASE_MESSAGES)
            full_tweet = f"{msg} {HASHTAG}"
            random_image = get_random_image()
            tweet_data = {'text': full_tweet, 'image_path': random_image}
            success = await post_tweet_async(page, tweet_data, account_id)
            await context.close()
            return success
        except Exception as e:
            logging.error(f"[Account {account_id}] Error: {e}")
            return False

async def infinite_posting_loop():
    print(f"🚀 Starting M4 Bot - {WINDOWS_COUNT} parallel windows, infinite loop")
    all_cookies = load_cookie_files()
    if not all_cookies:
        logging.error("No cookie files found!")
        return
    logging.info(f"Loaded {len(all_cookies)} cookie files")
    post_count = 0
    while True:
        try:
            selected_cookies = [choice(all_cookies) for _ in range(WINDOWS_COUNT)]
            logging.info(f"\n{'='*60}\nRound - {WINDOWS_COUNT} parallel posts\n{'='*60}")
            tasks = []
            for i, cookies in enumerate(selected_cookies):
                account_id = all_cookies.index(cookies)
                task = asyncio.create_task(post_with_cookies(cookies, f"{account_id}-{i}"))
                tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(1 for r in results if r is True)
            post_count += successful
            logging.info(f"✅ Total: {post_count}\n🚀 Next round...\n")
        except KeyboardInterrupt:
            logging.info("\n🛑 Stopping...")
            break
        except Exception as e:
            logging.error(f"Error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(infinite_posting_loop())

