"""
Clearing Management Module

This module handles the clearing of all automation functions from the list.
"""

import tkinter as tk
from tkinter import messagebox

def clear_all(self):
    """Clear all functions"""
    if messagebox.askyesno("Konfirmasi", "Hapus semua fungsi?"):
        self.automation_functions.clear()
        self.update_functions_list()
        self.status_label.config(text="Semua fungsi berhasil dihapus!")
