import re
from typing import Dict, List, Tuple
from config import get_website_pitch_template, get_automation_pitch_template

class LeadProcessor:
    SOCIAL_DOMAINS = [
        "instagram.com", "facebook.com", "fb.com", "twitter.com", "x.com",
        "linkedin.com", "youtube.com", "justdial.com", "indiamart.com",
        "pinterest.com", "tiktok.com", "t.me", "wa.me"
    ]

    @staticmethod
    def is_social_profile(url: str) -> bool:
        """Returns True if the URL is a social media profile link rather than an official website."""
        if not url:
            return False
        url_lower = url.lower()
        return any(domain in url_lower for domain in LeadProcessor.SOCIAL_DOMAINS)

    @staticmethod
    def clean_phone(phone_str: str) -> str:
        """Cleans raw phone numbers into standard format."""
        if not phone_str:
            return ""
        cleaned = re.sub(r"[^\d+]", "", phone_str)
        return cleaned

    @staticmethod
    def process_raw_leads(
        raw_leads: List[Dict],
        category: str,
        location: str
    ) -> Tuple[List[Dict], List[Dict], int]:
        """
        Processes raw scraped lead records:
        - Skips leads without a phone number / contact detail.
        - Deduplicates by phone number and business name.
        - Categorizes into Website Pitch Leads vs. Automation Pitch Leads.
        """
        website_pitch_leads = []
        automation_pitch_leads = []
        skipped_count = 0
        seen_phones = set()
        seen_names = set()

        for item in raw_leads:
            name = item.get("name", "").strip()
            phone = item.get("phone", "").strip()
            website = item.get("website", "").strip()
            address = item.get("address", "").strip()
            rating = item.get("rating", "")
            reviews_count = item.get("reviews_count", "")
            maps_url = item.get("maps_url", "")

            # Ignore generic placeholders
            if not name or name.lower() == "results" or name.startswith("Results for"):
                skipped_count += 1
                continue

            cleaned_phone = LeadProcessor.clean_phone(phone)

            # Filter: Skip if no valid phone / contact details available
            if not cleaned_phone or len(cleaned_phone) < 8:
                skipped_count += 1
                continue

            # Deduplication Check
            dedup_key = (cleaned_phone, name.lower())
            if cleaned_phone in seen_phones or name.lower() in seen_names:
                skipped_count += 1
                continue

            seen_phones.add(cleaned_phone)
            seen_names.add(name.lower())

            # Website classification: Custom domain vs Social profile vs No website
            is_social = LeadProcessor.is_social_profile(website)
            has_website = bool(website and len(website) > 4 and website.lower() != "n/a" and not is_social)

            lead_data = {
                "Business Name": name,
                "Category": category.title(),
                "Location": location.title(),
                "Phone Number": cleaned_phone,
                "Has Official Website": "Yes" if has_website else "No",
                "Website URL": website if has_website else "N/A",
                "Social Profile URL": website if is_social else "N/A",
                "Google Rating": rating or "N/A",
                "Reviews Count": reviews_count or "0",
                "Full Address": address or "N/A",
                "Google Maps URL": maps_url or "N/A"
            }

            if not has_website:
                # Category 1: No Custom Website -> Website Pitch Lead
                lead_data["Lead Classification"] = "Website Pitch"
                lead_data["Outreach Pitch Copy"] = get_website_pitch_template(name, category, location)
                website_pitch_leads.append(lead_data)
            else:
                # Category 2: Has Custom Website -> Automation & Social Pitch Lead
                lead_data["Lead Classification"] = "Automation & Social Pitch"
                lead_data["Outreach Pitch Copy"] = get_automation_pitch_template(name, category, location, website)
                automation_pitch_leads.append(lead_data)

        return website_pitch_leads, automation_pitch_leads, skipped_count
