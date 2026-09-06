import os
from pathlib import Path
from typing import List, Dict
import pandas as pd
from config import OUTPUT_DIR

class LeadExporter:
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
        Exports categorized leads into CSV files ONLY.
        Returns dictionary of created CSV file paths.
        """
        cat_str = cls.sanitize_filename(category)
        loc_str = cls.sanitize_filename(location)
        
        file_prefix = f"leads_{loc_str}_{cat_str}"
        website_csv_path = OUTPUT_DIR / f"{file_prefix}_website_pitch.csv"
        automation_csv_path = OUTPUT_DIR / f"{file_prefix}_automation_pitch.csv"

        df_website = pd.DataFrame(website_pitch_leads)
        df_automation = pd.DataFrame(automation_pitch_leads)

        # Export CSV files ONLY
        if not df_website.empty:
            df_website.to_csv(website_csv_path, index=False, encoding="utf-8-sig")

        if not df_automation.empty:
            df_automation.to_csv(automation_csv_path, index=False, encoding="utf-8-sig")

        return {
            "website_csv": str(website_csv_path) if not df_website.empty else None,
            "automation_csv": str(automation_csv_path) if not df_automation.empty else None
        }
