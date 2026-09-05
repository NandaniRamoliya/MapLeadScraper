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
                print(f"📥 Extracting deep contact details for top {max_results} listings...")
                
                # Re-locate elements dynamically
                locators = page.locator("div[role='article'] a.hfLiAc, div.Nv2PK a[href*='/maps/place/']")
                count = await locators.count()
                
                for i in range(min(count, max_results)):
                    name = ""
                    rating = ""
                    reviews_count = ""
                    address = ""
                    phone = ""
                    website = ""
                    maps_url = ""

                    try:
                        item = locators.nth(i)
                        # Scroll item into view and click to open side panel
                        await item.scroll_into_view_if_needed()
                        await item.click()
                        await page.wait_for_timeout(1500)

                        # Parse side pane details
                        pane_html = await page.content()
                        pane_soup = BeautifulSoup(pane_html, "html.parser")

                        # Title
                        h1_elem = pane_soup.find("h1", class_=re.compile(r"DUwfdc|fontTitleLarge"))
                        if h1_elem:
                            name = h1_elem.get_text(strip=True)

                        # Phone button / link
                        phone_btn = pane_soup.find("button", attrs={"data-item-id": re.compile(r"phone", re.I)}) or \
                                    pane_soup.find(attrs={"aria-label": re.compile(r"Phone:\s*[\d\+\s-]+", re.I)})
                        if phone_btn:
                            phone_label = phone_btn.get("aria-label", "") or phone_btn.get_text(strip=True)
                            phone_match = re.search(r"(\+?\d{1,4}[\s-]?\(?\d{2,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5})", phone_label)
                            if phone_match:
                                phone = phone_match.group(1).strip()
                            else:
                                phone = phone_label.replace("Phone:", "").strip()

                        # Website button / link
                        web_btn = pane_soup.find("a", attrs={"data-item-id": re.compile(r"authority", re.I)}) or \
                                  pane_soup.find("a", attrs={"aria-label": re.compile(r"Website:", re.I)})
                        if web_btn and web_btn.get("href"):
                            href = web_btn["href"]
                            if "google.com" not in href:
                                website = href

                        # Address
                        addr_btn = pane_soup.find("button", attrs={"data-item-id": re.compile(r"address", re.I)}) or \
                                   pane_soup.find(attrs={"aria-label": re.compile(r"Address:", re.I)})
                        if addr_btn:
                            address = addr_btn.get("aria-label", "").replace("Address:", "").strip() or addr_btn.get_text(strip=True)

                        # Rating & Reviews
                        rating_elem = pane_soup.find("div", class_=re.compile(r"F7L8d|fontBodyMedium"))
                        if rating_elem:
                            rating_text = rating_elem.get_text(strip=True)
                            r_match = re.search(r"(\d+\.\d+|\d+)", rating_text)
                            if r_match:
                                rating = r_match.group(1)

                        # Fallback for phone from text if pane search missed
                        if not phone:
                            text_body = pane_soup.get_text(separator=" ", strip=True)
                            phone_match = re.search(r"(\+91\s*[\d\s-]{10,12}|0?\d{10}|\+?\d{1,4}[\s-]?\d{10})", text_body)
                            if phone_match:
                                phone = phone_match.group(1).strip()

                    except Exception as err:
                        print(f"⚠️ Error extracting details for card #{i+1}: {err}")

                    if name or phone:
                        raw_leads.append({
                            "name": name or f"Business Lead #{i+1}",
                            "phone": phone,
                            "website": website,
                            "address": address,
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
