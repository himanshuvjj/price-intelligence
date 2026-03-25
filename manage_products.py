# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import json
import time

# ============================================
# FUNCTION 1 : SEARCH AMAZON FOR A PRODUCT
# ============================================

def search_amazon(query):
    print(f"\nSearching for: {query}")

    # Search Google for Amazon India results
    # Much more reliable than searching Amazon directly
    search_query = query.replace(" ", "+")
    url = f"https://www.google.com/search?q=site:amazon.in+{search_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
    }

    try:
        time.sleep(1)
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        # Find all Google search result links
        links = soup.find_all("a")

        count = 0
        for link in links:
            href = link.get("href", "")

            # Only keep Amazon product links
            # Amazon product URLs contain "/dp/" followed by product ID
            if "amazon.in" in href and "/dp/" in href:

                # Clean up the URL Google wraps around it
                if href.startswith("/url?q="):
                    href = href.split("/url?q=")[1].split("&")[0]

                # Get product name from link text
                name = link.text.strip()
                if not name or len(name) < 5:
                    # Try parent element for name
                    name = link.find_parent().text.strip()[:70]

                # Clean up URL - remove everything after the ASIN
                if "/dp/" in href:
                    base = href.split("/dp/")[0]
                    asin = href.split("/dp/")[1].split("/")[0].split("?")[0]
                    clean_url = f"https://www.amazon.in/dp/{asin}"

                    # Avoid duplicates
                    if not any(r["url"] == clean_url for r in results):
                        count += 1
                        results.append({
                            "index": count,
                            "name": name[:70] if name else f"Product {count}",
                            "price": "will fetch on tracking",
                            "url": clean_url
                        })

            if count >= 5:
                break

        print(f"Found {len(results)} Amazon products")
        return results

    except Exception as e:
        print(f"Error: {e}")
        return []
    
    

# ============================================
# FUNCTION 2 : SHOW RESULTS TO USER
# ============================================

def show_results(results):
    """
    Shows search results nicely
    User picks which one to track
    """

    if not results:
        print("No results found. Try a different search term.")
        return None

    print("\n" + "=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)

    for r in results:
        print(f"\n  [{r['index']}] {r['name']}")
        print(f"       Price: Rs.{r['price']}")

    print("\n  [0] Cancel - search again")
    print("=" * 60)

    # Ask user to pick
    while True:
        try:
            choice = int(input("\nWhich product to track? Enter number: "))
            if choice == 0:
                return None
            if 1 <= choice <= len(results):
                return results[choice - 1]
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")


# ============================================
# FUNCTION 3 : SAVE PRODUCT TO TRACKING LIST
# ============================================

def save_product(product):
    """
    Saves selected product to products.json
    This file is what the scraper reads every day
    """

    # Load existing products
    try:
        with open("products.json", "r", encoding="utf-8") as f:
            tracked = json.load(f)
    except:
        tracked = []

    # Check if already tracking this product
    for p in tracked:
        if p["url"] == product["url"]:
            print(f"\nAlready tracking: {product['name'][:50]}")
            return

    # Add new product
    tracked.append({
        "name": product["name"],
        "url": product["url"]
    })

    # Save back to file
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(tracked, f, indent=2, ensure_ascii=False)

    print(f"\nAdded to tracking list: {product['name'][:50]}")
    print(f"Total products tracked: {len(tracked)}")


# ============================================
# FUNCTION 4 : SHOW ALL TRACKED PRODUCTS
# ============================================

def show_tracked():
    """Shows all products currently being tracked"""

    try:
        with open("products.json", "r", encoding="utf-8") as f:
            tracked = json.load(f)
    except:
        tracked = []

    if not tracked:
        print("\nNo products tracked yet!")
        return

    print("\n" + "=" * 60)
    print(f"TRACKED PRODUCTS ({len(tracked)} total)")
    print("=" * 60)
    for i, p in enumerate(tracked, 1):
        print(f"  [{i}] {p['name'][:60]}")
    print("=" * 60)


# ============================================
# MAIN MENU
# ============================================

def main():
    while True:
        print("\n" + "=" * 40)
        print("   PRICE INTELLIGENCE - PRODUCT MANAGER")
        print("=" * 40)
        print("  [1] Add new product to track")
        print("  [2] View all tracked products")
        print("  [3] Exit")
        print("=" * 40)

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            query = input("\nEnter product name to search: ").strip()
            if query:
                results = search_amazon(query)
                selected = show_results(results)
                if selected:
                    save_product(selected)

        elif choice == "2":
            show_tracked()

        elif choice == "3":
            print("\nGoodbye!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()