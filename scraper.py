import asyncio
import re
import time
from typing import List, Dict
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from config import USER_AGENT, PAGE_TIMEOUT_MS

class GoogleMapsScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape(self, category: str, location: str, max_results: int = 20) -> List[Dict]:
        """
        Scrapes Google Maps for a given category and location up to max_results.
        Returns a list of raw business dictionaries.
        """
        search_query = f"{category} in {location}"
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        print(f"🔍 Searching Google Maps for: '{search_query}'...")

        raw_leads = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()

            try:
                await page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)

                # Dismiss cookie/consent dialogs if present
                try:
                    accept_btn = page.locator("button:has-text('Accept all'), button:has-text('I agree')")
                    if await accept_btn.count() > 0:
                        await accept_btn.first.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass

                # Locate the results feed pane
                feed_selector = "div[role='feed']"
                try:
                    await page.wait_for_selector(feed_selector, timeout=10000)
                except Exception:
                    print("⚠️ Results feed pane not found directly. Attempting general list extraction.")

                # Scroll loop to load dynamic results
                previous_count = 0
                scroll_attempts = 0
                max_scrolls = max(5, max_results // 2)

                while len(raw_leads) < max_results and scroll_attempts < max_scrolls:
                    # Scroll down inside the feed pane
                    feed_locator = page.locator(feed_selector)
                    if await feed_locator.count() > 0:
                        await feed_locator.evaluate("el => el.scrollTop += 1500")
                    else:
                        await page.evaluate("window.scrollBy(0, 1000)")

                    await page.wait_for_timeout(2000)
                    scroll_attempts += 1

                    # Check current list of items
                    items = await page.locator("div[role='article'], a.hfLiAc, div.Nv2PK").all()
                    if len(items) == previous_count and len(items) > 0:
                        # End of feed or reached bottom
                        if scroll_attempts > 3:
                            break
                    previous_count = len(items)

                # Parse loaded business entries
                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                articles = soup.find_all("div", {"role": "article"}) or soup.find_all("div", class_="Nv2PK")

                print(f"📥 Found {len(articles)} business cards in page source. Parsing details...")

                # Detail Extraction Loop
                for article in articles[:max_results]:
                    name = ""
                    rating = ""
                    reviews_count = ""
                    address = ""
                    phone = ""
                    website = ""
                    maps_url = ""

                    # Name
                    title_elem = article.find("div", class_=re.compile(r"fontHeadlineSmall|qBF1Pd|header")) or article.find("a", class_=re.compile(r"hfLiAc"))
                    if title_elem:
                        name = title_elem.get_text(strip=True)

                    # Link / Maps URL
                    link_elem = article.find("a", href=re.compile(r"/maps/place/"))
                    if link_elem and link_elem.get("href"):
                        maps_url = link_elem["href"]
                        if not maps_url.startswith("http"):
                            maps_url = "https://www.google.com" + maps_url

                    # Rating & Reviews
                    aria_elem = article.find(attrs={"aria-label": re.compile(r"stars|rating", re.I)})
                    if aria_elem and aria_elem.get("aria-label"):
                        aria_text = aria_elem["aria-label"]
                        rating_match = re.search(r"(\d+\.\d+|\d+)\s*stars?", aria_text, re.I)
                        reviews_match = re.search(r"(\d+)\s*Reviews?", aria_text, re.I)
                        if rating_match:
                            rating = rating_match.group(1)
                        if reviews_match:
                            reviews_count = reviews_match.group(1)

                    # Text details (Phone, Address, Website)
                    body_text = article.get_text(separator=" | ", strip=True)

                    # Phone Extraction Regex
                    phone_match = re.search(r"(\+?\d{1,4}[\s-]?\(?\d{2,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5})", body_text)
                    if phone_match:
                        phone = phone_match.group(1).strip()

                    # Website link inside card
                    web_elem = article.find("a", attrs={"data-value": re.compile(r"Website|website", re.I)}) or article.find("a", href=re.compile(r"http(s)?://"))
                    if web_elem and web_elem.get("href"):
                        href = web_elem["href"]
                        if "google.com" not in href and "google.co.in" not in href:
                            website = href

                    if name:
                        raw_leads.append({
                            "name": name,
                            "phone": phone,
                            "website": website,
                            "address": body_text,
                            "rating": rating,
                            "reviews_count": reviews_count,
                            "maps_url": maps_url
                        })

            except Exception as e:
                print(f"❌ Error during scraping: {str(e)}")
            finally:
                await browser.close()

        return raw_leads

def run_scraper_sync(category: str, location: str, max_results: int = 20, headless: bool = True) -> List[Dict]:
    """Helper function to run async scraper synchronously."""
    scraper = GoogleMapsScraper(headless=headless)
    return asyncio.run(scraper.scrape(category, location, max_results))
