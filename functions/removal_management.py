"""
Removal Management Module

This module handles the removal of automation functions from the list.
"""

import tkinter as tk
from tkinter import messagebox

def remove_function(self):
    """Remove selected function"""
    selection = self.functions_tree.selection()
    if not selection:
        messagebox.showwarning("Warning", "Pilih fungsi yang akan dihapus!")
        return
    
    item = selection[0]
    index = self.functions_tree.index(item)
    del self.automation_functions[index]
    self.update_functions_list()
    self.status_label.config(text="Fungsi berhasil dihapus!")
