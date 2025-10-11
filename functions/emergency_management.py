"""
Emergency Management Module

This module handles all emergency stop functionality including hotkey setup,
emergency stop triggering, UI updates, and cleanup operations.
"""

import tkinter as tk
from tkinter import messagebox
from pynput import keyboard


def setup_emergency_stop(self):
    """Setup global hotkey listener for emergency stop (Ctrl+Alt+Q)"""
    def on_hotkey():
        self.trigger_emergency_stop()
    
    try:
        # Setup global hotkey listener for Ctrl+Alt+Q
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+q': on_hotkey
        })
        self.hotkey_listener.start()
    except Exception as e:
        print(f"Warning: Could not setup emergency hotkey: {e}")


def trigger_emergency_stop(self):
    """Trigger emergency stop for automation"""
    self.emergency_stop = True
    self.is_running = False
    
    # Update UI in main thread
    self.root.after(0, self._update_emergency_stop_ui)
    
    print("🚨 EMERGENCY STOP ACTIVATED! (Ctrl+Alt+Q pressed)")


def _update_emergency_stop_ui(self):
    """Update UI after emergency stop (must run in main thread)"""
    self.start_btn.config(state=tk.NORMAL)
    self.stop_btn.config(state=tk.DISABLED)
    self.status_label.config(text="🚨 EMERGENCY STOP! Automation dihentikan paksa!")
    self.progress['value'] = 0
    
    # Show emergency stop message
    messagebox.showwarning("Emergency Stop", 
                         "Automation dihentikan dengan emergency stop!\n\n"
                         "Hotkey: Ctrl+Alt+Q\n"
                         "PyAutoGUI Failsafe: Gerakkan mouse ke pojok kiri atas")


def reset_emergency_stop(self):
    """Reset emergency stop flag"""
    self.emergency_stop = False
    if hasattr(self, 'status_label'):
        self.status_label.config(text="Status: Siap")


def cleanup_emergency_stop(self):
    """Cleanup emergency stop listener when closing application"""
    if self.hotkey_listener:
        try:
            self.hotkey_listener.stop()
        except:
            pass
