import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import threading
import json
import requests
import pyperclip
from pynput import keyboard
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
from functions.treeview_handlers import on_treeview_click
from functions.function_type_handlers import on_function_type_change
from functions.parameter_handlers import hide_all_parameters
from functions.screen_capture_handlers import capture_screen_region
from functions.text_input_handlers import show_text_input_popup
from functions.coordinate_handlers import capture_coordinates
from functions.image_handlers import browse_image_file, update_image_preview, wait_for_image
from functions.text_handlers import safe_typewrite, process_text_for_typing

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flexible Automation GUI")
        self.root.geometry("800x600")
        
        # List untuk menyimpan semua fungsi automation
        self.automation_functions = []
        self.is_running = False
        self.current_thread = None
        self.emergency_stop = False
        self.hotkey_listener = None
        
        # Variable storage system
        self.variables = {}  # Dictionary to store variables {name: value}
        
        # Enable pyautogui failsafe as backup (move mouse to top-left corner)
        pyautogui.FAILSAFE = True
        
        # Setup emergency stop hotkey listener
        self.setup_emergency_stop()
        
        self.setup_ui()
    
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
            "Click", "Type Text", "Type Text Popup", "Delay", "Hotkey", "Scroll", "Drag", "Double Click", "Right Click", "HTTP Request", "Wait for Image", "Set Variable", "Get Variable"
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
        
        # HTTP Request parameters
        self.http_url_label = ttk.Label(param_frame, text="URL:")
        self.http_url_entry = ttk.Entry(param_frame, width=40)
        
        self.http_method_label = ttk.Label(param_frame, text="Method:")
        self.http_method = ttk.Combobox(param_frame, values=["GET", "POST", "PUT", "DELETE", "PATCH"], state="readonly", width=10)
        self.http_method.set("GET")
        
        self.http_headers_label = ttk.Label(param_frame, text="Headers (JSON):")
        self.http_headers_entry = ttk.Entry(param_frame, width=40)
        self.http_headers_entry.insert(0, '{"Content-Type": "application/json"}')
        
        self.http_body_label = ttk.Label(param_frame, text="Body (JSON):")
        self.http_body_entry = ttk.Entry(param_frame, width=40)
        
        self.http_loop_label = ttk.Label(param_frame, text="Loop Count:")
        self.http_loop_entry = ttk.Entry(param_frame, width=8)
        self.http_loop_entry.insert(0, "1")
        
        self.http_loop_delay_label = ttk.Label(param_frame, text="Loop Delay (s):")
        self.http_loop_delay_entry = ttk.Entry(param_frame, width=8)
        self.http_loop_delay_entry.insert(0, "1.0")
        
        # Wait for Image parameters
        self.image_label = ttk.Label(param_frame, text="Template Image:")
        self.image_path_entry = ttk.Entry(param_frame, width=40)
        self.image_browse_btn = ttk.Button(param_frame, text="Browse", command=self.browse_image_file)
        self.image_capture_btn = ttk.Button(param_frame, text="Capture Screen", command=self.capture_screen_region)
        
        self.image_threshold_label = ttk.Label(param_frame, text="Threshold:")
        self.image_threshold_entry = ttk.Entry(param_frame, width=8)
        self.image_threshold_entry.insert(0, "0.8")
        
        self.image_timeout_label = ttk.Label(param_frame, text="Timeout (s):")
        self.image_timeout_entry = ttk.Entry(param_frame, width=8)
        self.image_timeout_entry.insert(0, "30")
        
        self.image_preview_label = ttk.Label(param_frame, text="Preview:")
        self.image_preview = ttk.Label(param_frame, text="No image selected", relief="sunken", width=20)
        
        # Variable parameters
        self.variable_name_label = ttk.Label(param_frame, text="Variable Name:")
        self.variable_name_entry = ttk.Entry(param_frame, width=20)
        
        self.variable_value_label = ttk.Label(param_frame, text="Variable Value:")
        self.variable_value_entry = ttk.Entry(param_frame, width=30)
        
        self.variable_source_label = ttk.Label(param_frame, text="Value Source:")
        self.variable_source_combo = ttk.Combobox(param_frame, values=[
            "Manual Input", "Clipboard", "Current Time", "Random Number", "Screen Text (OCR)", "Last Click Position"
        ], state="readonly", width=20)
        self.variable_source_combo.set("Manual Input")
        
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
        
        # Emergency stop indicator
        self.emergency_stop_label = ttk.Label(control_frame, text="Emergency Stop: Ctrl+Alt+Q", 
                                            foreground="red", font=("Arial", 9, "bold"))
        self.emergency_stop_label.grid(row=0, column=1, sticky=tk.E, pady=(0, 10))
        
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
        ttk.Button(btn_control_frame, text="Load Config", command=self.load_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_control_frame, text="Variable Manager", command=self.show_variable_manager).pack(side=tk.LEFT)
        
        # Initially hide parameter widgets
        self.hide_all_parameters()
    
    # Import the on_treeview_click method from the separate module
    on_treeview_click = on_treeview_click
    
    # Import the on_function_type_change method from the separate module
    on_function_type_change = on_function_type_change
    
    # Import the hide_all_parameters method from the separate module
    hide_all_parameters = hide_all_parameters
    
    # Import the capture_coordinates method from the separate module
    capture_coordinates = capture_coordinates
    
    # Import the browse_image_file method from the separate module
    browse_image_file = browse_image_file
    
    # Import the update_image_preview method from the separate module
    update_image_preview = update_image_preview
    
    # Import the capture_screen_region method from the separate module
    capture_screen_region = capture_screen_region
    
    # Import the wait_for_image method from the separate module
    wait_for_image = wait_for_image
    
    # Import the show_text_input_popup method from the separate module
    show_text_input_popup = show_text_input_popup
    
    # Import the safe_typewrite method from the separate module
    safe_typewrite = safe_typewrite
    
    # Import the process_text_for_typing method from the separate module
    process_text_for_typing = process_text_for_typing
    
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
            elif func_type == "Type Text Popup":
                # For Type Text Popup, we don't need parameter validation here
                # The text will be entered during execution via popup
                parameter = "popup_text"  # Placeholder to indicate popup text input
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
            elif func_type == "HTTP Request":
                url = self.http_url_entry.get().strip()
                method = self.http_method.get()
                headers = self.http_headers_entry.get().strip()
                body = self.http_body_entry.get().strip()
                loop_count = self.http_loop_entry.get().strip()
                loop_delay = self.http_loop_delay_entry.get().strip()
                
                if not url:
                    messagebox.showwarning("Warning", "Masukkan URL!")
                    return
                
                # Validate JSON format for headers
                try:
                    if headers:
                        json.loads(headers)
                except json.JSONDecodeError:
                    messagebox.showwarning("Warning", "Format headers harus JSON yang valid!")
                    return
                
                # Validate JSON format for body if not empty
                try:
                    if body:
                        json.loads(body)
                except json.JSONDecodeError:
                    messagebox.showwarning("Warning", "Format body harus JSON yang valid!")
                    return
                
                # Validate loop count
                try:
                    loop_count_int = int(loop_count) if loop_count else 1
                    if loop_count_int < 1:
                        messagebox.showwarning("Warning", "Loop count harus minimal 1!")
                        return
                except ValueError:
                    messagebox.showwarning("Warning", "Loop count harus berupa angka!")
                    return
                
                # Validate loop delay
                try:
                    loop_delay_float = float(loop_delay) if loop_delay else 1.0
                    if loop_delay_float < 0:
                        messagebox.showwarning("Warning", "Loop delay tidak boleh negatif!")
                        return
                except ValueError:
                    messagebox.showwarning("Warning", "Loop delay harus berupa angka!")
                    return
                
                parameter = json.dumps({
                    "url": url,
                    "method": method,
                    "headers": headers,
                    "body": body,
                    "loop_count": loop_count_int,
                    "loop_delay": loop_delay_float
                })
            elif func_type == "Wait for Image":
                image_path = self.image_path_entry.get().strip()
                threshold = self.image_threshold_entry.get().strip()
                timeout = self.image_timeout_entry.get().strip()
                
                if not image_path:
                    messagebox.showwarning("Warning", "Pilih atau capture gambar template!")
                    return
                
                if not os.path.exists(image_path):
                    messagebox.showwarning("Warning", "File gambar template tidak ditemukan!")
                    return
                
                # Validate threshold
                try:
                    threshold_float = float(threshold) if threshold else 0.8
                    if not (0.0 <= threshold_float <= 1.0):
                        messagebox.showwarning("Warning", "Threshold harus antara 0.0 dan 1.0!")
                        return
                except ValueError:
                    messagebox.showwarning("Warning", "Threshold harus berupa angka!")
                    return
                
                # Validate timeout
                try:
                    timeout_int = int(timeout) if timeout else 30
                    if timeout_int < 1:
                        messagebox.showwarning("Warning", "Timeout harus minimal 1 detik!")
                        return
                except ValueError:
                    messagebox.showwarning("Warning", "Timeout harus berupa angka!")
                    return
                
                parameter = json.dumps({
                    "image_path": image_path,
                    "threshold": threshold_float,
                    "timeout": timeout_int
                })
            elif func_type == "Set Variable":
                variable_name = self.variable_name_entry.get().strip()
                variable_source = self.variable_source_combo.get()
                variable_value = self.variable_value_entry.get()
                
                if not variable_name:
                    messagebox.showwarning("Warning", "Masukkan nama variabel!")
                    return
                
                if not variable_source:
                    messagebox.showwarning("Warning", "Pilih sumber nilai variabel!")
                    return
                
                if variable_source == "Manual Input" and not variable_value:
                    messagebox.showwarning("Warning", "Masukkan nilai variabel!")
                    return
                
                parameter = json.dumps({
                    "variable_name": variable_name,
                    "variable_source": variable_source,
                    "variable_value": variable_value
                })
            elif func_type == "Get Variable":
                variable_name = self.variable_name_entry.get().strip()
                
                if not variable_name:
                    messagebox.showwarning("Warning", "Masukkan nama variabel!")
                    return
                
                parameter = json.dumps({
                    "variable_name": variable_name
                })
            
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
        
        # Clear HTTP request fields
        self.http_url_entry.delete(0, tk.END)
        self.http_method.set("GET")
        self.http_headers_entry.delete(0, tk.END)
        self.http_headers_entry.insert(0, '{"Content-Type": "application/json"}')
        self.http_body_entry.delete(0, tk.END)
        self.http_loop_entry.delete(0, tk.END)
        self.http_loop_entry.insert(0, "1")
        self.http_loop_delay_entry.delete(0, tk.END)
        self.http_loop_delay_entry.insert(0, "1.0")
        
        # Clear Wait for Image fields
        self.image_path_entry.delete(0, tk.END)
        self.image_threshold_entry.delete(0, tk.END)
        self.image_threshold_entry.insert(0, "0.8")
        self.image_timeout_entry.delete(0, tk.END)
        self.image_timeout_entry.insert(0, "30")
        self.image_preview.config(image='', text="No image")
        
        # Clear Variable fields
        self.variable_name_entry.delete(0, tk.END)
        self.variable_value_entry.delete(0, tk.END)
        self.variable_source_combo.set("Manual Input")
        
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
            "Click", "Type Text", "Type Text Popup", "Delay", "Hotkey", "Scroll", "Drag", "Double Click", "Right Click", "HTTP Request", "Wait for Image", "Set Variable", "Get Variable"
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
        
        # HTTP Request parameters
        http_url_label = ttk.Label(param_frame, text="URL:")
        http_url_var = tk.StringVar()
        http_url_entry = ttk.Entry(param_frame, textvariable=http_url_var, width=40)
        
        http_method_label = ttk.Label(param_frame, text="Method:")
        http_method_var = tk.StringVar()
        http_method_combo = ttk.Combobox(param_frame, textvariable=http_method_var, values=["GET", "POST", "PUT", "DELETE", "PATCH"], state="readonly", width=10)
        
        http_headers_label = ttk.Label(param_frame, text="Headers (JSON):")
        http_headers_var = tk.StringVar()
        http_headers_entry = ttk.Entry(param_frame, textvariable=http_headers_var, width=40)
        
        http_body_label = ttk.Label(param_frame, text="Body (JSON):")
        http_body_var = tk.StringVar()
        http_body_entry = ttk.Entry(param_frame, textvariable=http_body_var, width=40)
        
        http_loop_label = ttk.Label(param_frame, text="Loop Count:")
        http_loop_var = tk.StringVar()
        http_loop_entry = ttk.Entry(param_frame, textvariable=http_loop_var, width=10)
        
        http_loop_delay_label = ttk.Label(param_frame, text="Loop Delay (s):")
        http_loop_delay_var = tk.StringVar()
        http_loop_delay_entry = ttk.Entry(param_frame, textvariable=http_loop_delay_var, width=10)
        
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
        elif func_data["type"] == "HTTP Request":
            # Parse HTTP Request parameter (JSON format)
            try:
                import json
                http_params = json.loads(current_param)
                http_url_var.set(http_params.get("url", ""))
                http_method_var.set(http_params.get("method", "GET"))
                http_headers_var.set(json.dumps(http_params.get("headers", {})))
                http_body_var.set(json.dumps(http_params.get("body", {})))
                http_loop_var.set(str(http_params.get("loop_count", 1)))
                http_loop_delay_var.set(str(http_params.get("loop_delay", 1.0)))
            except (json.JSONDecodeError, KeyError):
                # Set default values if parsing fails
                http_url_var.set("")
                http_method_var.set("GET")
                http_headers_var.set('{"Content-Type": "application/json"}')
                http_body_var.set("{}")
                http_loop_var.set("1")
                http_loop_delay_var.set("1.0")
        
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
            if type_var.get() in ["Type Text", "Type Text Popup", "Hotkey", "Delay", "HTTP Request"]:
                coord_frame.grid_remove()  # Hide entire coordinate frame
            else:
                coord_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)  # Show coordinate frame
        
        # Function to update parameter visibility based on function type
        def update_param_visibility(*args):
            # Hide all parameter widgets first
            for widget in [text_label, text_entry, hotkey_label, hotkey_entry, 
                          scroll_label, scroll_combo, scroll_amount_label, scroll_amount_entry,
                          drag_label, drag_x_entry, drag_y_label, drag_y_entry, drag_capture_btn,
                          http_url_label, http_url_entry, http_method_label, http_method_combo,
                          http_headers_label, http_headers_entry, http_body_label, http_body_entry,
                          http_loop_label, http_loop_entry, http_loop_delay_label, http_loop_delay_entry]:
                widget.grid_remove()
            
            # Show relevant parameter widgets based on function type
            func_type = type_var.get()
            if func_type == "Type Text":
                text_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
                text_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
            elif func_type == "Type Text Popup":
                # Type Text Popup doesn't need parameters in edit mode
                # The text will be entered through a popup during execution
                pass
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
            elif func_type == "HTTP Request":
                http_url_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
                http_url_entry.grid(row=0, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
                http_method_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
                http_method_combo.grid(row=1, column=1, padx=5, pady=5)
                http_headers_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
                http_headers_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
                http_body_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
                http_body_entry.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
                http_loop_label.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
                http_loop_entry.grid(row=4, column=1, padx=5, pady=5)
                http_loop_delay_label.grid(row=4, column=2, sticky=tk.W, padx=(10, 5), pady=5)
                http_loop_delay_entry.grid(row=4, column=3, padx=5, pady=5)
        
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
                if type_var.get() not in ["Type Text", "Type Text Popup", "Hotkey", "Delay", "HTTP Request"]:
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
                elif func_type == "Type Text Popup":
                    # For Type Text Popup, we don't need parameter validation here
                    # The text will be entered during execution via popup
                    parameter = "popup_text"  # Placeholder to indicate popup text input
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
                elif func_type == "HTTP Request":
                    # Validate and construct HTTP Request parameter
                    url = http_url_var.get().strip()
                    method = http_method_var.get()
                    headers_str = http_headers_var.get().strip()
                    body_str = http_body_var.get().strip()
                    loop_count_str = http_loop_var.get().strip()
                    loop_delay_str = http_loop_delay_var.get().strip()
                    
                    if not url:
                        messagebox.showerror("Error", "URL tidak boleh kosong!")
                        return
                    
                    # Validate JSON format for headers
                    try:
                        headers = json.loads(headers_str) if headers_str else {}
                    except json.JSONDecodeError:
                        messagebox.showerror("Error", "Format headers harus JSON yang valid!")
                        return
                    
                    # Validate JSON format for body
                    try:
                        body = json.loads(body_str) if body_str else {}
                    except json.JSONDecodeError:
                        messagebox.showerror("Error", "Format body harus JSON yang valid!")
                        return
                    
                    # Validate loop count
                    try:
                        loop_count_int = int(loop_count_str) if loop_count_str else 1
                        if loop_count_int <= 0:
                            messagebox.showerror("Error", "Loop count harus berupa angka positif!")
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Loop count harus berupa angka!")
                        return
                    
                    # Validate loop delay
                    try:
                        loop_delay_float = float(loop_delay_str) if loop_delay_str else 1.0
                        if loop_delay_float < 0:
                            messagebox.showerror("Error", "Loop delay harus berupa angka positif!")
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Loop delay harus berupa angka!")
                        return
                    
                    # Construct parameter JSON
                    parameter = json.dumps({
                        "url": url,
                        "method": method,
                        "headers": headers,
                        "body": body,
                        "loop_count": loop_count_int,
                        "loop_delay": loop_delay_float
                    })
                
                # Update function data
                self.automation_functions[func_index] = {
                    "name": new_name,
                    "type": type_var.get(),
                    "x": new_x,
                    "y": new_y,
                    "parameter": parameter,
                    "delay": float(new_delay),  # Convert to float to ensure consistent data type
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
                # Check for emergency stop or normal stop
                if not self.is_running or self.emergency_stop:
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
                        processed_text = self.process_text_for_typing(func['parameter'])
                        self.safe_typewrite(processed_text)
                
                elif func['type'] == "Type Text Popup":
                    # Show popup to get text input
                    popup_result = self.show_text_input_popup(func.get('name', 'Fungsi'))
                    if popup_result["confirmed"] and popup_result["text"]:
                        # Wait 2 seconds after OK is clicked before moving cursor
                        time.sleep(2)
                        
                        # Check if we should click at the original position first
                        if popup_result.get("click_before_type", True) and popup_result.get("click_position"):
                            # Move mouse back to original position and click
                            original_pos = popup_result["click_position"]
                            pyautogui.click(original_pos.x, original_pos.y)
                        
                        # Wait 1 second before typing
                        time.sleep(1)
                        # Process and type the entered text
                        processed_text = self.process_text_for_typing(popup_result["text"])
                        self.safe_typewrite(processed_text)
                    elif not popup_result["confirmed"]:
                        # If cancelled, skip this function
                        continue
                
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
                
                elif func['type'] == "HTTP Request":
                    if func['parameter']:
                        try:
                            # Parse HTTP request parameters
                            http_params = json.loads(func['parameter'])
                            url = http_params.get('url', '')
                            method = http_params.get('method', 'GET').upper()
                            headers_str = http_params.get('headers', '{}')
                            body_str = http_params.get('body', '')
                            loop_count = http_params.get('loop_count', 1)
                            loop_delay = http_params.get('loop_delay', 1.0)
                            
                            # Parse headers and body JSON
                            headers = json.loads(headers_str) if headers_str else {}
                            body_data = json.loads(body_str) if body_str else None
                            
                            # Execute HTTP requests with looping
                            for loop_i in range(loop_count):
                                if not self.is_running:
                                    break
                                
                                # Update status for loop iteration
                                if loop_count > 1:
                                    self.status_label.config(text=f"Menjalankan: {func.get('name', 'Unnamed')} - Loop {loop_i+1}/{loop_count} ({i+1}/{total_functions})")
                                    self.root.update()
                                
                                # Make HTTP request
                                response = None
                                if method == 'GET':
                                    response = requests.get(url, headers=headers, timeout=30)
                                elif method == 'POST':
                                    if body_data:
                                        response = requests.post(url, headers=headers, json=body_data, timeout=30)
                                    else:
                                        response = requests.post(url, headers=headers, timeout=30)
                                elif method == 'PUT':
                                    if body_data:
                                        response = requests.put(url, headers=headers, json=body_data, timeout=30)
                                    else:
                                        response = requests.put(url, headers=headers, timeout=30)
                                elif method == 'DELETE':
                                    response = requests.delete(url, headers=headers, timeout=30)
                                elif method == 'PATCH':
                                    if body_data:
                                        response = requests.patch(url, headers=headers, json=body_data, timeout=30)
                                    else:
                                        response = requests.patch(url, headers=headers, timeout=30)
                                
                                # Log response status
                                if response:
                                    print(f"HTTP {method} {url} - Status: {response.status_code}")
                                    if response.status_code >= 400:
                                        print(f"Response: {response.text}")
                                
                                # Apply loop delay if not the last iteration
                                if loop_i < loop_count - 1 and loop_delay > 0:
                                    time.sleep(loop_delay)
                                    
                        except requests.exceptions.RequestException as e:
                            print(f"HTTP Request Error: {str(e)}")
                            messagebox.showwarning("HTTP Error", f"HTTP Request gagal: {str(e)}")
                        except json.JSONDecodeError as e:
                            print(f"JSON Parse Error: {str(e)}")
                            messagebox.showwarning("JSON Error", f"Error parsing JSON: {str(e)}")
                        except Exception as e:
                            print(f"Unexpected Error: {str(e)}")
                            messagebox.showwarning("Error", f"Error pada HTTP Request: {str(e)}")
                
                elif func['type'] == "Wait for Image":
                    if func['parameter']:
                        try:
                            # Parse Wait for Image parameters
                            image_params = json.loads(func['parameter'])
                            image_path = image_params.get('image_path', '')
                            threshold = image_params.get('threshold', 0.8)
                            timeout = image_params.get('timeout', 30)
                            
                            # Update status to show waiting
                            self.status_label.config(text=f"Menunggu gambar: {func.get('name', 'Unnamed')} ({i+1}/{total_functions})")
                            self.root.update()
                            
                            # Wait for image to appear
                            success, message = self.wait_for_image(image_path, threshold, timeout)
                            
                            if success:
                                print(f"Wait for Image Success: {message}")
                            else:
                                print(f"Wait for Image Failed: {message}")
                                if "Stopped by user" not in message:
                                    messagebox.showwarning("Wait for Image", f"Gambar tidak ditemukan: {message}")
                                
                        except json.JSONDecodeError as e:
                            print(f"JSON Parse Error in Wait for Image: {str(e)}")
                            messagebox.showwarning("JSON Error", f"Error parsing Wait for Image parameters: {str(e)}")
                        except Exception as e:
                            print(f"Unexpected Error in Wait for Image: {str(e)}")
                            messagebox.showwarning("Error", f"Error pada Wait for Image: {str(e)}")
                
                elif func['type'] == "Set Variable":
                    if func['parameter']:
                        try:
                            # Parse Set Variable parameters
                            var_params = json.loads(func['parameter'])
                            var_name = var_params.get('variable_name', '')
                            var_source = var_params.get('variable_source', 'Manual Input')
                            var_value = var_params.get('variable_value', '')
                            
                            # Get value based on source
                            if var_source == "Manual Input":
                                value = var_value
                            elif var_source == "Clipboard":
                                value = pyperclip.paste()
                            elif var_source == "Current Time":
                                import datetime
                                value = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                value = var_value
                            
                            # Store variable
                            self.variables[var_name] = value
                            print(f"Variable '{var_name}' set to: {value}")
                            
                        except json.JSONDecodeError as e:
                            print(f"JSON Parse Error in Set Variable: {str(e)}")
                            messagebox.showwarning("JSON Error", f"Error parsing Set Variable parameters: {str(e)}")
                        except Exception as e:
                            print(f"Unexpected Error in Set Variable: {str(e)}")
                            messagebox.showwarning("Error", f"Error pada Set Variable: {str(e)}")
                
                elif func['type'] == "Get Variable":
                    if func['parameter']:
                        try:
                            # Parse Get Variable parameters
                            var_params = json.loads(func['parameter'])
                            var_name = var_params.get('variable_name', '')
                            
                            # Get variable value
                            if var_name in self.variables:
                                value = self.variables[var_name]
                                # Copy to clipboard for use
                                pyperclip.copy(str(value))
                                print(f"Variable '{var_name}' retrieved: {value} (copied to clipboard)")
                            else:
                                print(f"Variable '{var_name}' not found")
                                messagebox.showwarning("Variable Error", f"Variabel '{var_name}' tidak ditemukan!")
                            
                        except json.JSONDecodeError as e:
                            print(f"JSON Parse Error in Get Variable: {str(e)}")
                            messagebox.showwarning("JSON Error", f"Error parsing Get Variable parameters: {str(e)}")
                        except Exception as e:
                            print(f"Unexpected Error in Get Variable: {str(e)}")
                            messagebox.showwarning("Error", f"Error pada Get Variable: {str(e)}")
                
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

def main():
    root = tk.Tk()
    app = AutomationGUI(root)
    
    # Ensure cleanup on window close
    def on_closing():
        app.cleanup_emergency_stop()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()