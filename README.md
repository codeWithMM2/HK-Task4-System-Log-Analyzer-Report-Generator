# 🐍 System Log Analyzer & Report Generator

An advanced, high-performance CLI tool developed in Python to parse, analyze, search, and monitor system/application log files. Developed as part of **Task 4** for the **Python Internship 2026 (HK)**.

---

## 👩‍💻 Developer Details
- **Name:** Maryam
- **Project:** System Log Analyzer & Report Generator (Task 4)
- **Batch:** Python Internship 2026 (HK)

---

## 📚 Libraries Used & Technical Purpose

This project is built using a mix of Python's native standard libraries and advanced third-party modules to achieve maximum efficiency and visual appeal.

### 1. Built-in Standard Libraries (No Installation Required)
* **`re` (Regular Expressions):** Used as the core "detective" engine. Pre-compiled regex patterns (`re.compile`) scan thousands of log lines instantly to extract timestamps and log levels.
* **`threading` (Multithreading):** Powers the **Live Monitor** feature. It spawns a background daemon thread (`tail -f` simulation) to read log additions on-the-fly while keeping the main menu responsive.
* **`os` (Operating System):** Handles file system operations, checks file existence (`os.path.exists`), validates file formats, and prevents empty file processing (`os.path.getsize`).
* **`csv` (Comma-Separated Values):** Handles data writing to structured tabular sheets, converting raw log dicts into clean `.csv` reports for Excel.
* **`collections (defaultdict)`:** Used for optimized, error-free counting. Unlike a standard dictionary, `defaultdict(int)` avoids `KeyError` by automatically initializing new log categories from `0`.
* **`sys` & `time`:** Used for system termination (`sys.exit`) and putting threads to sleep (`time.sleep`) during live tracking to minimize CPU overhead.
* **`datetime`:** Fetches the current system time to add accurate "Generated on" timestamps to exported reports.

### 2. Third-Party Libraries (Advanced Bonus Features)
* **`matplotlib` (Data Visualization):** Translates log analytics into high-quality visual data. Generates dark-themed Bar Charts and Pie Charts to present log level distribution.
* **`fpdf2` (PDF Generation):** An advanced document styling library used to compile the log analysis results, level breakdowns, and top critical errors into a clean, professional `.pdf` document.

---

## 🚀 Key Features Implemented

* **Smart Log Ingestion:** Accepts both `.txt` and `.log` extensions, handling complex encoding symbols gracefully using `errors='replace'`.
* **Deep Log Analytics:** Generates terminal-based visual histograms showing the percentage share and direct counts of each log level (INFO, WARNING, ERROR, etc.).
* **Dynamic Search & Filter:** Case-insensitive search by custom keywords, or isolated sorting by specific Date patterns and Log Levels.
* **Multi-Format Export Engine:** Automatically creates custom-named files or uses timestamps to prevent overwriting.
  * **TXT:** Formatted human-readable text report.
  * **CSV:** Raw data matrix ready for spreadsheets.
  * **PDF:** Document report with clean hierarchy and typography.
* **Visual Reports (PNG Chart):** Automatically saves a high-resolution dark-mode visualization image (`chart_TIMESTAMP.png`).
* **Real-Time Live Monitor:** Simulates a live server tail monitor. Pressing `Enter` securely signals the background thread to stop using `threading.Event()`.

---

## 🛠️ Advanced Guardrails (Error Handling)

- **Empty File Protection:** Stops execution if file size is 0 bytes.
- **Missing File Graceful Exit:** Catches file path typos without crashing.
- **Permission Check:** Handles blocked/system-restricted file errors smoothly.
- **Case Insensitivity:** All search patterns utilize the `re.I` flag for flexibility.

---

## ⚙️ How To Run The Project

### 1. Install External Dependencies
Before running, open your terminal/command prompt and install the visualization tools:
```bash
pip install matplotlib fpdf2
And then type this to run:
python System log Analyzer.py
---

## 📹 Project Demo Video
A complete 1-minute walkthrough video demonstrating all the features of this tool is available directly in this repository:
- **File Name:** `System log Analyzer demo video .mp4`
- **Duration:** ~1 Minute (Quick Demo)
- **Features Showcased:** Log Ingestion, Dynamic Search, Level Filters, Matplotlib Dark Chart Export, Professional PDF Generation, and Live Multi-threaded Monitoring.

---
