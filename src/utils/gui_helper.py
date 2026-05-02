import tkinter as tk
from tkinter import ttk
from utils.utils import (
    get_topic_group,
    natural_sort_key,
    get_resource_path
)

class DragDropTreeview(ttk.Treeview):
    """Tkinter Treeview with hierarchical drag-and-drop."""
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind('<ButtonPress-1>', self.on_press)
        self.bind('<B1-Motion>', self.on_drag)
        self.dragged_item = None

    def on_press(self, event):
        self.dragged_item = self.identify_row(event.y)

    def on_drag(self, event):
        if not self.dragged_item:
            return
            
        target_item = self.identify_row(event.y)
        if not target_item or target_item == self.dragged_item:
            return

        # Identify the hierarchy level of both items
        dragged_parent = self.parent(self.dragged_item)
        target_parent = self.parent(target_item)

        # (Root topics can only swap with root topics. Children only with siblings)
        if dragged_parent != target_parent:
            return 

        target_index = self.index(target_item)
        self.move(self.dragged_item, dragged_parent, target_index)


class MergeReviewDialog(tk.Toplevel):
    def __init__(self, parent, folder_name, pdf_list):
        super().__init__(parent)
        self.title(f"Review Merge Order: {folder_name}")
        self.geometry("450x550")
        self.transient(parent)
        self.grab_set() 
        
        try:
            icon_path = get_resource_path("assets/icon.ico")
            self.iconbitmap(icon_path)
        except Exception:
            pass

        self.final_order = None

        lbl = ttk.Label(self, text="Drag topics or individual PDFs to reorder them:", font=("Arial", 10, "bold"))
        lbl.pack(pady=10, padx=10, anchor="w")

        # Initialize the new Treeview
        self.tree = DragDropTreeview(self, show='tree', selectmode='browse', height=20)
        self.tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        sorted_pdfs = sorted(pdf_list, key=natural_sort_key)
        
        # Group by Topic
        grouped_pdfs = {}
        for pdf in sorted_pdfs:
            topic = get_topic_group(pdf)
            if topic not in grouped_pdfs:
                grouped_pdfs[topic] = []
            grouped_pdfs[topic].append(pdf)

        # Populate the Treeview
        for topic, files in grouped_pdfs.items():
            # Insert the Parent "Topic" folder
            parent_id = self.tree.insert("", tk.END, text=topic, open=True)
            
            # Insert the Child PDFs inside it
            for file in files:
                self.tree.insert(parent_id, tk.END, text=file)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        confirm_btn = ttk.Button(btn_frame, text="Confirm Order", command=self.confirm)
        confirm_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def confirm(self):
        self.final_order = []
        # Iterate through the Treeview exactly as it appears visually on screen
        for parent_item in self.tree.get_children():
            for child_item in self.tree.get_children(parent_item):
                pdf_filename = self.tree.item(child_item, 'text')
                self.final_order.append(pdf_filename)
                
        self.destroy()

    def cancel(self):
        self.final_order = None
        self.destroy()