import asyncio
from playwright.async_api import async_playwright
import json
import os
import re
from datetime import datetime

# --- Configuration ---
URL_TO_SCRAPE = "https://en.uhomes.com/uk/london/imperial-college-london-icl"  # Or your preferred URL
PRICE_FILE = "uhomes_prices.json"
LOG_FILE = "discounts.log"

# Pop-up & Scraping Selectors (Ensure these are up-to-date)
COOKIE_ALLOW_SELECTOR = 'div.consent_button.all_action_button:has-text("Allow All")'
DREAM_HOME_CLOSE_SELECTOR = 'i.el-dialog__close.el-icon-close'  # Use the ICL one or add logic to try both
LISTING_SELECTOR = 'a.house-card.list'
NAME_SELECTOR = 'h2.title'
PRICE_SELECTOR = 'span.current-price'


# ---------------------

def clean_price(price_str):
    """Extracts numbers from the price string."""
    if not isinstance(price_str, str):
        return None
    match = re.search(r'£?([\d,]+)', price_str)
    return float(match.group(1).replace(',', '')) if match else None


def load_old_prices(filepath):
    """Loads previously saved prices."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {filepath}, starting fresh.")
            return {}
    return {}


def save_prices(filepath, data):
    """Saves current prices."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def log_change(message):
    """Logs a message to the console and a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def run_scraper():
    """Runs the Playwright scraper and returns data."""
    print("Starting Playwright scraper...")
    scraped_data = {}
    async with async_playwright() as p:
        # Run headlessly for automation!
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(URL_TO_SCRAPE, wait_until="networkidle", timeout=90000)
            print("Page loaded.")
            await page.wait_for_timeout(3000)

            # Handle Cookies (adjust timeout if needed)
            try:
                await page.locator(COOKIE_ALLOW_SELECTOR).click(timeout=10000)
                print("Clicked cookie banner.")
                await page.wait_for_timeout(500)
            except Exception:
                print("Cookie banner not found/clicked.")

            # Handle Dream Home (adjust timeout if needed)
            try:
                await page.locator(DREAM_HOME_CLOSE_SELECTOR).click(timeout=10000)
                print("Clicked 'Dream Home' close button.")
                await page.wait_for_timeout(500)
            except Exception:
                print("'Dream Home' pop-up not found/clicked.")

            print("Starting scraping...")
            await page.wait_for_selector(LISTING_SELECTOR, timeout=30000)
            listings = await page.locator(LISTING_SELECTOR).all()
            print(f"Found {len(listings)} listings.")

            for listing in listings:
                try:
                    link = await listing.get_attribute('href')
                    name = await listing.locator(NAME_SELECTOR).text_content(timeout=2000)
                    price_text = await listing.locator(PRICE_SELECTOR).text_content(timeout=2000)
                    price = clean_price(price_text)

                    if link and name and price is not None:
                        full_link = f"https://en.uhomes.com{link}" if link.startswith('/') else link
                        scraped_data[full_link] = {"name": name.strip(), "price": price}

                except Exception as e:
                    print(f"  - Error processing one listing: {e}")

        except Exception as e:
            print(f"FATAL ERROR during scraping: {e}")
            await page.screenshot(path="tracker_error.png")
        finally:
            await browser.close()

    print(f"Scraping finished. Extracted {len(scraped_data)} valid listings.")
    return scraped_data


async def track_prices():
    """Main tracking function."""
    old_prices = load_old_prices(PRICE_FILE)
    new_prices = await run_scraper()

    if not new_prices:
        print("No new data scraped. Aborting comparison.")
        return

    print("\nComparing prices...")
    changes_found = False
    for link, new_data in new_prices.items():
        old_data = old_prices.get(link)
        new_price = new_data["price"]
        name = new_data["name"]

        if old_data:
            old_price = old_data["price"]
            if new_price < old_price:
                log_change(f"DISCOUNT! {name}: £{old_price} -> £{new_price} | Link: {link}")
                changes_found = True
            elif new_price > old_price:
                log_change(f"PRICE UP! {name}: £{old_price} -> £{new_price} | Link: {link}")
                changes_found = True
            # else: print(f"  - No change for {name}") # Optional: log no changes

        else:
            log_change(f"NEW LISTING! {name}: £{new_price} | Link: {link}")
            changes_found = True

    # Check for removed listings (optional)
    for link, old_data in old_prices.items():
        if link not in new_prices:
            log_change(f"REMOVED! {old_data['name']} (was £{old_data['price']}) | Link: {link}")
            changes_found = True

    if not changes_found:
        print("No price changes or new/removed listings detected.")

    print(f"\nSaving current prices to {PRICE_FILE}...")
    save_prices(PRICE_FILE, new_prices)
    print("Tracker finished.")


# --- Run the main tracking function ---
if __name__ == "__main__":
    asyncio.run(track_prices())
