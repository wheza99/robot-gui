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
            "Click", "Type Text", "Type Text Popup", "Delay", "Hotkey", "Scroll", "Drag", "Double Click", "Right Click", "HTTP Request", "Wait for Image"
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
        if func_type in ["Type Text", "Type Text Popup", "Hotkey", "Delay", "HTTP Request"]:
            # Hide coordinate section for functions that don't need coordinates
            self.coord_frame.grid_remove()
        elif func_type:
            # Show coordinate section for functions that need coordinates
            self.coord_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        if func_type == "Type Text":
            self.text_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.text_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        elif func_type == "Type Text Popup":
            # Type Text Popup doesn't need parameters in the main form
            # The text will be entered through a popup during execution
            pass
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
        elif func_type == "HTTP Request":
            # Row 0: URL
            self.http_url_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.http_url_entry.grid(row=0, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=(0, 10))
            
            # Row 1: Method and Headers
            self.http_method_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.http_method.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.http_headers_label.grid(row=1, column=2, sticky=tk.W, padx=(10, 10), pady=(5, 0))
            self.http_headers_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
            
            # Row 2: Body
            self.http_body_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.http_body_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
            
            # Row 3: Loop settings
            self.http_loop_label.grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.http_loop_entry.grid(row=3, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.http_loop_delay_label.grid(row=3, column=2, sticky=tk.W, padx=(10, 10), pady=(5, 0))
            self.http_loop_delay_entry.grid(row=3, column=3, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        elif func_type == "Wait for Image":
            # Row 0: Image file selection
            self.image_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            self.image_path_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
            self.image_browse_btn.grid(row=0, column=3, padx=(5, 5))
            self.image_capture_btn.grid(row=0, column=4, padx=(5, 0))
            
            # Row 1: Threshold and Timeout
            self.image_threshold_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.image_threshold_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.image_timeout_label.grid(row=1, column=2, sticky=tk.W, padx=(10, 10), pady=(5, 0))
            self.image_timeout_entry.grid(row=1, column=3, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            
            # Row 2: Preview
            self.image_preview_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            self.image_preview.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=(0, 10), pady=(5, 0))
    
    def hide_all_parameters(self):
        """Hide all parameter widgets"""
        widgets_to_hide = [
            self.text_label, self.text_entry,
            self.hotkey_label, self.hotkey_entry,
            self.scroll_label, self.scroll_direction, self.scroll_amount_label, self.scroll_amount,
            self.drag_label, self.drag_x_label, self.drag_x, self.drag_y_label, self.drag_y, self.drag_capture_btn,
            self.http_url_label, self.http_url_entry, self.http_method_label, self.http_method,
            self.http_headers_label, self.http_headers_entry, self.http_body_label, self.http_body_entry,
            self.http_loop_label, self.http_loop_entry, self.http_loop_delay_label, self.http_loop_delay_entry,
            self.image_label, self.image_path_entry, self.image_browse_btn, self.image_capture_btn,
            self.image_threshold_label, self.image_threshold_entry, self.image_timeout_label, self.image_timeout_entry,
            self.image_preview_label, self.image_preview
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
    
    def browse_image_file(self):
        """Browse for image file"""
        file_path = filedialog.askopenfilename(
            title="Pilih gambar template",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, file_path)
            self.update_image_preview(file_path)
    
    def capture_screen_region(self):
        """Capture a region of the screen as template image"""
        self.root.withdraw()  # Hide main window
        
        # Create a fullscreen transparent window for selection
        capture_window = tk.Toplevel()
        capture_window.attributes('-fullscreen', True)
        capture_window.attributes('-alpha', 0.3)
        capture_window.configure(bg='black')
        capture_window.attributes('-topmost', True)
        
        # Variables for selection
        start_x = start_y = end_x = end_y = 0
        selection_rect = None
        
        canvas = tk.Canvas(capture_window, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        def on_mouse_press(event):
            nonlocal start_x, start_y, selection_rect
            start_x, start_y = event.x, event.y
            if selection_rect:
                canvas.delete(selection_rect)
        
        def on_mouse_drag(event):
            nonlocal selection_rect, end_x, end_y
            end_x, end_y = event.x, event.y
            if selection_rect:
                canvas.delete(selection_rect)
            selection_rect = canvas.create_rectangle(
                start_x, start_y, end_x, end_y, 
                outline='red', width=2
            )
        
        def on_mouse_release(event):
            nonlocal end_x, end_y
            end_x, end_y = event.x, event.y
            
            # Capture the selected region
            if abs(end_x - start_x) > 10 and abs(end_y - start_y) > 10:
                # Ensure coordinates are in correct order
                left = min(start_x, end_x)
                top = min(start_y, end_y)
                right = max(start_x, end_x)
                bottom = max(start_y, end_y)
                
                # Take screenshot of the selected region
                screenshot = pyautogui.screenshot(region=(left, top, right-left, bottom-top))
                
                # Save to temp file
                temp_dir = os.path.join(os.path.dirname(__file__), 'temp_images')
                os.makedirs(temp_dir, exist_ok=True)
                
                timestamp = int(time.time())
                temp_path = os.path.join(temp_dir, f'captured_template_{timestamp}.png')
                screenshot.save(temp_path)
                
                # Update UI
                self.image_path_entry.delete(0, tk.END)
                self.image_path_entry.insert(0, temp_path)
                self.update_image_preview(temp_path)
                
                capture_window.destroy()
                self.root.deiconify()  # Show main window
            else:
                capture_window.destroy()
                self.root.deiconify()
                messagebox.showwarning("Peringatan", "Area yang dipilih terlalu kecil!")
        
        def on_escape(event):
            capture_window.destroy()
            self.root.deiconify()
        
        canvas.bind('<Button-1>', on_mouse_press)
        canvas.bind('<B1-Motion>', on_mouse_drag)
        canvas.bind('<ButtonRelease-1>', on_mouse_release)
        capture_window.bind('<Escape>', on_escape)
        
        # Instructions
        instruction_label = tk.Label(
            capture_window, 
            text="Drag untuk memilih area gambar template. Tekan ESC untuk membatalkan.",
            fg='white', bg='black', font=('Arial', 12)
        )
        instruction_label.pack(pady=20)
    
    def update_image_preview(self, image_path):
        """Update image preview"""
        try:
            # Load and resize image for preview
            pil_image = Image.open(image_path)
            
            # Calculate size to fit in preview (max 150x150)
            max_size = 150
            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update preview label
            self.image_preview.config(image=photo)
            self.image_preview.image = photo  # Keep a reference
            
        except Exception as e:
            self.image_preview.config(image='', text=f"Error: {str(e)}")
    
    def wait_for_image(self, template_path, threshold=0.8, timeout=30):
        """Wait for image to appear on screen using template matching"""
        if not os.path.exists(template_path):
            return False, "Template image file not found"
        
        try:
            # Load template image
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return False, "Could not load template image"
            
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            template_h, template_w = template_gray.shape
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.emergency_stop or not self.is_running:
                    return False, "Stopped by user"
                
                # Take screenshot
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
                
                # Template matching
                result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= threshold:
                    # Image found
                    center_x = max_loc[0] + template_w // 2
                    center_y = max_loc[1] + template_h // 2
                    return True, f"Image found at ({center_x}, {center_y}) with confidence {max_val:.2f}"
                
                time.sleep(0.5)  # Check every 500ms
            
            return False, f"Image not found within {timeout} seconds"
            
        except Exception as e:
            return False, f"Error during image matching: {str(e)}"
    
    def show_text_input_popup(self, function_name=None):
        """Show popup window for text input and return the entered text"""
        popup_result = {"text": "", "confirmed": False, "click_position": None}
        
        # Store current mouse position before showing popup
        current_pos = pyautogui.position()
        popup_result["click_position"] = current_pos
        
        # Store main window state
        main_window_state = self.root.state()
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Input Text")
        popup.geometry("520x230")  # Increased width and height for better layout
        popup.resizable(False, False)
        
        # Make popup always on top and independent
        popup.attributes('-topmost', True)
        # Remove transient to make popup independent from main window
        popup.grab_set()
        
        # Center the popup on screen (not relative to main window)
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        
        # Bring popup to front and focus
        popup.lift()
        popup.focus_force()
        
        # Now minimize main window after popup is created and positioned
        self.root.iconify()
        
        # Main frame
        main_frame = ttk.Frame(popup, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_text = "Masukkan text yang akan diketik:"
        if function_name:
            title_text = f"Masukkan text untuk ({function_name}) yang akan diketik:"
        
        title_label = ttk.Label(main_frame, text=title_text, 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Text input field (multiline) - fixed height to ensure buttons are visible
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(pady=(0, 15), fill=tk.X)  # Changed from fill=BOTH, expand=True
        
        text_widget = tk.Text(text_frame, font=("Arial", 11), width=50, height=4, wrap=tk.WORD)  # Reduced height from 6 to 4
        text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Changed from fill=BOTH
        
        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.focus()
        
        # Checkbox for click position option
        click_option_var = tk.BooleanVar(value=True)
        click_checkbox = ttk.Checkbutton(main_frame, 
                                        text="Klik di posisi kursor sebelum mengetik", 
                                        variable=click_option_var)
        click_checkbox.pack(pady=(0, 4), anchor='w')
        
        # Button frame - pack normally after checkbox
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(0, 0))  # Pack normally with no padding
        
        def on_ok():
            popup_result["text"] = text_widget.get("1.0", tk.END).rstrip('\n')  # Get all text and remove trailing newline
            popup_result["confirmed"] = True
            popup_result["click_before_type"] = click_option_var.get()
            popup.destroy()
        
        def on_cancel():
            popup_result["confirmed"] = False
            popup.destroy()
        
        # OK and Cancel buttons with better styling - using tk.Button for larger appearance
        ok_btn = tk.Button(btn_frame, text="OK", command=on_ok, 
                          width=8, height=1, 
                          font=("Arial", 9, "bold"),
                          bg="#4CAF50", fg="white",
                          relief="raised", bd=1)
        ok_btn.pack(side=tk.LEFT, padx=(0, 5), pady=0)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=on_cancel, 
                              width=8, height=1,
                              font=("Arial", 9),
                              bg="#f44336", fg="white",
                              relief="raised", bd=1)
        cancel_btn.pack(side=tk.LEFT, padx=(5, 0), pady=0)
        
        # Center the buttons within the frame
        btn_frame.pack_configure(anchor='center')
        
        # Bind keyboard shortcuts for better UX
        def on_enter(event):
            # Enter key confirms (OK)
            on_ok()
            return "break"  # Prevent default behavior
        
        def on_shift_enter(event):
            # Shift+Enter creates new line
            text_widget.insert(tk.INSERT, '\n')
            return "break"  # Prevent default behavior
        
        def on_ctrl_enter(event):
            # Ctrl+Enter creates new line (alternative)
            text_widget.insert(tk.INSERT, '\n')
            return "break"  # Prevent default behavior
        
        # Bind Enter key to OK button when it has focus
        def on_button_enter(event):
            on_ok()
        
        # Bind keyboard events
        text_widget.bind("<Return>", on_enter)
        text_widget.bind("<Shift-Return>", on_shift_enter)
        text_widget.bind("<Control-Return>", on_ctrl_enter)
        popup.bind("<Return>", on_enter)
        ok_btn.bind("<Return>", on_button_enter)
        
        # Make OK button accessible via Tab navigation
        ok_btn.focus_set()
        
        # Wait for popup to close
        popup.wait_window()
        
        # Restore main window after popup closes
        if main_window_state == 'normal':
            self.root.deiconify()
            self.root.lift()
        elif main_window_state == 'zoomed':
            self.root.deiconify()
            self.root.state('zoomed')
            self.root.lift()
        
        return popup_result
    
    def safe_typewrite(self, text):
        """Enhanced typing method that handles special characters and emoticons better"""
        if not text:
            return
            
        try:
            # Try normal typewrite first
            pyautogui.typewrite(text)
        except Exception as e:
            # If normal typewrite fails, try character by character
            print(f"Normal typewrite failed: {e}. Trying character by character...")
            for char in text:
                try:
                    if char == '\n':
                        # Handle newline with Enter key
                        pyautogui.press('enter')
                    elif char == '\t':
                        # Handle tab with Tab key
                        pyautogui.press('tab')
                    else:
                        # Try to type the character
                        pyautogui.typewrite(char)
                except Exception as char_error:
                    # If character can't be typed, try using clipboard
                    try:
                        import pyperclip
                        pyperclip.copy(char)
                        pyautogui.hotkey('ctrl', 'v')
                    except Exception as clipboard_error:
                        print(f"Could not type character '{char}': {char_error}, clipboard error: {clipboard_error}")
                        # Skip this character if all methods fail
                        continue
    
    def process_text_for_typing(self, text):
        """Process text to handle escape sequences and special characters"""
        if not text:
            return text
            
        # Handle common escape sequences
        processed_text = text.replace('\\n', '\n')  # New line
        processed_text = processed_text.replace('\\t', '\t')  # Tab
        processed_text = processed_text.replace('\\r', '\r')  # Carriage return
        processed_text = processed_text.replace('\\\\', '\\')  # Literal backslash
        
        return processed_text
    
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
            "Click", "Type Text", "Type Text Popup", "Delay", "Hotkey", "Scroll", "Drag", "Double Click", "Right Click", "HTTP Request", "Wait for Image"
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