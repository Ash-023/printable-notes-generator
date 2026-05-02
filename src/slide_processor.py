import os
import math
import pymupdf
from utils.utils import (
    natural_sort_key,
    
)

def get_grid_layout(n):
    layouts = { 1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2), 6: (3, 2), 8: (4, 2), 9: (3, 3) }
    if n in layouts: return layouts[n]
    cols = math.ceil(math.sqrt(n))
    return math.ceil(n / cols), cols

def create_processed_doc(input_path, config):
    """
    Core engine: Processes a single PDF and returns the modified document in memory.
    Returns: (success_boolean, processed_doc_object, final_page_count)
    """
    try:
        doc = pymupdf.open(input_path)
        num_pages = len(doc)
        
        remove_first = config.get('remove_first_page', False)
        remove_last = config.get('remove_last_page', False)
        pages_to_remove = int(remove_first) + int(remove_last)
        
        if num_pages <= pages_to_remove:
            doc.close()
            return False, None, 0
            
        start_idx = 1 if remove_first else 0
        end_idx = num_pages - 1 if remove_last else num_pages
        pages_to_process = list(range(start_idx, end_idx))
            
        out_pdf = pymupdf.open()
        n_up = config['n_up']
        margin = config['margin']
        spacing = config['slide_spacing']
        
        base_w, base_h = config['output_size']
        
        port_w, port_h = min(base_w, base_h), max(base_w, base_h)
        land_w, land_h = port_h, port_w
        
        rows, cols = get_grid_layout(n_up)
        
        # Get the aspect ratio of the first slide to run our tests
        test_page = doc[pages_to_process[0]]
        w_orig = test_page.rect.width
        h_orig = test_page.rect.height
        
        # Test Portrait Scale
        cell_w_p = (port_w - (2 * margin)) / cols
        cell_h_p = (port_h - (2 * margin)) / rows
        scale_p = min((cell_w_p - spacing) / w_orig, (cell_h_p - spacing) / h_orig)
        
        # Test Landscape Scale
        cell_w_l = (land_w - (2 * margin)) / cols
        cell_h_l = (land_h - (2 * margin)) / rows
        scale_l = min((cell_w_l - spacing) / w_orig, (cell_h_l - spacing) / h_orig)
        
        # Lock in the winning dimensions for the rest of the script
        if scale_l > scale_p:
            out_w, out_h = land_w, land_h
            cell_w, cell_h = cell_w_l, cell_h_l
        else:
            out_w, out_h = port_w, port_h
            cell_w, cell_h = cell_w_p, cell_h_p
        
        for i in range(0, len(pages_to_process), n_up):
            chunk = pages_to_process[i:i + n_up]
            out_page = out_pdf.new_page(width=out_w, height=out_h)
            
            for idx, page_index in enumerate(chunk):
                col = idx % cols
                row = idx // cols
                page = doc[page_index]
                
                pix = page.get_pixmap(dpi=config['dpi'], colorspace=pymupdf.csGRAY)
                pix.invert_irect(pix.irect)
                
                # Fetch fresh original dimensions per slide (in case slide sizes vary)
                w_orig_current = page.rect.width
                h_orig_current = page.rect.height
                
                scale = min((cell_w - spacing) / w_orig_current, (cell_h - spacing) / h_orig_current)
                new_w = w_orig_current * scale
                new_h = h_orig_current * scale
                
                x_offset = margin + (col * cell_w) + (cell_w - new_w) / 2
                y_offset = margin + (row * cell_h) + (cell_h - new_h) / 2
                target_rect = pymupdf.Rect(x_offset, y_offset, x_offset + new_w, y_offset + new_h)
                
                img_bytes = pix.tobytes("jpeg", jpg_quality=config['jpg_quality']) 
                out_page.insert_image(target_rect, stream=img_bytes)

        final_page_count = len(out_pdf)
        doc.close()
        return True, out_pdf, final_page_count
        
    except Exception as e:
        print(f"Failed to process file {input_path} : {e}")
        return False, None, 0

def process_directory_tree(input_dir, output_dir, config, explicit_orders=None, progress_callback=None):
    if explicit_orders is None:
        explicit_orders = {}
    
    os.makedirs(output_dir, exist_ok=True)
    total_pdfs = sum(1 for root, _, files in os.walk(input_dir) for f in files if f.lower().endswith('.pdf'))
    
    if total_pdfs == 0:
        return 0, 0

    processed_count = 0
    total_successful_pdfs = 0
    total_output_pages = 0
    is_merging = config.get("merge_pdfs", False)

    for root, dirs, files in os.walk(input_dir):
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        if not pdf_files:
            continue

        relative_path = os.path.relpath(root, input_dir)
        target_dir = os.path.join(output_dir, relative_path)
        os.makedirs(target_dir, exist_ok=True)

        # Apply sorting (User's drag-and-drop order OR Natural alphabetical order)
        if is_merging and root in explicit_orders:
            ordered_files = explicit_orders[root]
        else:
            ordered_files = sorted(pdf_files, key=natural_sort_key)

        # Processing logic based on mode
        if is_merging:
            merged_doc = pymupdf.open()
            
            # Name the merged file after the folder (or "Merged_Root" if base folder)
            folder_name = os.path.basename(root)
            if not folder_name:  
                folder_name = "Merged_Root"
            merged_out_path = os.path.join(target_dir, f"{folder_name}.pdf")
            
            folder_success = False

            for file in ordered_files:
                input_file_path = os.path.join(root, file)
                success, processed_doc, out_pages = create_processed_doc(input_file_path, config)
                
                if success:
                    merged_doc.insert_pdf(processed_doc)
                    processed_doc.close()
                    total_output_pages += out_pages
                    folder_success = True
                
                processed_count += 1
                if progress_callback:
                    progress_callback(processed_count, total_pdfs)
            
            # Save the final compiled document to the hard drive
            if folder_success:
                merged_doc.save(merged_out_path, garbage=3, deflate=True)
                total_successful_pdfs += 1  # Counts as 1 combined file
            merged_doc.close()

        else:
            for file in ordered_files:
                input_file_path = os.path.join(root, file)
                output_file_path = os.path.join(target_dir, file)
                
                success, processed_doc, out_pages = create_processed_doc(input_file_path, config)
                
                if success:
                    processed_doc.save(output_file_path, garbage=3, deflate=True)
                    processed_doc.close() # Free memory!
                    total_successful_pdfs += 1
                    total_output_pages += out_pages
                
                processed_count += 1
                if progress_callback:
                    progress_callback(processed_count, total_pdfs)

    return total_successful_pdfs, total_output_pages