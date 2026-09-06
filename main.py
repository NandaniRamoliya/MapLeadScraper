import argparse
import sys
import time
from scraper import run_scraper_sync
from lead_processor import LeadProcessor
from exporter import LeadExporter

def main():
    parser = argparse.ArgumentParser(
        description="🚀 Web Scraper & Lead Categorizer for Sales & Agency Outreach"
    )
    parser.add_argument(
        "-c", "--category",
        type=str,
        default=None,
        help="Business category (e.g. Salon, Spa, Dentist, Restaurant). Required."
    )
    parser.add_argument(
        "-l", "--location",
        type=str,
        default="Gujarat",
        help="Target location/city/state (default: Gujarat)"
    )
    parser.add_argument(
        "-m", "--max-results",
        type=int,
        default=30,
        help="Maximum number of business leads to extract (default: 30)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in headful mode (visible window)"
    )

    args = parser.parse_args()

    # Category handling: Require input if not provided via CLI flag
    category = args.category.strip() if args.category else ""
    if not category:
        try:
            category = input("🏷️ Enter target business category (e.g. Salon, Spa, Dentist): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled.")
            sys.exit(0)

    if not category:
        print("❌ Error: Category is required to perform search.")
        sys.exit(1)

    location = args.location.strip() if args.location else "Gujarat"
    max_results = args.max_results
    headless = not args.no_headless

    print("=" * 60)
    print("🎯 LEAD GENERATION SCRAPER & CATEGORIZER")
    print(f"📍 Location     : {location}")
    print(f"🏷️  Category     : {category}")
    print(f"📊 Max Targets  : {max_results}")
    print(f"🖥️  Headless     : {headless}")
    print("=" * 60)

    start_time = time.time()

    # Step 1: Scrape Raw Leads
    raw_leads = run_scraper_sync(category, location, max_results, headless)
    total_scraped = len(raw_leads)

    if not raw_leads:
        print("❌ No business listings found. Try relaxing search criteria.")
        sys.exit(0)

    # Step 2: Clean, Filter & Categorize Leads
    website_pitch_leads, automation_pitch_leads, skipped_count = LeadProcessor.process_raw_leads(
        raw_leads, category, location
    )

    # Step 3: Export to CSV
    export_files = LeadExporter.export_to_files(
        website_pitch_leads, automation_pitch_leads, category, location
    )

    elapsed_time = round(time.time() - start_time, 2)

    # Step 4: Summary Report
    print("\n" + "=" * 60)
    print("🎉 LEAD PROCESSING SUMMARY REPORT")
    print("=" * 60)
    print(f"📥 Total Scraped Listings      : {total_scraped}")
    print(f"🚫 Skipped (No Phone Contact)  : {skipped_count}")
    print(f"🌐 Website Pitch Leads         : {len(website_pitch_leads)}")
    print(f"🤖 Automation & Social Pitch   : {len(automation_pitch_leads)}")
    print(f"⏱️  Time Elapsed               : {elapsed_time}s")
    print("-" * 60)
    print("📁 EXPORTED CSV FILES:")
    print(f"  📄 Website Pitch CSV    : {export_files['website_csv']}")
    print(f"  📄 Automation Pitch CSV : {export_files['automation_csv']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
