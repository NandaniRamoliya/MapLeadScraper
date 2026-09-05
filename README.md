# 🚀 Lead Generation Web Scraper & Categorizer

A Python web scraping and lead classification engine built for digital agencies, sales teams, and freelancers to generate targeted business leads.

It searches local business listings (such as Google Maps) by **location** (e.g. `Gujarat`) and **category** (e.g. `Salon`), extracts contact details, filters out contact-less entries, classifies qualified leads into pitch buckets, and exports formatted Excel and CSV files complete with tailored WhatsApp outreach messages.

---

## 📌 Features & Lead Routing Logic

- 🔍 **Dynamic Search**: Scrapes businesses by location & category.
- 📱 **Contact Filter**: Omits listings without phone numbers.
- 🌐 **Bucket 1: Website Pitch Leads**
  - **Condition**: Phone/WhatsApp available + **NO Website**.
  - **Goal**: Pitch custom mobile website design & online booking.
- 🤖 **Bucket 2: Automation & Social Media Pitch Leads**
  - **Condition**: Phone/WhatsApp available + **Website Exists**.
  - **Goal**: Pitch WhatsApp automated chatbots, Instagram DM auto-replies, appointment reminders, and social management.
- 📑 **Multi-Tab Excel & CSV Export**: Automatically exports `Website Pitch Leads` and `Automation Pitch Leads` into separate spreadsheets with auto-crafted outreach message templates.

---

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 🏃 Usage Examples

### Default Run (Salon in Gujarat)
```bash
python main.py
```

### Custom Location & Category
```bash
python main.py --location "Ahmedabad, Gujarat" --category "Spa & Salon" --max-results 30
```

### Options & Flags
- `-l`, `--location`: Target city, state, or region (e.g. `Gujarat`, `Surat`).
- `-c`, `--category`: Business niche (e.g. `Salon`, `Dentist`, `Restaurant`).
- `-m`, `--max-results`: Maximum leads to fetch (default: `20`).
- `--no-headless`: Run browser with visual UI window open.

---

## 📁 Output Structure

The generated Excel workbook will be saved in the `output/` folder:
- `output/leads_gujarat_salon.xlsx`
  - Sheet 1: `Website Pitch Leads`
  - Sheet 2: `Automation Pitch Leads`
- `output/leads_gujarat_salon_website_pitch.csv`
- `output/leads_gujarat_salon_automation_pitch.csv`
