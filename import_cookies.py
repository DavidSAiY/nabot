"""Import cookies exported from a browser extension into Playwright session format.

Usage:
  1. Install "Cookie-Editor" or "EditThisCookie" browser extension
  2. Go to x.com while logged in to your account
  3. Export cookies (copies JSON to clipboard)
  4. Save to browser_cookies.json in this directory
  5. Run: python3 import_cookies.py
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
BROWSER_COOKIES = BASE_DIR / "browser_cookies.json"
SESSION_FILE = BASE_DIR / "x_session.json"


def convert_cookies(raw_cookies):
    """Convert browser extension cookie format to Playwright format."""
    pw_cookies = []
    for c in raw_cookies:
        cookie = {
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False),
        }
        # Handle sameSite
        same_site = c.get("sameSite", "Lax")
        if same_site in ("no_restriction", "unspecified", "None"):
            same_site = "None"
        elif same_site not in ("Strict", "Lax", "None"):
            same_site = "Lax"
        cookie["sameSite"] = same_site

        # Handle expiry
        if "expirationDate" in c and c["expirationDate"]:
            cookie["expires"] = c["expirationDate"]
        elif "expiry" in c and c["expiry"]:
            cookie["expires"] = c["expiry"]
        else:
            cookie["expires"] = -1

        pw_cookies.append(cookie)
    return pw_cookies


def main():
    if not BROWSER_COOKIES.exists():
        print(f"No cookie file found at {BROWSER_COOKIES}")
        print("Export cookies from your browser and save them there.")
        return

    with open(BROWSER_COOKIES) as f:
        raw_cookies = json.load(f)

    print(f"Loaded {len(raw_cookies)} cookies from browser export.")

    pw_cookies = convert_cookies(raw_cookies)

    # Check for critical cookies
    cookie_names = [c["name"] for c in pw_cookies]
    has_auth = "auth_token" in cookie_names
    has_ct0 = "ct0" in cookie_names

    print(f"auth_token: {'YES' if has_auth else 'MISSING'}")
    print(f"ct0: {'YES' if has_ct0 else 'MISSING'}")

    if not has_auth:
        print("\nWARNING: No auth_token cookie found!")
        print("Make sure you're logged in to x.com before exporting.")
        print(f"Cookies found: {cookie_names}")
        return

    # Save as Playwright session
    session = {
        "cookies": pw_cookies,
        "origins": []
    }

    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)

    print(f"\nSession saved to {SESSION_FILE}")
    print("Run 'python3 verify_session.py' to test it.")


if __name__ == "__main__":
    main()
