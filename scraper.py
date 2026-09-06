import asyncio
import re
import time
from typing import List, Dict
from playwright.async_api import async_playwright
from config import USER_AGENT, PAGE_TIMEOUT_MS

class GoogleMapsScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape(self, category: str, location: str, max_results: int = 30) -> List[Dict]:
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
                await page.wait_for_timeout(3500)

                # Dismiss consent / cookie dialogs if present
                try:
                    accept_btn = page.locator("button:has-text('Accept all'), button:has-text('I agree')")
                    if await accept_btn.count() > 0:
                        await accept_btn.first.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass

                # Locate feed pane and scroll
                feed_selector = "div[role='feed']"
                try:
                    await page.wait_for_selector(feed_selector, timeout=10000)
                except Exception:
                    pass

                scroll_attempts = 0
                max_scrolls = max(8, max_results // 2)

                while scroll_attempts < max_scrolls:
                    feed_locator = page.locator(feed_selector)
                    if await feed_locator.count() > 0:
                        await feed_locator.evaluate("el => el.scrollTop += 2500")
                    else:
                        await page.evaluate("window.scrollBy(0, 1500)")

                    await page.wait_for_timeout(2000)
                    scroll_attempts += 1

                    links_count = await page.locator("a.hfLiAc, a[href*='/maps/place/']").count()
                    if links_count >= max_results:
                        break

                # Collect place links & initial names from search feed
                cards = page.locator("div.Nv2PK, div[role='article']")
                total_found = await cards.count()
                print(f"📥 Found {total_found} business cards in search feed. Collecting listing targets...")

                place_targets = []
                for i in range(total_found):
                    if len(place_targets) >= max_results * 2:
                        break

                    card = cards.nth(i)
                    link_el = card.locator("a.hfLiAc, a[href*='/maps/place/']").first
                    if await link_el.count() > 0:
                        link_title = await link_el.get_attribute("aria-label") or ""
                        href = await link_el.get_attribute("href")
                        if href:
                            full_url = href if href.startswith("http") else "https://www.google.com" + href
                            place_targets.append({
                                "initial_name": link_title.strip(),
                                "url": full_url
                            })

                print(f"📥 Visiting {len(place_targets)} place pages for deep contact extraction...")

                # Direct URL Navigation for 100% reliable extraction
                for target in place_targets:
                    if len(raw_leads) >= max_results:
                        break

                    name = target["initial_name"]
                    phone = ""
                    website = ""
                    address = ""
                    rating = ""
                    reviews_count = "0"

                    try:
                        await page.goto(target["url"], wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
                        await page.wait_for_timeout(2200)

                        main_pane = page.locator("div[role='main']").first
                        if await main_pane.count() > 0:
                            # H1 Name
                            pane_h1 = main_pane.locator("h1.DUwfdc, h1.fontTitleLarge, h1").first
                            if await pane_h1.count() > 0:
                                h1_text = (await pane_h1.inner_text()).strip()
                                if h1_text and h1_text.lower() != "results" and not h1_text.startswith("Results for"):
                                    name = h1_text

                            # Phone
                            phone_button = main_pane.locator("button[data-item-id^='phone'], button[aria-label*='Phone:']").first
                            if await phone_button.count() > 0:
                                phone_aria = await phone_button.get_attribute("aria-label") or await phone_button.inner_text()
                                phone = re.sub(r"[^\d+]", "", phone_aria.replace("Phone:", ""))

                            # Fallback phone search in pane text if button missing
                            if not phone:
                                pane_text = await main_pane.inner_text()
                                p_match = re.search(r"(\+91[\s-]?\d{10}|\b0?\d{10}\b)", pane_text)
                                if p_match:
                                    phone = re.sub(r"[^\d+]", "", p_match.group(1))

                            # Website
                            web_button = main_pane.locator("a[data-item-id^='authority'], a[aria-label*='Website:']").first
                            if await web_button.count() > 0:
                                web_href = await web_button.get_attribute("href")
                                if web_href and "google.com" not in web_href:
                                    website = web_href

                            # Address
                            addr_button = main_pane.locator("button[data-item-id^='address'], button[aria-label*='Address:']").first
                            if await addr_button.count() > 0:
                                addr_aria = await addr_button.get_attribute("aria-label") or await addr_button.inner_text()
                                address = addr_aria.replace("Address:", "").strip()

                            # Rating
                            rating_loc = main_pane.locator("div.F7L8d, div.fontBodyMedium span[aria-hidden='true']").first
                            if await rating_loc.count() > 0:
                                r_text = await rating_loc.inner_text()
                                r_match = re.search(r"(\d+\.\d+|\d+)", r_text)
                                if r_match:
                                    rating = r_match.group(1)

                    except Exception as err:
                        print(f"⚠️ Error extracting {target['url']}: {err}")

                    if name and name.lower() != "results":
                        raw_leads.append({
                            "name": name,
                            "phone": phone,
                            "website": website,
                            "address": address,
                            "rating": rating,
                            "reviews_count": reviews_count,
                            "maps_url": target["url"]
                        })

            except Exception as e:
                print(f"❌ Error during scraping: {str(e)}")
            finally:
                await browser.close()

        return raw_leads

def run_scraper_sync(category: str, location: str, max_results: int = 30, headless: bool = True) -> List[Dict]:
    """Helper function to run async scraper synchronously."""
    scraper = GoogleMapsScraper(headless=headless)
    return asyncio.run(scraper.scrape(category, location, max_results))
