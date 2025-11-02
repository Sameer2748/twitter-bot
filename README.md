# Twitter Bot - Multi-Cookie Infinite Loop

Twitter/X posting bot with support for multiple accounts and Mac variants.

## Files

- `bot_m1.py` - Mac M1 version (3 parallel windows)
- `bot_m2.py` - Mac M2 version (5 parallel windows)  
- `bot_m4.py` - Mac M4 version (10 parallel windows)
- `X_Bot_Multi_Cookie.py` - General version (5 parallel windows)
- `login_with_google.py` - Login helper to get cookies
- `cookie_parser.py` - Parse raw cookies to JSON
- `test_cookies.py` - Test if cookies are valid

## Setup

1. **Install dependencies:**
```bash
pip3 install playwright python-dotenv
playwright install chromium
```

2. **Configure .env:**
```bash
cp ENV_TEMPLATE.txt .env
# Edit .env with your Chrome path
```

3. **Add cookies:**
```bash
# Option 1: Login with Google
python3 login_with_google.py

# Option 2: Parse raw cookies
python3 cookie_parser.py < my_cookies.txt

# Copy cookie files to cookies/ folder
mkdir -p cookies
cp twitter_cookies.json cookies/account_1.json
# Repeat for each account
```

## Run Commands

### Mac M1 (3 windows)
```bash
cd twitter-bot
python3 bot_m1.py
```

### Mac M2 (5 windows)
```bash
cd twitter-bot
python3 bot_m2.py
```

### Mac M4 (10 windows)
```bash
cd twitter-bot
python3 bot_m4.py
```

### General Version (5 windows)
```bash
cd twitter-bot
python3 X_Bot_Multi_Cookie.py
```

## Stop Bot

**Method 1:** Press `Ctrl+C` in the terminal running the bot

**Method 2:** From any terminal:
```bash
# Stop specific bot
pkill -f bot_m1
pkill -f bot_m2
pkill -f bot_m4
pkill -f X_Bot_Multi_Cookie

# OR stop ALL bots at once
pkill -f bot_m
pkill -f X_Bot_Multi
```

## How It Works

1. **Loads all cookies** from `cookies/` folder
2. **Random selection** - Picks random cookies for each round
3. **Parallel posting** - Posts N tweets simultaneously (N = windows count)
4. **Infinite loop** - Runs forever, no wait between rounds
5. **Random content** - Random messages + images from arrays

## Customize

Edit the bot files to change:
- `BASE_MESSAGES` - Tweet messages
- `HASHTAG` - Hashtag to add
- `WINDOWS_COUNT` - Number of parallel windows

## Requirements

- Python 3.9+
- Playwright
- Chrome/Chromium
- Multiple X/Twitter accounts (cookies)

## Troubleshooting

**No cookies found:** Add JSON files to `cookies/` folder

**Chrome path error:** Update `CHROME_PATH` in `.env`

**Account not logging in:** Cookie expired, regenerate cookies

**Rate limiting:** Add delays if you hit rate limits

