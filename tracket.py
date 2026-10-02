import os, re, requests
from bs4 import BeautifulSoup

# EDIT THIS LIST: (name, product link, target price in rupees)
PRODUCTS = [
    ("E Gate Zen 8X", "PASTE_AMAZON_LINK_HERE", 15000),
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
    soup = BeautifulSoup(r.text, "html.parser")
    tag = soup.select_one("span.a-price-whole")
    if not tag:
        return None
    digits = re.sub(r"[^\d]", "", tag.get_text())
    return int(digits) if digits else None

for name, url, target in PRODUCTS:
    price = get_price(url)
    if price is None:
        print(f"{name}: could not read price (page may be blocked)")
        continue
    print(f"{name}: Rs {price} (target {target})")
    if price <= target:
        notify(f"Price drop! {name} is Rs {price} (target Rs {target})\n{url}")
