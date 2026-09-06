import os
from pathlib import Path
from typing import List, Dict
import pandas as pd
from config import OUTPUT_DIR

class LeadExporter:
    DEFAULT_COLUMNS = [
        "Business Name", "Category", "Location", "Phone Number",
        "Has Official Website", "Website URL", "Social Profile URL",
        "Google Rating", "Reviews Count", "Full Address",
        "Google Maps URL", "Lead Classification", "Outreach Pitch Copy"
    ]

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitizes text for safe filename generation."""
        return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name.lower())

    @classmethod
    def export_to_files(
        cls,
        website_pitch_leads: List[Dict],
        automation_pitch_leads: List[Dict],
        category: str,
        location: str
    ) -> Dict[str, str]:
        """
        Exports categorized leads into BOTH CSV files (Website Pitch & Automation Pitch).
        Always creates both files even if one category has 0 leads.
        """
        cat_str = cls.sanitize_filename(category)
        loc_str = cls.sanitize_filename(location)
        
        file_prefix = f"leads_{loc_str}_{cat_str}"
        website_csv_path = OUTPUT_DIR / f"{file_prefix}_website_pitch.csv"
        automation_csv_path = OUTPUT_DIR / f"{file_prefix}_automation_pitch.csv"

        df_website = pd.DataFrame(website_pitch_leads) if website_pitch_leads else pd.DataFrame(columns=cls.DEFAULT_COLUMNS)
        df_automation = pd.DataFrame(automation_pitch_leads) if automation_pitch_leads else pd.DataFrame(columns=cls.DEFAULT_COLUMNS)

        # Export BOTH CSV files ALWAYS
        df_website.to_csv(website_csv_path, index=False, encoding="utf-8-sig")
        df_automation.to_csv(automation_csv_path, index=False, encoding="utf-8-sig")

        return {
            "website_csv": str(website_csv_path),
            "automation_csv": str(automation_csv_path)
        }
