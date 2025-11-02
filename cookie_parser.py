"""
Cookie Parser for Twitter/X Bot

Converts cookie text from browser DevTools to JSON format that Playwright can use.
"""

import json
import re
from datetime import datetime

def parse_cookies_from_text(text):
    """
    Parse cookies from copied browser DevTools format
    
    Expected format (tab-separated):
    Name    Value    Domain    Path    Expires    Size    HttpOnly    Secure    SameSite    Priority
    """
    lines = text.strip().split('\n')
    
    # Skip header if present
    if 'Name' in lines[0] or '__cf_bm' in lines[0]:
        # First line might be header or first cookie
        if len(lines[0].split('\t')) > 10:
            start_idx = 1  # Skip header
        else:
            start_idx = 0  # No header, first line is cookie
    else:
        start_idx = 0
    
    cookies = []
    
    for line in lines[start_idx:]:
        if not line.strip():
            continue
            
        parts = line.split('\t')
        if len(parts) < 5:
            continue
        
        try:
            name = parts[0].strip()
            value = parts[1].strip()
            domain = parts[2].strip()
            path = parts[3].strip()
            expires_raw = parts[4].strip()
            
            # Parse expiry date
            if expires_raw == 'Session':
                expires = None
            else:
                try:
                    expires_dt = datetime.fromisoformat(expires_raw.replace('Z', '+00:00'))
                    expires = int(expires_dt.timestamp())
                except:
                    expires = None
            
            # Create cookie object
            cookie = {
                'name': name,
                'value': value,
                'domain': domain,
                'path': path,
            }
            
            if expires:
                cookie['expires'] = expires
            
            # Parse optional fields
            if len(parts) > 6:
                http_only = parts[6].strip() == '✓' if len(parts) > 6 else False
                secure = parts[7].strip() == '✓' if len(parts) > 7 else False
                same_site = parts[8].strip() if len(parts) > 8 and parts[8].strip() else 'Lax'
                
                cookie['httpOnly'] = http_only
                cookie['secure'] = secure
                if same_site not in ['None', '']:
                    cookie['sameSite'] = same_site
            
            cookies.append(cookie)
            
        except Exception as e:
            print(f"⚠️  Skipping invalid cookie line: {e}")
            continue
    
    return cookies

def save_cookies_to_file(cookies, filename='twitter_cookies.json'):
    """Save cookies to JSON file"""
    with open(filename, 'w') as f:
        json.dump(cookies, f, indent=2)
    print(f"✅ Saved {len(cookies)} cookies to {filename}")

def main():
    print("\n🍪 Twitter/X Cookie Parser\n")
    print("Paste your cookies below (from browser DevTools)")
    print("Press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done\n")
    print("-" * 60)
    
    # Read multiple lines from stdin
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    text = '\n'.join(lines)
    
    if not text.strip():
        print("❌ No cookies provided")
        return
    
    # Parse cookies
    cookies = parse_cookies_from_text(text)
    
    if not cookies:
        print("❌ No valid cookies found")
        return
    
    # Save to file
    save_cookies_to_file(cookies)
    
    print(f"\n✅ Successfully parsed {len(cookies)} cookies!")
    print("\nNow you can run: python3 X_Bot_Cookie_Login.py")

if __name__ == "__main__":
    main()

