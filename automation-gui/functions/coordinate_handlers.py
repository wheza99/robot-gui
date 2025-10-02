"""
Coordinate capture handlers for the automation GUI
"""
import tkinter as tk
import pyautogui
import time
import threading

def capture_coordinates(self):
    """Capture mouse coordinates after 3 seconds"""
    def capture():
        for i in range(3, 0, -1):
            self.status_label.config(text=f"Capture koordinat dalam {i} detik...")
            self.root.update()
            time.sleep(1)
        
        pos = pyautogui.position()
        self.coord_x.delete(0, tk.END)
        self.coord_x.insert(0, str(pos.x))
        self.coord_y.delete(0, tk.END)
        self.coord_y.insert(0, str(pos.y))
        self.status_label.config(text=f"Koordinat captured: ({pos.x}, {pos.y})")
    
    threading.Thread(target=capture, daemon=True).start()

def capture_drag_coordinates(self):
    """Capture mouse coordinates for drag destination after 3 seconds"""
    def capture():
        for i in range(3, 0, -1):
            self.status_label.config(text=f"Capture koordinat drag dalam {i} detik...")
            self.root.update()
            time.sleep(1)
        
        pos = pyautogui.position()
        self.drag_x.delete(0, tk.END)
        self.drag_x.insert(0, str(pos.x))
        self.drag_y.delete(0, tk.END)
        self.drag_y.insert(0, str(pos.y))
        self.status_label.config(text=f"Koordinat drag captured: ({pos.x}, {pos.y})")
    
    threading.Thread(target=capture, daemon=True).start()
