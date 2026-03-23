import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os 




# ============================================
# FUNCTION 1 : WRITE LOG
# ============================================

def write_log(message):
    log_path = "logs/scraper_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"📝 {log_entry.strip()}")


# ============================================
# FUNCTION 2 : FETCH PAGE
# ============================================

def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Page fetched successfully!")
            return response.text
        else:
            print(f"❌ Failed! Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ============================================
# FUNCTION 3 : EXTRACT DATA
# ============================================

def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extract product name
    try:
        name = soup.find("span", {"id": "productTitle"})
        name = name.text.strip()
    except:
        name = "Name not found"

    # Extract price
    try:
        price = soup.find("span", {"class": "a-price-whole"})
        price = price.text.strip()
        price = price.replace(",", "").replace(".", "")
        price = float(price)
    except:
        price = None
        print("⚠️ Price not found")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"📦 Product  : {name[:60]}...")
    print(f"💰 Price    : ₹{price}")
    print(f"🕐 Time     : {timestamp}")

    return {
        "name": name,
        "price": price,
        "timestamp": timestamp
    }


# ============================================
# FUNCTION 4 : SAVE TO DATABASE
# ============================================

def save_to_database(data, url):
    # Make sure data folder exists
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect("data/price_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            url       TEXT,
            name      TEXT,
            price     REAL,
            timestamp TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO prices (url, name, price, timestamp)
        VALUES (?, ?, ?, ?)
    """, (url, data["name"], data["price"], data["timestamp"]))

    conn.commit()
    conn.close()
    print("✅ Data saved to database!")


# ============================================
# FUNCTION 5 : VIEW HISTORY
# ============================================

def view_history(url):
    try:
        conn = sqlite3.connect("data/price_history.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, price, timestamp
            FROM prices
            WHERE url = ?
            ORDER BY timestamp DESC
        """, (url,))
        rows = cursor.fetchall()
        conn.close()

        print("\n📊 PRICE HISTORY")
        print("-" * 50)
        for row in rows:
            name, price, timestamp = row
            print(f"  ₹{price:,.0f}  |  {timestamp}")
    except:
        print("No history yet.")


# ============================================
# MAIN PROGRAM
# ============================================

if __name__ == "__main__":

    # 🔁 Add as many product URLs as you want here
    products = [
        "https://www.amazon.in/dp/B0CHX1W1XY",   # Change this to any product
    ]

    print("🚀 Starting Price Scraper...\n")
    write_log("🚀 Scraper started")

    for url in products:
        print(f"\n🔍 Scraping: {url}")
        html = get_page(url)

        if html:
            product_data = extract_data(html)

            if product_data["price"]:
                save_to_database(product_data, url)
                write_log(f"✅ Success — ₹{product_data['price']} — {product_data['name'][:40]}")
            else:
                write_log("⚠️ Price not found — possible block")
        else:
            write_log("❌ Page fetch failed")

    view_history(products[0])
    write_log("🏁 Scraper finished\n")
    print("\n✅ All done!")