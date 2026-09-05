import re
from typing import Dict, List, Tuple
from config import get_website_pitch_template, get_automation_pitch_template

class LeadProcessor:
    @staticmethod
    def clean_phone(phone_str: str) -> str:
        """
        Cleans raw phone numbers into standard format with country code handling.
        """
        if not phone_str:
            return ""
        # Remove non-digit characters except leading '+'
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
        - Splits remaining leads into Website Pitch Leads vs. Automation Pitch Leads.
        - Generates tailored pitch messages.

        Returns:
            (website_pitch_leads, automation_pitch_leads, total_skipped_count)
        """
        website_pitch_leads = []
        automation_pitch_leads = []
        skipped_count = 0

        for item in raw_leads:
            name = item.get("name", "").strip()
            phone = item.get("phone", "").strip()
            website = item.get("website", "").strip()
            address = item.get("address", "").strip()
            rating = item.get("rating", "")
            reviews_count = item.get("reviews_count", "")
            maps_url = item.get("maps_url", "")

            # Filter: Skip if no phone / contact details available
            if not phone:
                skipped_count += 1
                continue

            cleaned_phone = LeadProcessor.clean_phone(phone)

            # Check if website is present
            has_website = bool(website and len(website) > 4 and website.lower() != "n/a")

            lead_data = {
                "Business Name": name,
                "Category": category.title(),
                "Location": location.title(),
                "Phone Number": cleaned_phone or phone,
                "Has Website": "Yes" if has_website else "No",
                "Website URL": website if has_website else "N/A",
                "Google Rating": rating or "N/A",
                "Reviews Count": reviews_count or "0",
                "Full Address": address or "N/A",
                "Google Maps URL": maps_url or "N/A"
            }

            if not has_website:
                # Category 1: No Website -> Website Pitch
                lead_data["Lead Classification"] = "Website Pitch"
                lead_data["Outreach Pitch Copy"] = get_website_pitch_template(name, category, location)
                website_pitch_leads.append(lead_data)
            else:
                # Category 2: Has Website -> Automation & Social Pitch
                lead_data["Lead Classification"] = "Automation & Social Pitch"
                lead_data["Outreach Pitch Copy"] = get_automation_pitch_template(name, category, location, website)
                automation_pitch_leads.append(lead_data)

        return website_pitch_leads, automation_pitch_leads, skipped_count
