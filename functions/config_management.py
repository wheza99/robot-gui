"""
Configuration Management Module

This module handles saving and loading automation configurations.
"""

import json
from tkinter import messagebox


def save_config(self):
    """Save automation configuration to file"""
    if not self.automation_functions:
        messagebox.showwarning("Warning", "Tidak ada fungsi untuk disimpan!")
        return
    
    try:
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.automation_functions, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Berhasil", f"Konfigurasi disimpan ke {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan: {str(e)}")


def load_config(self):
    """Load automation configuration from file"""
    try:
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_functions = json.load(f)
            
            # Ensure backward compatibility and data type consistency
            for func in loaded_functions:
                if 'enabled' not in func:
                    func['enabled'] = True
                
                # Convert delay to float to ensure consistent data type
                if 'delay' in func:
                    try:
                        func['delay'] = float(func['delay'])
                    except (ValueError, TypeError):
                        func['delay'] = 1.0  # Default delay if conversion fails
                else:
                    func['delay'] = 1.0  # Default delay if missing
            
            self.automation_functions = loaded_functions
            self.update_functions_list()
            messagebox.showinfo("Berhasil", f"Konfigurasi dimuat dari {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat: {str(e)}")
