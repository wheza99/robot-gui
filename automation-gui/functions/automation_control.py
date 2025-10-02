"""
Automation Control Module

This module handles the starting and control of the automation process.
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

def start_automation(self):
    """Start the automation process"""
    if not self.automation_functions:
        messagebox.showwarning("Warning", "Tambahkan minimal satu fungsi automation!")
        return
    
    # Reset emergency stop flag before starting
    self.reset_emergency_stop()
    
    self.is_running = True
    self.start_btn.config(state=tk.DISABLED)
    self.stop_btn.config(state=tk.NORMAL)
    
    # Show countdown before starting
    self.status_label.config(text="Automation akan dimulai dalam 3 detik...")
    self.root.update()
    time.sleep(1)
    
    if not self.is_running:  # Check if stopped during countdown
        return
        
    self.status_label.config(text="Automation akan dimulai dalam 2 detik...")
    self.root.update()
    time.sleep(1)
    
    if not self.is_running:  # Check if stopped during countdown
        return
        
    self.status_label.config(text="Automation akan dimulai dalam 1 detik...")
    self.root.update()
    time.sleep(1)
    
    if not self.is_running:  # Check if stopped during countdown
        return
    
    # Start automation in separate thread
    self.current_thread = threading.Thread(target=self.run_automation, daemon=True)
    self.current_thread.start()

def stop_automation(self):
    """Stop the automation process"""
    self.is_running = False
    self.start_btn.config(state=tk.NORMAL)
    self.stop_btn.config(state=tk.DISABLED)
    self.status_label.config(text="Automation dihentikan!")
    self.progress['value'] = 0
