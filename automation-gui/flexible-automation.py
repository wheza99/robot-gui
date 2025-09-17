import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import threading
import json

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flexible Automation GUI")
        self.root.geometry("800x600")
        
        # List untuk menyimpan semua fungsi automation
        self.automation_functions = []
        self.is_running = False
        self.current_thread = None
        
        # Disable pyautogui failsafe untuk mencegah error
        pyautogui.FAILSAFE = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Flexible Automation System", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Add Function Section
        add_frame = ttk.LabelFrame(main_frame, text="Tambah Fungsi Automation", padding="10")
        add_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        add_frame.columnconfigure(1, weight=1)
        
        # Function Name Field
        ttk.Label(add_frame, text="Nama Fungsi:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.function_name = ttk.Entry(add_frame, width=25)
        self.function_name.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Function Type Selection
        ttk.Label(add_frame, text="Pilih Fungsi:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.function_type = ttk.Combobox(add_frame, values=[
            "Click", "Type Text", "Delay", "Hotkey", "Scroll", "Drag", "Double Click", "Right Click"
        ], state="readonly", width=15)
        self.function_type.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        self.function_type.bind("<<ComboboxSelected>>", self.on_function_type_change)
        add_frame.columnconfigure(1, weight=1)
        add_frame.columnconfigure(3, weight=1)
        
        # Coordinate Section
        self.coord_frame = ttk.Frame(add_frame)
        self.coord_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.coord_frame.columnconfigure(1, weight=1)
        self.coord_frame.columnconfigure(3, weight=1)
        
        ttk.Label(self.coord_frame, text="Koordinat:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Label(self.coord_frame, text="X:").grid(row=0, column=1, sticky=tk.W, padx=(10, 5))
        self.coord_x = ttk.Entry(self.coord_frame, width=8)
        self.coord_x.grid(row=0, column=2, padx=(0, 10))
        
        ttk.Label(self.coord_frame, text="Y:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.coord_y = ttk.Entry(self.coord_frame, width=8)
        self.coord_y.grid(row=0, column=4, padx=(0, 10))
        
        self.capture_btn = ttk.Button(self.coord_frame, text="Capture Mouse", command=self.capture_coordinates)
        self.capture_btn.grid(row=0, column=5, padx=(10, 0))
        
        # Hide coordinate section initially
        self.coord_frame.grid_remove()
        
        # Parameters Section
        param_frame = ttk.Frame(add_frame)
        param_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        param_frame.columnconfigure(1, weight=1)
        param_frame.columnconfigure(3, weight=1)
        
        # Text parameter (for Type Text function)
        self.text_label = ttk.Label(param_frame, text="Text:")
        self.text_entry = ttk.Entry(param_frame, width=30)
        
        # Hotkey parameter (for Hotkey function)
        self.hotkey_label = ttk.Label(param_frame, text="Hotkey:")
        self.hotkey_entry = ttk.Entry(param_frame, width=20)
        
        # Scroll parameter
        self.scroll_label = ttk.Label(param_frame, text="Scroll:")
        self.scroll_direction = ttk.Combobox(param_frame, values=["Up", "Down"], state="readonly", width=10)
        self.scroll_amount_label = ttk.Label(param_frame, text="Amount:")
        self.scroll_amount = ttk.Entry(param_frame, width=8)
        self.scroll_amount.insert(0, "3")
        
        # Drag parameters
        self.drag_label = ttk.Label(param_frame, text="Drag to:")
        self.drag_x_label = ttk.Label(param_frame, text="X:")
        self.drag_x = ttk.Entry(param_frame, width=8)
        self.drag_y_label = ttk.Label(param_frame, text="Y:")
        self.drag_y = ttk.Entry(param_frame, width=8)
        self.drag_capture_btn = ttk.Button(param_frame, text="Capture Mouse", command=self.capture_drag_coordinates)
        
        # Store param_frame reference for later use
        self.param_frame = param_frame
        
        # Hide parameter section initially
        self.param_frame.grid_remove()
        
        # Delay parameter
        delay_frame = ttk.Frame(add_frame)
        delay_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(delay_frame, text="Delay setelah (detik):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.delay_entry = ttk.Entry(delay_frame, width=8)
        self.delay_entry.grid(row=0, column=1, padx=(0, 20))
        self.delay_entry.insert(0, "1.0")
        
        # Add button
        self.add_btn = ttk.Button(delay_frame, text="Tambah Fungsi", command=self.add_function)
        self.add_btn.grid(row=0, column=2, padx=(20, 0))
        
        # Store delay_frame reference for later use
        self.delay_frame = delay_frame
        
        # Hide delay section initially
        self.delay_frame.grid_remove()
        
        # Functions List Section
        list_frame = ttk.LabelFrame(main_frame, text="Daftar Fungsi Automation", padding="10")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for functions list
        columns = ("Enabled", "No", "Nama", "Fungsi", "Koordinat", "Parameter", "Delay")
        self.functions_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.functions_tree.heading("Enabled", text="Run")
        self.functions_tree.heading("No", text="No")
        self.functions_tree.heading("Nama", text="Nama Fungsi")
        self.functions_tree.heading("Fungsi", text="Jenis")
        self.functions_tree.heading("Koordinat", text="Koordinat")
        self.functions_tree.heading("Parameter", text="Parameter")
        self.functions_tree.heading("Delay", text="Delay (s)")
        
        self.functions_tree.column("Enabled", width=40, anchor=tk.CENTER)
        self.functions_tree.column("No", width=40, anchor=tk.CENTER)
        self.functions_tree.column("Nama", width=150, anchor=tk.W)
        self.functions_tree.column("Fungsi", width=80, anchor=tk.CENTER)
        self.functions_tree.column("Koordinat", width=80, anchor=tk.CENTER)
        self.functions_tree.column("Parameter", width=150, anchor=tk.W)
        self.functions_tree.column("Delay", width=60, anchor=tk.CENTER)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.functions_tree.yview)
        self.functions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.functions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind click event to toggle enabled status
        self.functions_tree.bind("<Button-1>", self.on_treeview_click)
        
        # Function management buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Edit", command=self.edit_function).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Hapus Fungsi", command=self.remove_function).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Pindah Atas", command=self.move_up).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Pindah Bawah", command=self.move_down).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        
        # Control Section
        control_frame = ttk.LabelFrame(main_frame, text="Kontrol Automation", padding="10")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Status and progress
        self.status_label = ttk.Label(control_frame, text="Status: Siap")
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.progress = ttk.Progressbar(control_frame, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Control buttons
        btn_control_frame = ttk.Frame(control_frame)
        btn_control_frame.grid(row=2, column=0, columnspan=3)
        
        self.start_btn = ttk.Button(btn_control_frame, text="Mulai Automation", command=self.start_automation)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(btn_control_frame, text="Stop", command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_control_frame, text="Save Config", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_control_frame, text="Load Config", command=self.load_config).pack(side=tk.LEFT)
        
        # Initially hide parameter widgets
        self.hide_all_parameters()
    
    def on_treeview_click(self, event):
        """Handle treeview click to toggle enabled status"""
        region = self.functions_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.functions_tree.identify_column(event.x)
            if column == "#1":  # First column (Enabled)
                item = self.functions_tree.identify_row(event.y)
                if item:
                    # Get the index of the clicked item
                    item_index = self.functions_tree.index(item)
                    if 0 <= item_index < len(self.automation_functions):
                        # Toggle enabled status
                        self.automation_functions[item_index]['enabled'] = not self.automation_functions[item_index].get('enabled', True)
                        # Update the display
                        self.update_functions_list()
    
    def on_function_type_change(self, event=None):
        """Handle function type selection change"""
        self.hide_all_parameters()
        func_type = self.function_type.get()
        
        # Show sections when function type is selected
        if func_type:
            # Show parameter section
            self.param_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
            
            # Show delay section
            self.delay_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Show/hide coordinate section based on function type
        if func_type in ["Type Text", "Hotkey", "Delay"]:
            # Hide coordinate section for functions that don't need coordinates
            self.coord_frame.grid_remove()
        elif func_type:
            # Show coordinate section for functions that need coordinates
            self.coord_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        if func_type == "Type Text":
            self.text_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.text_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        elif func_type == "Hotkey":
            self.hotkey_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.hotkey_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        elif func_type == "Scroll":
            self.scroll_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.scroll_direction.grid(row=0, column=1, padx=(0, 10))
            self.scroll_amount_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
            self.scroll_amount.grid(row=0, column=3, padx=(0, 10))
        elif func_type == "Drag":
            self.drag_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.drag_x_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 5))
            self.drag_x.grid(row=0, column=2, padx=(0, 10))
            self.drag_y_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 5))
            self.drag_y.grid(row=0, column=4, padx=(0, 10))
            self.drag_capture_btn.grid(row=0, column=5, padx=(10, 0))
    
    def hide_all_parameters(self):
        """Hide all parameter widgets"""
        widgets_to_hide = [
            self.text_label, self.text_entry,
            self.hotkey_label, self.hotkey_entry,
            self.scroll_label, self.scroll_direction, self.scroll_amount_label, self.scroll_amount,
            self.drag_label, self.drag_x_label, self.drag_x, self.drag_y_label, self.drag_y, self.drag_capture_btn
        ]
        for widget in widgets_to_hide:
            widget.grid_remove()
    
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
    
    def add_function(self):
        """Add a new automation function"""
        func_type = self.function_type.get()
        func_name = self.function_name.get().strip()
        
        if not func_type:
            messagebox.showwarning("Warning", "Pilih jenis fungsi terlebih dahulu!")
            return
            
        if not func_name:
            messagebox.showwarning("Warning", "Masukkan nama fungsi!")
            return
        
        try:
            # Get coordinates
            x = int(self.coord_x.get()) if self.coord_x.get() else 0
            y = int(self.coord_y.get()) if self.coord_y.get() else 0
            delay = float(self.delay_entry.get()) if self.delay_entry.get() else 1.0
            
            # Get parameters based on function type
            parameter = ""
            if func_type == "Type Text":
                parameter = self.text_entry.get()
                if not parameter:
                    messagebox.showwarning("Warning", "Masukkan text yang akan diketik!")
                    return
            elif func_type == "Hotkey":
                parameter = self.hotkey_entry.get()
                if not parameter:
                    messagebox.showwarning("Warning", "Masukkan hotkey (contoh: ctrl+c)!")
                    return
            elif func_type == "Scroll":
                direction = self.scroll_direction.get()
                amount = self.scroll_amount.get()
                if not direction:
                    messagebox.showwarning("Warning", "Pilih arah scroll!")
                    return
                parameter = f"{direction} {amount}"
            elif func_type == "Drag":
                drag_x = int(self.drag_x.get()) if self.drag_x.get() else 0
                drag_y = int(self.drag_y.get()) if self.drag_y.get() else 0
                parameter = f"to ({drag_x}, {drag_y})"
            
            # Create function object
            function = {
                "name": func_name,
                "type": func_type,
                "x": x,
                "y": y,
                "parameter": parameter,
                "delay": delay,
                "enabled": True  # Default to enabled
            }
            
            self.automation_functions.append(function)
            self.update_functions_list()
            self.clear_inputs()
            
            # Hide all sections after adding function
            self.coord_frame.grid_remove()
            self.param_frame.grid_remove()
            self.delay_frame.grid_remove()
            
            self.status_label.config(text=f"Fungsi {func_type} berhasil ditambahkan!")
            
        except ValueError:
            messagebox.showerror("Error", "Koordinat dan delay harus berupa angka!")
    
    def clear_inputs(self):
        """Clear all input fields"""
        self.function_type.set("")
        self.function_name.delete(0, tk.END)
        self.coord_x.delete(0, tk.END)
        self.coord_y.delete(0, tk.END)
        self.text_entry.delete(0, tk.END)
        self.hotkey_entry.delete(0, tk.END)
        self.scroll_direction.set("")
        self.scroll_amount.delete(0, tk.END)
        self.scroll_amount.insert(0, "3")
        self.drag_x.delete(0, tk.END)
        self.drag_y.delete(0, tk.END)
        self.delay_entry.delete(0, tk.END)
        self.delay_entry.insert(0, "1.0")
        self.hide_all_parameters()
    
    def update_functions_list(self):
        """Update the functions list display"""
        # Clear existing items
        for item in self.functions_tree.get_children():
            self.functions_tree.delete(item)
        
        # Update functions list display
        for i, func in enumerate(self.automation_functions, 1):
            coord_text = "N/A"
            if func['type'] not in ["Type Text", "Hotkey", "Delay"]:
                coord_text = f"({func['x']}, {func['y']})" if func['x'] or func['y'] else "N/A"
            
            # Get enabled status with default True for backward compatibility
            enabled_text = "✓" if func.get('enabled', True) else "X"
            
            self.functions_tree.insert("", tk.END, values=(
                enabled_text, i, func.get('name', 'Unnamed'), func['type'], coord_text, func['parameter'], func['delay']
            ))
    
    def edit_function(self):
        """Edit selected function"""
        selection = self.functions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Pilih fungsi yang akan diedit!")
            return
        
        # Get selected function index
        item = selection[0]
        func_index = self.functions_tree.index(item)
        func_data = self.automation_functions[func_index]
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Fungsi")
        edit_window.geometry("500x400")
        edit_window.resizable(False, False)
        edit_window.grab_set()  # Make dialog modal
        
        # Center the window
        edit_window.transient(self.root)
        
        # Function name
        ttk.Label(edit_window, text="Nama Fungsi:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=func_data.get("name", ""))
        name_entry = ttk.Entry(edit_window, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Function type
        ttk.Label(edit_window, text="Jenis Fungsi:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        type_var = tk.StringVar(value=func_data["type"])
        type_combo = ttk.Combobox(edit_window, textvariable=type_var, values=[
            "Click", "Type Text", "Delay", "Hotkey", "Scroll", "Drag", "Double Click", "Right Click"
        ], state="readonly", width=27)
        type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Coordinates frame
        coord_frame = ttk.LabelFrame(edit_window, text="Koordinat")
        coord_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(coord_frame, text="X:").grid(row=0, column=0, padx=5, pady=5)
        x_var = tk.StringVar(value=str(func_data["x"]) if func_data["x"] is not None else "")
        x_entry = ttk.Entry(coord_frame, textvariable=x_var, width=10)
        x_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="Y:").grid(row=0, column=2, padx=5, pady=5)
        y_var = tk.StringVar(value=str(func_data["y"]) if func_data["y"] is not None else "")
        y_entry = ttk.Entry(coord_frame, textvariable=y_var, width=10)
        y_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Capture Mouse button for coordinates
        def capture_edit_coordinates():
            """Capture mouse coordinates for edit dialog"""
            def capture():
                for i in range(3, 0, -1):
                    status_label.config(text=f"Capture koordinat dalam {i} detik...")
                    edit_window.update()
                    time.sleep(1)
                
                pos = pyautogui.position()
                x_var.set(str(pos.x))
                y_var.set(str(pos.y))
                status_label.config(text=f"Koordinat captured: ({pos.x}, {pos.y})")
            
            threading.Thread(target=capture, daemon=True).start()
        
        capture_coord_btn = ttk.Button(coord_frame, text="Capture Mouse", command=capture_edit_coordinates)
        capture_coord_btn.grid(row=0, column=4, padx=(10, 5), pady=5)
        
        # Parameter frame
        param_frame = ttk.LabelFrame(edit_window, text="Parameter")
        param_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Create specific parameter fields for each function type
        # Text parameter
        text_label = ttk.Label(param_frame, text="Text:")
        text_var = tk.StringVar()
        text_entry = ttk.Entry(param_frame, textvariable=text_var, width=40)
        
        # Hotkey parameter
        hotkey_label = ttk.Label(param_frame, text="Hotkey:")
        hotkey_var = tk.StringVar()
        hotkey_entry = ttk.Entry(param_frame, textvariable=hotkey_var, width=40)
        
        # Scroll parameters
        scroll_label = ttk.Label(param_frame, text="Arah:")
        scroll_var = tk.StringVar()
        scroll_combo = ttk.Combobox(param_frame, textvariable=scroll_var, values=["up", "down"], state="readonly", width=10)
        scroll_amount_label = ttk.Label(param_frame, text="Jumlah:")
        scroll_amount_var = tk.StringVar()
        scroll_amount_entry = ttk.Entry(param_frame, textvariable=scroll_amount_var, width=10)
        
        # Drag parameters
        drag_label = ttk.Label(param_frame, text="Drag to X:")
        drag_x_var = tk.StringVar()
        drag_x_entry = ttk.Entry(param_frame, textvariable=drag_x_var, width=10)
        drag_y_label = ttk.Label(param_frame, text="Y:")
        drag_y_var = tk.StringVar()
        drag_y_entry = ttk.Entry(param_frame, textvariable=drag_y_var, width=10)
        
        # Capture Mouse button for drag coordinates
        def capture_edit_drag_coordinates():
            """Capture mouse coordinates for drag destination in edit dialog"""
            def capture():
                for i in range(3, 0, -1):
                    status_label.config(text=f"Capture koordinat drag dalam {i} detik...")
                    edit_window.update()
                    time.sleep(1)
                
                pos = pyautogui.position()
                drag_x_var.set(str(pos.x))
                drag_y_var.set(str(pos.y))
                status_label.config(text=f"Koordinat drag captured: ({pos.x}, {pos.y})")
            
            threading.Thread(target=capture, daemon=True).start()
        
        drag_capture_btn = ttk.Button(param_frame, text="Capture Mouse", command=capture_edit_drag_coordinates)
        
        # Initialize parameter values based on current function type
        current_param = func_data.get("parameter", "")
        if func_data["type"] == "Type Text":
            text_var.set(current_param)
        elif func_data["type"] == "Hotkey":
            hotkey_var.set(current_param)
        elif func_data["type"] == "Scroll":
            # Parse scroll parameter (e.g., "up 3")
            parts = current_param.split()
            if len(parts) >= 2:
                scroll_var.set(parts[0])
                scroll_amount_var.set(parts[1])
            else:
                scroll_amount_var.set("3")
        elif func_data["type"] == "Drag":
            # Parse drag parameter (e.g., "to (300, 400)")
            import re
            match = re.search(r'to \((\d+), (\d+)\)', current_param)
            if match:
                drag_x_var.set(match.group(1))
                drag_y_var.set(match.group(2))
        
        # Delay
        ttk.Label(edit_window, text="Delay (detik):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        delay_var = tk.StringVar(value=str(func_data["delay"]))
        delay_entry = ttk.Entry(edit_window, textvariable=delay_var, width=30)
        delay_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Status label for capture feedback
        status_label = ttk.Label(edit_window, text="", foreground="blue")
        status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Function to update coordinate visibility
        def update_coord_visibility(*args):
            if type_var.get() in ["Type Text", "Hotkey", "Delay"]:
                coord_frame.grid_remove()  # Hide entire coordinate frame
            else:
                coord_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)  # Show coordinate frame
        
        # Function to update parameter visibility based on function type
        def update_param_visibility(*args):
            # Hide all parameter widgets first
            for widget in [text_label, text_entry, hotkey_label, hotkey_entry, 
                          scroll_label, scroll_combo, scroll_amount_label, scroll_amount_entry,
                          drag_label, drag_x_entry, drag_y_label, drag_y_entry, drag_capture_btn]:
                widget.grid_remove()
            
            # Show relevant parameter widgets based on function type
            func_type = type_var.get()
            if func_type == "Type Text":
                text_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
                text_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            elif func_type == "Hotkey":
                hotkey_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
                hotkey_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            elif func_type == "Scroll":
                scroll_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
                scroll_combo.grid(row=0, column=1, padx=5, pady=5)
                scroll_amount_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 5), pady=5)
                scroll_amount_entry.grid(row=0, column=3, padx=5, pady=5)
            elif func_type == "Drag":
                drag_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
                drag_x_entry.grid(row=0, column=1, padx=5, pady=5)
                drag_y_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 5), pady=5)
                drag_y_entry.grid(row=0, column=3, padx=5, pady=5)
                drag_capture_btn.grid(row=0, column=4, padx=(10, 5), pady=5)
        
        type_var.trace("w", update_coord_visibility)
        type_var.trace("w", update_param_visibility)
        update_coord_visibility()  # Initial call
        update_param_visibility()  # Initial call
        
        # Delay frame
        delay_frame = ttk.LabelFrame(edit_window, text="Delay")
        delay_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        ttk.Label(delay_frame, text="Delay setelah (detik):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        delay_var = tk.StringVar(value=str(func_data["delay"]))
        delay_entry = ttk.Entry(delay_frame, textvariable=delay_var, width=10)
        delay_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Enabled checkbox frame
        enabled_frame = ttk.LabelFrame(edit_window, text="Status")
        enabled_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        enabled_var = tk.BooleanVar(value=func_data.get('enabled', True))
        enabled_checkbox = ttk.Checkbutton(enabled_frame, text="Aktifkan fungsi ini", variable=enabled_var)
        enabled_checkbox.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(edit_window)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def save_changes():
            """Save the edited function"""
            try:
                # Validate name
                new_name = name_var.get().strip()
                if not new_name:
                    messagebox.showerror("Error", "Nama fungsi tidak boleh kosong!")
                    return
                
                # Get delay
                new_delay = delay_var.get()
                if not new_delay:
                    new_delay = "1.0"
                try:
                    float(new_delay)
                except ValueError:
                    messagebox.showerror("Error", "Delay harus berupa angka!")
                    return
                
                # Get coordinates if needed
                new_x, new_y = None, None
                if type_var.get() not in ["Type Text", "Hotkey", "Delay"]:
                    try:
                        new_x = int(x_var.get()) if x_var.get() else None
                        new_y = int(y_var.get()) if y_var.get() else None
                    except ValueError:
                        messagebox.showerror("Error", "Koordinat harus berupa angka!")
                        return
                
                # Get parameters based on function type
                parameter = ""
                func_type = type_var.get()
                
                if func_type == "Type Text":
                    parameter = text_var.get()
                    if not parameter:
                        messagebox.showerror("Error", "Masukkan text yang akan diketik!")
                        return
                elif func_type == "Hotkey":
                    parameter = hotkey_var.get()
                    if not parameter:
                        messagebox.showerror("Error", "Masukkan hotkey (contoh: ctrl+c)!")
                        return
                elif func_type == "Scroll":
                    direction = scroll_var.get()
                    amount = scroll_amount_var.get()
                    if not direction:
                        messagebox.showerror("Error", "Pilih arah scroll!")
                        return
                    if not amount:
                        amount = "3"
                    parameter = f"{direction} {amount}"
                elif func_type == "Drag":
                    drag_x = drag_x_var.get()
                    drag_y = drag_y_var.get()
                    if not drag_x or not drag_y:
                        messagebox.showerror("Error", "Masukkan koordinat drag tujuan!")
                        return
                    try:
                        int(drag_x)
                        int(drag_y)
                    except ValueError:
                        messagebox.showerror("Error", "Koordinat drag harus berupa angka!")
                        return
                    parameter = f"to ({drag_x}, {drag_y})"
                
                # Update function data
                self.automation_functions[func_index] = {
                    "name": new_name,
                    "type": type_var.get(),
                    "x": new_x,
                    "y": new_y,
                    "parameter": parameter,
                    "delay": new_delay,
                    "enabled": enabled_var.get()
                }
                
                self.update_functions_list()
                edit_window.destroy()
                messagebox.showinfo("Success", "Fungsi berhasil diperbarui!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        
        ttk.Button(btn_frame, text="Simpan", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Batal", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        edit_window.columnconfigure(1, weight=1)
        coord_frame.columnconfigure(1, weight=1)
        coord_frame.columnconfigure(3, weight=1)
        param_frame.columnconfigure(1, weight=1)
    
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
    
    def clear_all(self):
        """Clear all functions"""
        if messagebox.askyesno("Konfirmasi", "Hapus semua fungsi?"):
            self.automation_functions.clear()
            self.update_functions_list()
            self.status_label.config(text="Semua fungsi berhasil dihapus!")
    
    def start_automation(self):
        """Start the automation process"""
        if not self.automation_functions:
            messagebox.showwarning("Warning", "Tambahkan minimal satu fungsi automation!")
            return
        
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
    
    def run_automation(self):
        """Execute all automation functions in sequence"""
        try:
            # Filter only enabled functions
            enabled_functions = [func for func in self.automation_functions if func.get('enabled', True)]
            total_functions = len(enabled_functions)
            
            if total_functions == 0:
                self.status_label.config(text="Tidak ada fungsi yang diaktifkan!")
                self.is_running = False
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                return
            
            self.progress['maximum'] = total_functions
            
            for i, func in enumerate(enabled_functions):
                if not self.is_running:
                    break
                
                self.status_label.config(text=f"Menjalankan: {func.get('name', 'Unnamed')} ({i+1}/{total_functions})")
                self.root.update()
                
                # Execute function based on type
                if func['type'] == "Click":
                    if func['x'] and func['y']:
                        pyautogui.click(func['x'], func['y'])
                
                elif func['type'] == "Double Click":
                    if func['x'] and func['y']:
                        pyautogui.doubleClick(func['x'], func['y'])
                
                elif func['type'] == "Right Click":
                    if func['x'] and func['y']:
                        pyautogui.rightClick(func['x'], func['y'])
                
                elif func['type'] == "Type Text":
                    if func['parameter']:
                        pyautogui.typewrite(func['parameter'])
                
                elif func['type'] == "Hotkey":
                    if func['parameter']:
                        keys = func['parameter'].replace(' ', '').split('+')
                        pyautogui.hotkey(*keys)
                
                elif func['type'] == "Delay":
                    time.sleep(func['delay'])
                    continue  # Skip the normal delay for this function
                
                elif func['type'] == "Scroll":
                    if func['x'] and func['y']:
                        pyautogui.moveTo(func['x'], func['y'])  # Move mouse to position without clicking
                    parts = func['parameter'].split()
                    if len(parts) >= 2:
                        direction = parts[0]
                        amount = int(parts[1])
                        scroll_amount = amount if direction == "Up" else -amount
                        pyautogui.scroll(scroll_amount)
                
                elif func['type'] == "Drag":
                    if func['x'] and func['y'] and func['parameter']:
                        # Extract target coordinates from parameter
                        import re
                        coords = re.findall(r'\d+', func['parameter'])
                        if len(coords) >= 2:
                            target_x, target_y = int(coords[0]), int(coords[1])
                            # Move to start position first, then drag to target position
                            pyautogui.moveTo(func['x'], func['y'])
                            pyautogui.dragTo(target_x, target_y, duration=1, button='left')
                
                # Apply delay after function execution
                if func['delay'] > 0:
                    time.sleep(func['delay'])
                
                # Update progress
                self.progress['value'] = i + 1
                self.root.update()
            
            if self.is_running:
                self.status_label.config(text="Automation selesai!")
                messagebox.showinfo("Selesai", "Semua fungsi automation telah dijalankan!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi error: {str(e)}")
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
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
                
                # Ensure backward compatibility by adding enabled field if missing
                for func in loaded_functions:
                    if 'enabled' not in func:
                        func['enabled'] = True
                
                self.automation_functions = loaded_functions
                self.update_functions_list()
                messagebox.showinfo("Berhasil", f"Konfigurasi dimuat dari {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat: {str(e)}")

def main():
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()