import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from pynput import keyboard
from functions.treeview_handlers import on_treeview_click
from functions.function_type_handlers import on_function_type_change
from functions.parameter_handlers import hide_all_parameters
from functions.screen_capture_handlers import capture_screen_region
from functions.text_input_handlers import show_text_input_popup
from functions.coordinate_handlers import capture_coordinates, capture_drag_coordinates
from functions.image_handlers import browse_image_file, update_image_preview, wait_for_image
from functions.text_handlers import safe_typewrite, process_text_for_typing
from functions.function_management import add_function
from functions.input_management import clear_inputs
from functions.list_management import update_functions_list
from functions.edit_management import edit_function
from functions.removal_management import remove_function
from functions.movement_management import move_up, move_down
from functions.clearing_management import clear_all
from functions.automation_control import start_automation, stop_automation
from functions.automation_execution import run_automation
from functions.config_management import save_config, load_config
from functions.variable_management import show_variable_manager

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
    
    # Import the capture_drag_coordinates method from the separate module
    capture_drag_coordinates = capture_drag_coordinates
    
    # Import the add_function method from the separate module
    add_function = add_function
    
    # Import the clear_inputs method from the separate module
    clear_inputs = clear_inputs
    
    # Import the update_functions_list method from the separate module
    update_functions_list = update_functions_list
    
    # Assign the imported edit_function
    edit_function = edit_function
    
    # Assign the imported remove_function
    remove_function = remove_function
    
    # Assign the imported move_up function
    move_up = move_up
    
    # Assign the imported move_down function
    move_down = move_down
    
    # Assign the imported clear_all function
    clear_all = clear_all
    
    # Assign the imported start_automation function
    start_automation = start_automation
    
    # Assign the imported stop_automation function
    stop_automation = stop_automation
    
    # Automation execution function
    run_automation = run_automation
    
    # Assign the imported save_config function
    save_config = save_config
    
    # Assign the imported load_config function
    load_config = load_config
    
    # Assign the imported show_variable_manager function
    show_variable_manager = show_variable_manager
    

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