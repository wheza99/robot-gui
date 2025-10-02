"""
Image handling functions for the automation GUI
"""
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import pyautogui
import time
import os

def browse_image_file(self):
    """Browse for image file"""
    file_path = filedialog.askopenfilename(
        title="Pilih gambar template",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("All files", "*.*")
        ]
    )
    if file_path:
        self.image_path_entry.delete(0, tk.END)
        self.image_path_entry.insert(0, file_path)
        self.update_image_preview(file_path)

def update_image_preview(self, image_path):
    """Update image preview"""
    try:
        # Load and resize image for preview
        pil_image = Image.open(image_path)
        
        # Calculate size to fit in preview (max 150x150)
        max_size = 150
        pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Update preview label
        self.image_preview.config(image=photo)
        self.image_preview.image = photo  # Keep a reference
        
    except Exception as e:
        self.image_preview.config(image='', text=f"Error: {str(e)}")

def wait_for_image(self, template_path, threshold=0.8, timeout=30):
    """Wait for image to appear on screen using template matching"""
    if not os.path.exists(template_path):
        return False, "Template image file not found"
    
    try:
        # Load template image
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            return False, "Could not load template image"
        
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_h, template_w = template_gray.shape
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.emergency_stop or not self.is_running:
                return False, "Stopped by user"
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Image found
                center_x = max_loc[0] + template_w // 2
                center_y = max_loc[1] + template_h // 2
                return True, f"Image found at ({center_x}, {center_y}) with confidence {max_val:.2f}"
            
            time.sleep(0.5)  # Check every 500ms
        
        return False, f"Image not found within {timeout} seconds"
        
    except Exception as e:
        return False, f"Error during image matching: {str(e)}"
