import asyncio
from playwright.async_api import async_playwright
import nest_asyncio
import json  # To print results nicely

# Apply nest_asyncio for Jupyter compatibility
nest_asyncio.apply()

# --- Configuration ---
LONDON_URL = "https://en.uhomes.com/uk/london/imperial-college-london-icl/u96a1-sorta2"

# Pop-up Selectors (Working!)
COOKIE_ALLOW_SELECTOR = 'div.consent_button.all_action_button:has-text("Allow All")'
DREAM_HOME_CLOSE_SELECTOR = 'div.lead-form-dialog div.close'
DREAM_HOME_CLOSE_SELECTOR = 'i.el-dialog__close.el-icon-close'

# <i class="el-dialog__close el-icon el-icon-close"></i>
# --- NEW: Scraping Selectors (Based on your HTML) ---
LISTING_SELECTOR = 'a.house-card.list'
NAME_SELECTOR = 'h2.title'
ADDRESS_SELECTOR = 'div.location'
PRICE_SELECTOR = 'span.current-price'
AMENITIES_SELECTOR = 'div.tags-box span.item'
# ---------------------------------------------------

print("Libraries imported. All pop-up and scraping selectors defined.")


async def scrape_london_uhomes():
    """
    Opens uhomes.com, handles pop-ups, and scrapes listing data.
    """
    print("Starting Playwright...")
    scraped_data = []  # List to hold our results
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False)  # Keep visible for now
    page = await browser.new_page()
    print(f"Playwright started. Navigating to {LONDON_URL}...")

    try:
        # Go to the page
        await page.goto(LONDON_URL, wait_until="networkidle", timeout=60000)  # Wait for network idle
        print("Page loaded. Waiting 3 seconds...")
        await page.wait_for_timeout(3000)

        # --- 1. Attempt to click the cookie banner (FIRST) ---
        try:
            print(f"  - Looking for cookie banner: {COOKIE_ALLOW_SELECTOR}")
            await page.locator(COOKIE_ALLOW_SELECTOR).click(timeout=7000)
            print("  - Clicked cookie banner.")
            await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  - Could not click cookie banner: {type(e).__name__}")
        # ----------------------------------------

        # --- 2. Attempt to close 'Dream Home' Pop-up (SECOND) ---
        try:
            print(f"  - Looking for Dream Home close button: {DREAM_HOME_CLOSE_SELECTOR}")
            await page.locator(DREAM_HOME_CLOSE_SELECTOR).click(timeout=10 * 7000)
            print("  - Clicked 'Dream Home' close button.")
            await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  - Could not click 'Dream Home' close button: {type(e).__name__}")
        # ----------------------------------------

        print("\nPop-up handling done. Starting scraping...")
        await page.wait_for_timeout(3000)  # Final wait before scraping

        # --- 3. Scrape the listings ---
        print(f"Looking for listings with selector: {LISTING_SELECTOR}")
        await page.wait_for_selector(LISTING_SELECTOR, timeout=20000)
        listings = await page.locator(LISTING_SELECTOR).all()
        print(f"Found {len(listings)} listings on this page.")

        for i, listing in enumerate(listings):
            print(f"  - Processing listing {i + 1}...")
            try:
                name = await listing.locator(NAME_SELECTOR).text_content(timeout=2000)
                address = await listing.locator(ADDRESS_SELECTOR).text_content(timeout=2000)
                price = await listing.locator(PRICE_SELECTOR).text_content(timeout=2000)
                link = await listing.get_attribute('href')

                # Get all amenities - this returns a list of strings
                amenity_elements = await listing.locator(AMENITIES_SELECTOR).all()
                amenities = [await amenity.text_content() for amenity in amenity_elements]
                # Clean up amenities (remove empty strings, strip whitespace)
                amenities = [a.strip() for a in amenities if a and a.strip()]

                # Build the full URL for the link
                full_link = f"https://en.uhomes.com{link}" if link and link.startswith('/') else link

                scraped_data.append({
                    "name": name.strip() if name else "N/A",
                    "address": address.strip() if address else "N/A",
                    "price_per_week": price.strip() if price else "N/A",
                    "amenities": amenities,
                    "link": full_link
                })
                print(f"    -> Scraped: {name.strip() if name else 'N/A'}")

            except Exception as e:
                print(f"    -> FAILED to process listing {i + 1}: {e}")

            await page.wait_for_timeout(50)  # Tiny delay between listings

        # -----------------------------

    except Exception as e:
        print(f"An major error occurred during scraping: {e}")
        await page.screenshot(path="scraping_error_screenshot.png")
        print("Saved screenshot to scraping_error_screenshot.png")

    finally:
        # Ensure the browser is always closed
        print("Closing browser...")
        await browser.close()
        await p.stop()
        print("Browser closed.")

    # --- *** NEW: Save the data to a JSON file *** ---
    if scraped_data:
        try:
            with open('uhomes_data.json', 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=4)
            print(f"Successfully saved {len(scraped_data)} listings to uhomes_data.json")
        except Exception as e:
            print(f"Error saving data to JSON: {e}")
    else:
        print("No data was scraped, so no file was saved.")
    # --- *** End of New Code *** ---

    return scraped_data # Still return the data