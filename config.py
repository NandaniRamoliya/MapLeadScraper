import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Scraper Settings
DEFAULT_HEADLESS = True
DEFAULT_MAX_RESULTS = 20
PAGE_TIMEOUT_MS = 60000

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_website_pitch_template(business_name: str, category: str, location: str) -> str:
    """
    Generates a personalized WhatsApp outreach message for businesses WITHOUT a website.
    """
    return (
        f"Hi team {business_name} 👋,\n\n"
        f"I noticed your {category} in {location} has great reviews on Google Maps, but I couldn't find a website for your business.\n\n"
        f"Many potential clients looking for {category} services prefer to check modern price lists, portfolios, and online booking before visiting.\n\n"
        f"We build high-converting, affordable mobile websites for local businesses like yours in {location}. Would you be open to seeing a free 2-minute demo preview of what a website for {business_name} would look like?"
    )

def get_automation_pitch_template(business_name: str, category: str, location: str, website: str) -> str:
    """
    Generates a personalized WhatsApp/Social outreach message for businesses WITH a website.
    """
    return (
        f"Hi {business_name} team 👋,\n\n"
        f"I came across your business ({website}) while looking up top-rated {category} services in {location}!\n\n"
        f"We help businesses automate client inquiries via WhatsApp Chatbots, Instagram DM Auto-replies, and Instant Appointment Reminders to never lose a potential lead after hours.\n\n"
        f"Would you be interested in a quick 3-minute video showing how automated WhatsApp responses could save your team hours and convert more visitors into booked clients?"
    )
