import os
import math
import pymupdf

def get_grid_layout(n):
    layouts = { 1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2), 6: (3, 2), 8: (4, 2), 9: (3, 3) }
    if n in layouts: return layouts[n]
    cols = math.ceil(math.sqrt(n))
    return math.ceil(n / cols), cols

def process_pdf(input_path, output_path, config):
    try:
        doc = pymupdf.open(input_path)
        num_pages = len(doc)
        
        remove_first = config['remove_first_page']
        remove_last = config['remove_last_page']
        pages_to_remove = int(remove_first) + int(remove_last)
        
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
        
        for i in range(0, len(pages_to_process), n_up):
            chunk = pages_to_process[i:i + n_up]
            out_page = out_pdf.new_page(width=out_w, height=out_h)
            
            for idx, page_index in enumerate(chunk):
                col = idx % cols
                row = idx // cols
                page = doc[page_index]
                
                pix = page.get_pixmap(dpi=config['dpi'], colorspace=pymupdf.csGRAY)
                pix.invert_irect(pix.irect)
                
                w_orig = page.rect.width
                h_orig = page.rect.height
                scale = min((cell_w - spacing) / w_orig, (cell_h - spacing) / h_orig)
                new_w = w_orig * scale
                new_h = h_orig * scale
                
                x_offset = margin + (col * cell_w) + (cell_w - new_w) / 2
                y_offset = margin + (row * cell_h) + (cell_h - new_h) / 2
                target_rect = pymupdf.Rect(x_offset, y_offset, x_offset + new_w, y_offset + new_h)
                
                img_bytes = pix.tobytes("jpeg", jpg_quality=config['jpg_quality']) 
                out_page.insert_image(target_rect, stream=img_bytes)

        final_page_count = len(out_pdf)
        out_pdf.save(output_path, garbage=3, deflate=True)
        out_pdf.close()
        doc.close()
        return True, final_page_count
        
    except Exception as e:
        print(f"Failed to process file {input_path} : {e}")
        return False, 0

def process_directory_tree(input_dir, output_dir, config, progress_callback=None):
    os.makedirs(output_dir, exist_ok=True)
    total_pdfs = sum(1 for root, _, files in os.walk(input_dir) for f in files if f.lower().endswith('.pdf'))
    
    if total_pdfs == 0:
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
                
                # Send progress back to GUI if callback exists
                if progress_callback:
                    progress_callback(processed_count, total_pdfs)

    return total_successful_pdfs, total_output_pages

def mm_to_point(mm):
    return mm * (72.0/25.4)