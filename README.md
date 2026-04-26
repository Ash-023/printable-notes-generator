# Printable Notes Generator for PW And Other Platforms📄

A lightweight desktop tool to automatically crop, invert, and format PDF lecture slides for better readability and printing.
[![Download Latest Release](https://img.shields.io/github/v/release/Ash-023/printable-notes-generator?style=for-the-badge&label=Download%20Latest%20Version&color=success)](https://github.com/Ash-023/printable-notes-generator/releases/latest)
---

## How It Works & Features

This tool is designed to process batches of PDF slides and make them print-friendly or easier to read. When you run the tool, it performs the following automated steps:

- **Smart Folder Replication:** You don't have to process files one by one. If you select a main "Source" folder that contains multiple sub-folders (e.g., `Math/Week1/`), the app will perfectly recreate that exact folder structure in your "Destination" folder. Your file organization stays completely intact!
- **Ink-Saving & Dark Mode Conversion:** Automatically converts all slides to grayscale and inverts the colors (e.g., dark presentation backgrounds become white, and white text becomes black). This saves massive amounts of ink when printing and reduces eye strain.
- **Custom Grid Layouts (N-Up):** Condenses multiple slides onto a single output page. It automatically calculates the best looking grid based on your input (e.g., 2, 3, 4, 6, or 9 slides per page).
- **Auto-Trimming:** Allows you to automatically remove the first page (usually a useless title slide) or the last page (usually a blank or "Thank You" slide) from every PDF.
- **Precision Formatting:** You have full control over the output page size (defaults to standard A4 dimensions: 210x297mm), page margins, spacing between slides, and image quality (DPI and JPG compression).

---

## For General Users (Easiest Way)

You do not need to install Python or know how to code to use this tool.

1. Click the **[Download Latest Version](https://github.com/Ash-023/printable-notes-generator/releases/latest)** button above.
2. Download the latest `Printable_Notes_Generator.exe` file under "Assets".
   For Mac Users: Download the zip file and extract it.
3. Double-click the `.exe` (for Windows Users) or `.app` (for Mac Users) to open the application window.
4. Select your folders, configure your slide settings, and hit "Start Processing"!

_(Note for Windows Users: Windows Defender may show a "Windows protected your PC" warning since this is an indie developer app. Click "More info" > "Run anyway" to proceed)._

_(Note for Mac Users: Because this is an indie application, macOS may block it from opening initially. To bypass this, Right-Click (or Control-click) the application file and select Open from the menu, then confirm you want to open it.)._

---

## For Command-Line Users

If you prefer running headless scripts without a GUI, you can use the core logic directly.

1. Ensure you have Python installed.
2. Clone this repository.
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `config/config.json`, modify it with your paths and preferences, and save it.
5. Run the script: `python src/direct_executable.py`

---

## For Developers

Want to modify the application or build the executable yourself?

### Repository Structure

- **`src/app_gui.py`**: The Tkinter frontend and threading logic.
- **`src/slide_processor.py`**: The core PyMuPDF manipulation engine.
- **`src/direct_executable.py`**: The Command-Line executable logic.
- **`config/`**: Contains the template JSON for headless execution.

### How to Build the Executable Locally

1. Clone the repo and install requirements (`pip install -r requirements.txt`).
2. Run PyInstaller from the root directory:
   ```bash
   pyinstaller --onefile --windowed --name "Printable_Notes_Generator" src/app_gui.py
   ```
3. The .exe will be generated inside a newly created dist/ folder.
