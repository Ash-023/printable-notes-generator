import os
import sys
import math
import pymupdf
import json

def get_grid_layout(n):
    """
    Returns an optimized (rows, columns) grid layout based on the number of slides.
    Standard academic layouts (1, 2, 3, 4, 6, 9) are hardcoded for the best look.
    """
    layouts = {
        1: (1, 1),
        2: (2, 1), # 2 rows, 1 col (stacked vertically)
        3: (3, 1), # 3 rows, 1 col (standard university handout)
        4: (2, 2), # 2x2 grid
        6: (3, 2),
        8: (4, 2),
        9: (3, 3)
    }
    if n in layouts:
        return layouts[n]
    
    # Generic fallback for weird numbers (e.g., 5 or 7)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return rows, cols

def process_pdf(input_path, output_path, config):
    """
    Reads a PDF, applies trimming, N-up grid layout, grayscale, and color inversion.
    Returns: (success_boolean, output_page_count)
    """
    try:
        doc = pymupdf.open(input_path)
        num_pages = len(doc)
        
        # Page Trimming Logic
        remove_first = config['remove_first_page']
        remove_last = config['remove_last_page']
        
        pages_to_remove = int(remove_first) + int(remove_last)
        
        # Safety check
        if num_pages <= pages_to_remove:
            doc.close()
            return False, 0
            
        start_idx = 1 if remove_first else 0
        end_idx = num_pages - 1 if remove_last else num_pages
        
        pages_to_process = list(range(start_idx, end_idx))
            
        out_pdf = pymupdf.open()
        
        n_up = config['n_up']
        margin = config['margin']
        spacing = config['slide_spacing']
        out_w, out_h = config['output_size']
        
        rows, cols = get_grid_layout(n_up)
        
        usable_w = out_w - (2 * margin)
        usable_h = out_h - (2 * margin)
        
        cell_w = usable_w / cols
        cell_h = usable_h / rows
        
        # Process original pages in chunks of 'N'
        for i in range(0, len(pages_to_process), n_up):
            chunk = pages_to_process[i:i + n_up]
            out_page = out_pdf.new_page(width=out_w, height=out_h)
            
            for idx, page_index in enumerate(chunk):
                col = idx % cols
                row = idx // cols
                
                page = doc[page_index]
                
                # Render directly to Grayscale AND invert
                pix = page.get_pixmap(dpi=config['dpi'], colorspace=pymupdf.csGRAY)
                pix.invert_irect(pix.irect)
                
                # Aspect Ratio Scaling
                w_orig = page.rect.width
                h_orig = page.rect.height
                
                scale = min((cell_w - spacing) / w_orig, (cell_h - spacing) / h_orig)
                
                new_w = w_orig * scale
                new_h = h_orig * scale
                
                x_offset = margin + (col * cell_w) + (cell_w - new_w) / 2
                y_offset = margin + (row * cell_h) + (cell_h - new_h) / 2
                
                target_rect = pymupdf.Rect(x_offset, y_offset, x_offset + new_w, y_offset + new_h)
                
                # Stamp compressed jpeg onto layout
                img_bytes = pix.tobytes("jpeg", jpg_quality=config['jpg_quality']) 
                out_page.insert_image(target_rect, stream=img_bytes)

        # Count how many pages were created in the new PDF
        final_page_count = len(out_pdf)

        out_pdf.save(output_path, garbage=3, deflate=True)
        out_pdf.close()
        doc.close()
        
        return True, final_page_count
        
    except Exception as e:
        print(f"Failed to process file {input_path} : {e}")
        return False, 0

def process_directory_tree(input_dir, output_dir, config):
    """Replicates hierarchy, processes PDFs, and manages the progress tracker."""
    os.makedirs(output_dir, exist_ok=True)

    # Count total PDFs to initialize the progress bar
    total_pdfs = sum(1 for root, _, files in os.walk(input_dir) for f in files if f.lower().endswith('.pdf'))
    
    if total_pdfs == 0:
        print(f"No PDFs found in '{input_dir}'.")
        return 0, 0

    processed_count = 0
    total_successful_pdfs = 0
    total_output_pages = 0

    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        target_dir = os.path.join(output_dir, relative_path)
        
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            if file.lower().endswith(".pdf"):
                input_file_path = os.path.join(root, file)
                output_file_path = os.path.join(target_dir, file)
                
                success, out_pages = process_pdf(input_file_path, output_file_path, config)
                
                if success:
                    total_successful_pdfs += 1
                    total_output_pages += out_pages
                
                processed_count += 1
                
                # Progress Bar Logic
                progress = processed_count / total_pdfs
                bar_length = 40
                filled_length = int(bar_length * progress)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                
                sys.stdout.write(f'\rProgress: |{bar}| {processed_count}/{total_pdfs} files ')
                sys.stdout.flush()

    # Move to the next line after the progress bar finishes
    print() 
    
    return total_successful_pdfs, total_output_pages

def mm_to_point(mm):
    return mm * (72.0/25.4)

def load_configuration(json_path="config.json"):
    """Loads the JSON config and maps variables."""
    try:
        with open(json_path, 'r') as f:
            raw_config = json.load(f)
            
        parsed_config = {
            "source_folder": raw_config.get("source_folder", "notes"),
            "destination_folder": raw_config.get("destination_folder", "notes_inverted"),
            
            "remove_first_page": raw_config.get("remove_first_page", True),
            "remove_last_page": raw_config.get("remove_last_page", False),
            
            "n_up": raw_config.get("slides_per_page", 3),
            "dpi": raw_config.get("dpi", 150),
            "jpg_quality": raw_config.get("jpg_quality", 75),
            
            "output_size": (
                mm_to_point(raw_config["output_size_mm"][0]), 
                mm_to_point(raw_config["output_size_mm"][1])
            ),
            "margin": mm_to_point(raw_config["margin_mm"]),
            "slide_spacing": mm_to_point(raw_config["slide_spacing_mm"])
        }
        return parsed_config
        
    except FileNotFoundError:
        print(f"Error: Could not find '{json_path}'. Please ensure it is in the same directory.")
        return None
    except KeyError as e:
        print(f"Error: Missing key in config.json: {e}")
        return None

if __name__ == "__main__":
    CONFIG = load_configuration("config/config.json")
    
    if CONFIG:
        source = CONFIG["source_folder"]
        destination = CONFIG["destination_folder"]
        
        if not os.path.exists(source):
            print(f"Error: The source folder '{source}' does not exist.")
        else:
            print(f"Starting batch conversion from '{source}' to '{destination}'...")
            
            # Run the process and catch the returned totals
            final_pdf_count, final_page_count = process_directory_tree(source, destination, CONFIG)
            
            # Output final summary
            print("\n--- Summary ---")
            print(f"Total PDFs successfully generated: {final_pdf_count}")
            print(f"Total combined pages generated: {final_page_count}")
            print("All done!")

    else:
        print("Failed to Load Config.")