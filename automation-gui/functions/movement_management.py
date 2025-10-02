"""
Movement Management Module

This module handles the movement and reordering of automation functions in the list.
"""

import tkinter as tk
from tkinter import messagebox

def move_up(self):
    """Move selected function up"""
    selection = self.functions_tree.selection()
    if not selection:
        messagebox.showwarning("Warning", "Pilih fungsi yang akan dipindah!")
        return
    
    item = selection[0]
    index = self.functions_tree.index(item)
    if index > 0:
        self.automation_functions[index], self.automation_functions[index-1] = \
            self.automation_functions[index-1], self.automation_functions[index]
        self.update_functions_list()
        # Reselect the moved item
        new_item = self.functions_tree.get_children()[index-1]
        self.functions_tree.selection_set(new_item)

def move_down(self):
    """Move selected function down"""
    selection = self.functions_tree.selection()
    if not selection:
        messagebox.showwarning("Warning", "Pilih fungsi yang akan dipindah!")
        return
    
    item = selection[0]
    index = self.functions_tree.index(item)
    if index < len(self.automation_functions) - 1:
        self.automation_functions[index], self.automation_functions[index+1] = \
            self.automation_functions[index+1], self.automation_functions[index]
        self.update_functions_list()
        # Reselect the moved item
        new_item = self.functions_tree.get_children()[index+1]
        self.functions_tree.selection_set(new_item)
