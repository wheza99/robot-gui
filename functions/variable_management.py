"""
Variable Management Module

This module handles the Variable Manager window and all variable-related operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox


def show_variable_manager(self):
    """Show Variable Manager window"""
    var_window = tk.Toplevel(self.root)
    var_window.title("Variable Manager")
    var_window.geometry("600x400")
    var_window.resizable(True, True)
    var_window.grab_set()  # Make dialog modal
    
    # Center the window
    var_window.transient(self.root)
    
    # Main frame
    main_frame = ttk.Frame(var_window, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    ttk.Label(main_frame, text="Variable Manager", font=("Arial", 14, "bold")).pack(pady=(0, 10))
    
    # Variables list frame
    list_frame = ttk.LabelFrame(main_frame, text="Current Variables", padding="10")
    list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # Treeview for variables
    columns = ("Name", "Value", "Type")
    var_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
    
    # Configure columns
    var_tree.heading("Name", text="Variable Name")
    var_tree.heading("Value", text="Value")
    var_tree.heading("Type", text="Type")
    
    var_tree.column("Name", width=150)
    var_tree.column("Value", width=250)
    var_tree.column("Type", width=100)
    
    # Scrollbar for treeview
    var_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=var_tree.yview)
    var_tree.configure(yscrollcommand=var_scrollbar.set)
    
    var_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    var_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Update variables list
    def update_var_list():
        # Clear existing items
        for item in var_tree.get_children():
            var_tree.delete(item)
        
        # Add current variables
        for var_name, var_value in self.variables.items():
            value_str = str(var_value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            
            var_type = type(var_value).__name__
            var_tree.insert("", tk.END, values=(var_name, value_str, var_type))
    
    # Control buttons frame
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Add variable button
    def add_variable():
        add_var_window = tk.Toplevel(var_window)
        add_var_window.title("Add Variable")
        add_var_window.geometry("400x200")
        add_var_window.resizable(False, False)
        add_var_window.grab_set()
        add_var_window.transient(var_window)
        
        # Add variable form
        form_frame = ttk.Frame(add_var_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Variable Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(form_frame, text="Variable Value:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        value_entry = ttk.Entry(form_frame, width=30)
        value_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        form_frame.columnconfigure(1, weight=1)
        
        def save_variable():
            name = name_entry.get().strip()
            value = value_entry.get()
            
            if not name:
                messagebox.showwarning("Warning", "Masukkan nama variabel!")
                return
            
            self.variables[name] = value
            update_var_list()
            add_var_window.destroy()
        
        btn_frame_add = ttk.Frame(form_frame)
        btn_frame_add.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(btn_frame_add, text="Save", command=save_variable).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame_add, text="Cancel", command=add_var_window.destroy).pack(side=tk.LEFT)
    
    # Delete variable button
    def delete_variable():
        selection = var_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Pilih variabel yang akan dihapus!")
            return
        
        item = selection[0]
        var_name = var_tree.item(item)["values"][0]
        
        if messagebox.askyesno("Confirm", f"Hapus variabel '{var_name}'?"):
            if var_name in self.variables:
                del self.variables[var_name]
                update_var_list()
    
    # Clear all variables button
    def clear_all_variables():
        if messagebox.askyesno("Confirm", "Hapus semua variabel?"):
            self.variables.clear()
            update_var_list()
    
    ttk.Button(btn_frame, text="Add Variable", command=add_variable).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_frame, text="Delete Selected", command=delete_variable).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_frame, text="Clear All", command=clear_all_variables).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(btn_frame, text="Refresh", command=update_var_list).pack(side=tk.LEFT)
    
    # Info frame
    info_frame = ttk.LabelFrame(main_frame, text="Usage Information", padding="10")
    info_frame.pack(fill=tk.X)
    
    info_text = """Cara menggunakan variabel:
1. Gunakan format ${variable_name} dalam teks untuk mengganti dengan nilai variabel
2. Contoh: "Hello ${username}, today is ${date}"
3. Variabel dapat diset menggunakan fungsi "Set Variable"
4. Variabel dapat diambil menggunakan fungsi "Get Variable" (disalin ke clipboard)"""
    
    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
    
    # Initial update
    update_var_list()
