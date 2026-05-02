# Printable Notes Generator for PW And Other Platforms 📄

A lightweight desktop tool to automatically crop, invert, format, and merge PDF lecture slides for better readability and printing.

[![Download Latest Release](https://img.shields.io/github/v/release/Ash-023/printable-notes-generator?style=for-the-badge&label=Download%20Latest%20Version&color=success)](https://github.com/Ash-023/printable-notes-generator/releases/latest)

[![Download Latest Release](https://img.shields.io/github/v/release/Ash-023/printable-notes-generator?style=for-the-badge&label=Download%20Latest%20Version&color=success)](https://github.com/Ash-023/printable-notes-generator/releases/latest)
---

## How It Works & Features

This tool is designed to process batches of PDF slides and make them print-friendly or easier to read. When you run the tool, it performs the following automated steps:

- **Smart Folder Replication:** You don't have to process files one by one. If you select a main "Source" folder that contains multiple sub-folders (e.g., `Math/Week1/`), the app perfectly recreates that exact folder structure in your "Destination" folder.
- **Ink-Saving & Dark Mode Conversion:** Automatically converts all slides to grayscale and inverts the colors (dark presentation backgrounds become white, and white text becomes black). This saves massive amounts of ink and reduces eye strain.
- **Custom Grid Layouts (N-Up):** Condenses multiple slides onto a single output page (e.g., 2, 3, 4, 6, or 9 slides per page).
- **Smart Page Orientation:** The app mathematically calculates the best fit for your chosen grid and automatically switches between Portrait and Landscape mode to ensure your slides are as large and readable as possible!
- **Smart PDF Merging & Reordering:** Optionally merge all individual PDFs within a subfolder into a single master PDF. Includes a built-in drag-and-drop interface that automatically groups files by topic so you can visually confirm the exact merge order.
- **Auto-Trimming:** Automatically remove the first page (usually a useless title slide) or the last page (usually a blank or "Thank You" slide) from every PDF.
- **Live Progress Tracking:** Watch the tool work with a real-time progress bar, file counter, and intelligent ETA calculator.
- **Precision Formatting:** Full control over output page size (defaults to standard A4: 210x297mm), margins, spacing between slides, and output image quality.

---

## For General Users (Easiest Way)

You do not need to install Python or know how to code to use this tool!

1. Click the **[Download Latest Version](https://github.com/Ash-023/printable-notes-generator/releases/latest)** button above.
2. Download the latest `Printable_Notes_Generator.exe` file under "Assets".
   _(For Mac Users: Download the zip file and extract it)._
3. Double-click the application to open it.

_(Note for Windows Users: Windows Defender may show a "Windows protected your PC" warning since this is an indie developer app. Click "More info" > "Run anyway" to proceed)._

_(Note for Mac Users: macOS may block it from opening initially. Right-Click or Control-click the application file, select "Open", and confirm)._

---

## How to Use the App

Once you have the application open, follow these steps to format your notes:

1. **Select Folders:** Use the "Browse" buttons to pick your `Source Folder` (where your original PDFs are) and your `Destination Folder` (where you want the new files saved).
2. **Trim Unwanted Slides:** If your lectures always have a useless title slide, set "Remove First Page" to **Yes**. Same for the last page.
3. **Choose Your Grid:** Select how many slides you want on a single piece of paper (e.g., `3` is a great balance of size and paper-saving).
4. **(Optional) Merge PDFs:** If you check the **"Merge subfolder PDFs"** box, the app will combine multiple lectures from the same folder into one file.
   - _When you click Start, a pop-up window will appear allowing you to click and drag your files into the exact order you want them merged!_
5. **Start Processing:** Click the big green button, sit back, and watch the progress bar!

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

- **`src/app_gui.py`**: The Tkinter frontend, interactive treeview, and threading logic.
- **`src/slide_processor.py`**: The core PyMuPDF manipulation engine (handles natural sorting, smart orientation, and image generation).
- **`src/direct_executable.py`**: The Command-Line executable logic.
- **`src/utils/`**: Contains utility functions.
- **`config/`**: Contains the template JSON for headless execution.
- **`assets/`**: Contains the application icon files.

### How to Build the Executable Locally

1. Clone the repo and install requirements (`pip install -r requirements.txt`).
2. Run PyInstaller from the root directory to bundle the app and embed the custom icon:
   ```bash
   pyinstaller --onefile --windowed --icon="assets/icon.ico" --add-data "assets/icon.ico:assets" --name "Printable_Notes_Generator" src/app_gui.py
   ```
3. The standalone .exe (or .app on Mac) will be generated inside the newly created dist/ folder.
