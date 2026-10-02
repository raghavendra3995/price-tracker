import os, re, json, requests
from bs4 import BeautifulSoup

# (name, product link, target price in rupees)
# TEST: targets are 99999 so you get a message right away.
# After the test, change 99999 to your real target (e.g. 15000).
PRODUCTS = [
    ("Zen 8X Flipkart",
     "https://www.flipkart.com/egate-zen-8x-official-google-tv-certified-apps-netflix-prime-1080p-native-4k-support-17500-lm-1-speaker-wireless-remote-controller-projector/p/itm17d4ca07a0a20?pid=PROHR9ZN4WAZXUWR",
     99999),
    # ("Zen 8X Amazon", "PASTE_AMAZON_LINK_HERE", 99999),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

def notify(text):
    token = os.environ["TELEGRAM_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                  data={"chat_id": chat, "text": text}, timeout=20)

def get_price(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    print("HTTP status:", r.status_code)
    soup = BeautifulSoup(r.text, "html.parser")
    # 1) product data embedded in the page (common on Flipkart)
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        for item in (data if isinstance(data, list) else [data]):
            offers = item.get("offers") if isinstance(item, dict) else None
            if isinstance(offers, list):
                offers = offers[0] if offers else None
            if isinstance(offers, dict) and offers.get("price"):
                try:
                    return int(float(offers["price"]))
                except ValueError:
                    pass
    # 2) Amazon fallback
    tag = soup.select_one("span.a-price-whole")
    if tag:
        digits = re.sub(r"[^\d]", "", tag.get_text())
        return int(digits) if digits else None
    return None

for name, url, target in PRODUCTS:
    try:
        price = get_price(url)
    except Exception as e:
        print(f"{name}: error {e}")
        continue
    if price is None:
        print(f"{name}: could not read price (page may be blocked)")
        continue
    print(f"{name}: Rs {price} (target {target})")
    if price <= target:
        notify(f"Price drop! {name} is Rs {price} (target Rs {target})\n{url}")
