import os
import sys
import re

def get_topic_group(filename):
    """Extracts the topic prefix from a filename (everything before the first digit)."""
    match = re.match(r"([^\d]+)", filename)
    if match:
        prefix = match.group(1).strip()
        prefix = re.sub(r'[-_]+$', '', prefix).strip()
        return prefix if prefix else "Ungrouped"
    return "Ungrouped"

def natural_sort_key(filename):
    """Sorts strings containing numbers naturally."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def mm_to_point(mm):
    return mm * (72.0/25.4)