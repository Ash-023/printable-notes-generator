import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import slide_processor 

def browse_source():
    folder = filedialog.askdirectory(title="Select Source Folder")
    if folder:
        source_folder.delete(0, tk.END)
        source_folder.insert(0, folder)

def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder")
    if folder:
        destination_folder.delete(0, tk.END)
        destination_folder.insert(0, folder)

def update_progress(current, total):
    """Callback function triggered by slide_processor to update the GUI bar"""
    progress_var.set((current / total) * 100)
    root.update_idletasks() # Force UI to refresh

def execute_processing_thread():
    """Runs in the background so the GUI doesn't freeze"""
    try:
        # Grab and validate simple inputs
        src = source_folder.get().strip()
        dest = destination_folder.get().strip()
        remove_first = True if rem_f_page.get() == "Yes" else False
        remove_last = True if rem_l_page.get() == "Yes" else False
        
        # Grab and convert numeric inputs
        slides_count = int(slides_per_page.get())
        dpi_val = int(dpi.get().strip())
        quality_val = int(jpg_quality.get().strip())
        width_mm = float(page_width.get().strip())
        height_mm = float(page_height.get().strip())
        margin = float(margin_mm.get().strip())
        spacing = float(slide_spacing_mm.get().strip())

        # Build the config dictionary
        config = {
            "remove_first_page": remove_first,
            "remove_last_page": remove_last,
            "n_up": slides_count,
            "dpi": dpi_val,
            "jpg_quality": quality_val,
            "output_size": (
                slide_processor.mm_to_point(width_mm), 
                slide_processor.mm_to_point(height_mm)
            ),
            "margin": slide_processor.mm_to_point(margin),
            "slide_spacing": slide_processor.mm_to_point(spacing)
        }

        # Run the core logic and pass the update_progress function
        final_pdf_count, final_page_count = slide_processor.process_directory_tree(
            src, dest, config, progress_callback=update_progress
        )

        # Show Summary Pop-up
        summary_msg = f"Processing Complete!\n\nPDFs Processed: {final_pdf_count}\nTotal Pages Generated: {final_page_count}"
        messagebox.showinfo("Summary", summary_msg)

    except Exception as e:
        messagebox.showerror("Execution Error", f"An error occurred:\n{str(e)}")
    finally:
        # Re-enable the start button and reset progress bar
        start_button.config(state=tk.NORMAL)
        progress_var.set(0)


def run_script():
    """Triggered when user clicks Start. Validates paths, then starts the thread."""
    src = source_folder.get().strip()
    dest = destination_folder.get().strip()

    if not src or not dest:
        messagebox.showwarning("Input Error", "Both Source and Destination folders are required.")
        return
    if not os.path.isdir(src):
        messagebox.showerror("Path Error", "The Source folder path does not exist.")
        return
        
    if not os.path.isdir(dest):
        try: os.makedirs(dest)
        except Exception as e:
            messagebox.showerror("Path Error", f"Could not create Destination folder:\n{e}")
            return

    # Disable button to prevent clicking multiple times
    start_button.config(state=tk.DISABLED)
    progress_var.set(0)
    
    # Start the processing in a background thread
    threading.Thread(target=execute_processing_thread, daemon=True).start()

# Window Setup
root = tk.Tk()
root.title("Printable Notes Generator")
root.geometry("550x620")
root.configure(padx=20, pady=20)
root.columnconfigure(1, weight=1)

# UI Elements
tk.Label(root, text="Source Folder:*").grid(row=0, column=0, sticky="w", pady=5)
source_folder = tk.Entry(root)
source_folder.grid(row=0, column=1, sticky="ew", padx=5)
tk.Button(root, text="Browse", command=browse_source).grid(row=0, column=2)

tk.Label(root, text="Destination Folder:*").grid(row=1, column=0, sticky="w", pady=5)
destination_folder = tk.Entry(root)
destination_folder.grid(row=1, column=1, sticky="ew", padx=5)
tk.Button(root, text="Browse", command=browse_destination).grid(row=1, column=2)

tk.Label(root, text="Remove First Page:").grid(row=2, column=0, sticky="w", pady=5)
rem_f_page = ttk.Combobox(root, values=["Yes", "No"], state="readonly")
rem_f_page.grid(row=2, column=1, sticky="ew", padx=5)
rem_f_page.set("No")

tk.Label(root, text="Remove Last Page:").grid(row=3, column=0, sticky="w", pady=5)
rem_l_page = ttk.Combobox(root, values=["Yes", "No"], state="readonly")
rem_l_page.grid(row=3, column=1, sticky="ew", padx=5)
rem_l_page.set("No")

tk.Label(root, text="Slides Per Page:").grid(row=4, column=0, sticky="w", pady=5)
slides_per_page = ttk.Combobox(root, values=[1,2,3,4,5,6,7,8,9], state="readonly")
slides_per_page.grid(row=4, column=1, sticky="ew", padx=5)
slides_per_page.set(3)

tk.Label(root, text="DPI (Recommended 72):").grid(row=5, column=0, sticky="w", pady=5)
dpi = tk.Entry(root)
dpi.grid(row=5, column=1, sticky="ew", padx=5)
dpi.insert(0, "72")

tk.Label(root, text="JPG Quality (1-100):").grid(row=6, column=0, sticky="w", pady=5)
jpg_quality = tk.Entry(root)
jpg_quality.grid(row=6, column=1, sticky="ew", padx=5)
jpg_quality.insert(0, "75")

tk.Label(root, text="Output Page Size (mm):").grid(row=7, column=0, sticky="w", pady=5)
size_frame = tk.Frame(root)
size_frame.grid(row=7, column=1, sticky="ew", padx=5)
tk.Label(size_frame, text="W:").pack(side=tk.LEFT)
page_width = tk.Entry(size_frame, width=8)
page_width.pack(side=tk.LEFT, padx=(0, 10))
page_width.insert(0, "210")
tk.Label(size_frame, text="H:").pack(side=tk.LEFT)
page_height = tk.Entry(size_frame, width=8)
page_height.pack(side=tk.LEFT)
page_height.insert(0, "297")

tk.Label(root, text="Page Margin (mm):").grid(row=8, column=0, sticky="w", pady=5)
margin_mm = tk.Entry(root)
margin_mm.grid(row=8, column=1, sticky="ew", padx=5)
margin_mm.insert(0, "2")

tk.Label(root, text="Slide Spacing (mm):").grid(row=9, column=0, sticky="w", pady=5)
slide_spacing_mm = tk.Entry(root)
slide_spacing_mm.grid(row=9, column=1, sticky="ew", padx=5)
slide_spacing_mm.insert(0, "2")

# Start Button
start_button = tk.Button(root, text="Start Processing", command=run_script, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
start_button.grid(row=10, column=0, columnspan=3, pady=(20, 10), ipadx=20, ipady=5)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.grid(row=11, column=0, columnspan=3, sticky="ew", pady=(0, 10))

root.mainloop()