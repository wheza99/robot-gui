"""
Screen capture handlers for the automation GUI
"""
import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import os

def capture_screen_region(self):
    """Capture a region of the screen as template image"""
    self.root.withdraw()  # Hide main window
    
    # Create a fullscreen transparent window for selection
    capture_window = tk.Toplevel()
    capture_window.attributes('-fullscreen', True)
    capture_window.attributes('-alpha', 0.3)
    capture_window.configure(bg='black')
    capture_window.attributes('-topmost', True)
    
    # Variables for selection
    start_x = start_y = end_x = end_y = 0
    selection_rect = None
    
    canvas = tk.Canvas(capture_window, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    def on_mouse_press(event):
        nonlocal start_x, start_y, selection_rect
        start_x, start_y = event.x, event.y
        if selection_rect:
            canvas.delete(selection_rect)
    
    def on_mouse_drag(event):
        nonlocal selection_rect, end_x, end_y
        end_x, end_y = event.x, event.y
        if selection_rect:
            canvas.delete(selection_rect)
        selection_rect = canvas.create_rectangle(
            start_x, start_y, end_x, end_y, 
            outline='red', width=2
        )
    
    def on_mouse_release(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        
        # Capture the selected region
        if abs(end_x - start_x) > 10 and abs(end_y - start_y) > 10:
            # Ensure coordinates are in correct order
            left = min(start_x, end_x)
            top = min(start_y, end_y)
            right = max(start_x, end_x)
            bottom = max(start_y, end_y)
            
            # Take screenshot of the selected region
            screenshot = pyautogui.screenshot(region=(left, top, right-left, bottom-top))
            
            # Save to temp file
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_images')
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = int(time.time())
            temp_path = os.path.join(temp_dir, f'captured_template_{timestamp}.png')
            screenshot.save(temp_path)
            
            # Update UI
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, temp_path)
            self.update_image_preview(temp_path)
            
            capture_window.destroy()
            self.root.deiconify()  # Show main window
        else:
            capture_window.destroy()
            self.root.deiconify()
            messagebox.showwarning("Peringatan", "Area yang dipilih terlalu kecil!")
    
    def on_escape(event):
        capture_window.destroy()
        self.root.deiconify()
    
    canvas.bind('<Button-1>', on_mouse_press)
    canvas.bind('<B1-Motion>', on_mouse_drag)
    canvas.bind('<ButtonRelease-1>', on_mouse_release)
    capture_window.bind('<Escape>', on_escape)
    
    # Instructions
    instruction_label = tk.Label(
        capture_window, 
        text="Drag untuk memilih area gambar template. Tekan ESC untuk membatalkan.",
        fg='white', bg='black', font=('Arial', 12)
    )
    instruction_label.pack(pady=20)
