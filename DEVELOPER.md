# 🛠️ Developer Guide & Command Cheatsheet

Welcome to the developer documentation for **MapLeadScraper**. This guide covers project architecture, virtual environment setup, module breakdowns, execution commands, and standard Git workflows for contributing to the repository.

---

## 📁 Project Architecture & Directory Layout

```text
D:\MapLeadScraper\
├── config.py           # Project constants, timeouts, output paths, & pitch templates
├── scraper.py          # Playwright Google Maps scraper & deep element parser
├── lead_processor.py   # Phone validation, lead classification, & copy generation
├── exporter.py         # CSV file export engine (UTF-8-SIG encoded)
├── main.py             # CLI entry point & summary reporting
├── requirements.txt    # Python package dependencies
├── README.md           # Quickstart guide
├── DEVELOPER.md        # Comprehensive developer & Git operations guide
├── .gitignore          # Ignored build files, venv, and CSV outputs
├── .venv/              # Python virtual environment (ignored by Git)
└── output/             # Exported lead CSV files (ignored by Git)
```

---

## ⚙️ 1. Virtual Environment Setup (`.venv`)

### Create Virtual Environment
```powershell
# Using standard Python
python -m venv .venv

# Or using uv (ultra-fast installer)
uv venv .venv
```

### Activate Virtual Environment
```powershell
# PowerShell (Windows)
.\.venv\Scripts\Activate.ps1

# CMD (Windows Command Prompt)
.\.venv\Scripts\activate.bat

# Git Bash / Linux / macOS
source .venv/bin/activate
```

> **PowerShell Execution Policy Fix** (if activation is blocked):
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Deactivate Virtual Environment
```powershell
deactivate
```

### Install / Update Dependencies
```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

---

## 📦 2. Module Breakdown: What Each File Does

### 1. `main.py` (CLI & Pipeline Orchestrator)
- **Role**: Entry point for command-line execution.
- **Responsibilities**:
  - Parses command-line arguments (`--location`, `--category`, `--max-results`, `--no-headless`).
  - Calls `run_scraper_sync()` from `scraper.py`.
  - Sends raw scraped results to `LeadProcessor`.
  - Triggers `LeadExporter` to write CSV files.
  - Prints real-time formatted execution metrics and summary reports.

### 2. `scraper.py` (Scraping & Browser Automation Engine)
- **Role**: Interacts with Google Maps via Playwright.
- **Responsibilities**:
  - Launches headless/headful Chromium browser instance.
  - Navigates to `https://www.google.com/maps/search/{category}+in+{location}`.
  - Handles dynamic scrolling inside Google Maps results pane (`div[role='feed']`).
  - Clicks into each listing card to open side detail panel (`div[role='main']`).
  - Extracts Name, Direct Phone Number, Website URL, Full Address, Rating, and Review Count using regex & BeautifulSoup.

### 3. `lead_processor.py` (Data Cleaning & Lead Categorization)
- **Role**: Business logic and lead routing.
- **Responsibilities**:
  - `clean_phone()`: Sanitizes phone strings into clean digit format.
  - **Filter**: Discards leads without phone numbers.
  - **Bucket 1 (Website Pitch)**: Phone exists + **No Website** -> Attaches tailored website creation outreach copy.
  - **Bucket 2 (Automation Pitch)**: Phone exists + **Website Exists** -> Attaches WhatsApp chatbot / Instagram DM / CRM automation pitch copy.

### 4. `exporter.py` (CSV Export Layer)
- **Role**: Data persistence into clean CSV files.
- **Responsibilities**:
  - `sanitize_filename()`: Normalizes user inputs for file names.
  - Exports `leads_<location>_<category>_website_pitch.csv`.
  - Exports `leads_<location>_<category>_automation_pitch.csv`.
  - Uses `utf-8-sig` encoding for compatibility with Excel and CRM tools.

### 5. `config.py` (Global Configurations & Copy Templates)
- **Role**: Centralized settings store.
- **Responsibilities**:
  - Configures `OUTPUT_DIR`, default timeouts, and user agents.
  - Stores message template functions `get_website_pitch_template()` and `get_automation_pitch_template()`.

---

## 🚀 3. How to Run the Lead Scraper

### Standard Run (Default: Salon in Gujarat, 20 results)
```powershell
.venv\Scripts\python.exe main.py
```

### Custom Location & Category
```powershell
.venv\Scripts\python.exe main.py --location "Ahmedabad, Gujarat" --category "Spa" --max-results 30
```

### Watch Scraper Run in Visible Browser (`--no-headless`)
```powershell
.venv\Scripts\python.exe main.py --location "Surat" --category "Dentist" --max-results 15 --no-headless
```

---

## 🌿 4. Git Cheatsheet (Fetch, Push, Merge, Pull, Rebase)

> Note: Using PortableGit path if standard `git` command is not in system PATH:
> `& "C:\Users\nanda\PortableGit\cmd\git.exe"`

### Basic Git Commands

#### Check Repository Status
```powershell
git status
```

#### Add Changes & Commit
```powershell
git add .
git commit -m "Describe your code changes here"
```

#### Fetch Updates from Remote GitHub
```powershell
git fetch origin
```

#### Pull Latest Code from Remote `main`
```powershell
git pull origin main
```

#### Push Local Commits to GitHub
```powershell
git push origin main
```

---

### Working with Branches & Merging

#### Create and Switch to a New Feature Branch
```powershell
git checkout -b feature/new-scraper-feature
```

#### Switch Back to `main` Branch
```powershell
git checkout main
```

#### Merge Feature Branch into `main`
```powershell
git checkout main
git merge feature/new-scraper-feature
git push origin main
```

#### Handle Rebase Conflicts (if remote updated)
```powershell
git pull origin main --rebase
# Resolve any file conflicts, then:
git add .
git rebase --continue
git push origin main
```

#### View Commit History
```powershell
git log --oneline -n 10
```
