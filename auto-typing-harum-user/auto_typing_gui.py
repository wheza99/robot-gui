import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pyautogui
import time
import threading

try:
    import pynput.mouse as mouse
except ImportError:
    print("Warning: pynput not installed. Dropdown coordinate capture may not work.")
    mouse = None

class AutoTypingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Typing GUI")
        self.root.geometry("800x600")
        
        # Data variables
        self.excel_data = None
        self.coordinates = {
            'submit': None
        }
        
        # Control variables
        self.is_running = False
        self.current_thread = None
        self.submit_delay = 1.0  # Default delay after submit in seconds
        
        # Field type selection for each column
        self.field_types = {}  # column_name -> 'text' or 'dropdown'
        self.dropdown_configs = {}  # column_name -> {field_coord, conditions: [{value, coord}]}
        
        # Custom columns with default values
        self.custom_columns = {}  # column_name -> {'type': 'text'/'dropdown', 'default_value': str, 'config': {}}
        
        # Pre-click button coordinates - list of {'coordinate': (x, y), 'delay': float}
        self.pre_click_enabled = tk.BooleanVar(value=False)
        self.pre_click_buttons = []
        
        self.coord_vars = {}
        
        self.setup_ui()
        self.fit_window_to_content()
    
    def fit_window_to_content(self):
        """Adjust window size to fit content"""
        # Update all pending geometry changes
        self.root.update_idletasks()
        
        # Get the required size of the scrollable frame
        self.scrollable_frame.update_idletasks()
        req_width = self.scrollable_frame.winfo_reqwidth() + 50  # Add padding for scrollbar
        req_height = self.scrollable_frame.winfo_reqheight() + 50  # Add padding
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Limit window size to 90% of screen size
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)
        
        # Set minimum size
        min_width = 600
        min_height = 400
        
        # Calculate final window size
        final_width = max(min_width, min(req_width, max_width))
        final_height = max(min_height, min(req_height, max_height))
        
        # Center window on screen
        x = (screen_width - final_width) // 2
        y = (screen_height - final_height) // 2
        
        # Set window geometry
        self.root.geometry(f"{final_width}x{final_height}+{x}+{y}")
        
        # Set minimum window size
        self.root.minsize(min_width, min_height)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def setup_ui(self):
        # Configure root grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Main frame inside scrollable frame
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main_frame grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
        
        # Pre-click button section
        preclick_frame = ttk.LabelFrame(main_frame, text="Pre-Click Button", padding="10")
        preclick_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Pre-click checkbox
        preclick_check = ttk.Checkbutton(preclick_frame, text="Aktifkan klik tombol sebelum input data", 
                                       variable=self.pre_click_enabled)
        preclick_check.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Add pre-click button controls
        add_preclick_frame = ttk.Frame(preclick_frame)
        add_preclick_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(add_preclick_frame, text="Delay (detik):").grid(row=0, column=0, sticky=tk.W, padx=(20, 5))
        self.preclick_delay_var = tk.StringVar(value="1.0")
        delay_entry = ttk.Entry(add_preclick_frame, textvariable=self.preclick_delay_var, width=8)
        delay_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(add_preclick_frame, text="Tambah Button", command=self.add_preclick_button).grid(row=0, column=2, padx=(5, 0))
        
        # Pre-click buttons list
        self.preclick_buttons_frame = ttk.Frame(preclick_frame)
        self.preclick_buttons_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Initialize pre-click buttons display
        self.refresh_preclick_buttons_display()
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Pilih File Excel/CSV", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60, state="readonly").grid(row=0, column=0, padx=(0, 10))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Coordinates section (will be populated after Excel file is loaded)
        self.coord_frame = ttk.LabelFrame(main_frame, text="Koordinat Input", padding="10")
        self.coord_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Show message to load file first
        self.coord_message = ttk.Label(self.coord_frame, text="Silakan pilih file Excel/CSV terlebih dahulu untuk melihat kolom yang tersedia")
        self.coord_message.grid(row=0, column=0, columnspan=3, pady=20)
        
        # Custom columns section
        custom_frame = ttk.LabelFrame(main_frame, text="Custom Columns", padding="10")
        custom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Row range section
        range_frame = ttk.LabelFrame(main_frame, text="Range Baris untuk Diproses", padding="10")
        range_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(range_frame, text="Dari baris:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_row_var = tk.StringVar(value="1")
        start_row_entry = ttk.Entry(range_frame, textvariable=self.start_row_var, width=10)
        start_row_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(range_frame, text="Sampai baris:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_row_var = tk.StringVar(value="")
        end_row_entry = ttk.Entry(range_frame, textvariable=self.end_row_var, width=10)
        end_row_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(range_frame, text="(kosongkan 'Sampai baris' untuk memproses sampai akhir)").grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Submit Button section
        submit_frame = ttk.LabelFrame(main_frame, text="Submit", padding="10")
        submit_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Submit button coordinate
        ttk.Label(submit_frame, text="Submit Button:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.coordinates['submit'] = None
        submit_var = tk.StringVar()
        self.coord_vars['submit'] = submit_var
        ttk.Entry(submit_frame, textvariable=submit_var, width=15, state="readonly").grid(row=0, column=1, padx=(0, 5))
        ttk.Button(submit_frame, text="Set Submit", 
                  command=lambda: self.set_coordinate('submit')).grid(row=0, column=2, padx=(0, 5))
        
        # Delay setting
        ttk.Label(submit_frame, text="Delay setelah Submit (detik):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.delay_var = tk.StringVar(value="1.0")
        delay_entry = ttk.Entry(submit_frame, textvariable=self.delay_var, width=10)
        delay_entry.grid(row=1, column=1, padx=(0, 10), pady=(10, 0))
        
        # Add custom column controls
        add_custom_frame = ttk.Frame(custom_frame)
        add_custom_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(add_custom_frame, text="Column Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.custom_column_name_var = tk.StringVar()
        custom_name_entry = ttk.Entry(add_custom_frame, textvariable=self.custom_column_name_var, width=15)
        custom_name_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(add_custom_frame, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.custom_column_type_var = tk.StringVar(value="text")
        custom_type_combo = ttk.Combobox(add_custom_frame, textvariable=self.custom_column_type_var, 
                                       values=["text", "dropdown"], state="readonly", width=10)
        custom_type_combo.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(add_custom_frame, text="Default Value:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.custom_column_default_var = tk.StringVar()
        custom_default_entry = ttk.Entry(add_custom_frame, textvariable=self.custom_column_default_var, width=15)
        custom_default_entry.grid(row=0, column=5, padx=(0, 10))
        
        ttk.Button(add_custom_frame, text="Add Column", command=self.add_custom_column).grid(row=0, column=6, padx=(5, 0))
        
        # Custom columns list
        self.custom_columns_frame = ttk.Frame(custom_frame)
        self.custom_columns_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Initialize custom columns display
        self.refresh_custom_columns_display()
        

        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        self.start_button = ttk.Button(control_frame, text="Start Auto Typing", command=self.start_auto_typing)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_auto_typing, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Siap")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_file(self):
        """Browse and select Excel or CSV file"""
        file_path = filedialog.askopenfilename(
            title="Pilih File Excel atau CSV",
            filetypes=[
                ("All supported files", "*.xlsx *.xls *.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.load_data_file(file_path)
    
    def load_data_file(self, file_path):
        """Load data from Excel or CSV file"""
        try:
            # Detect file extension and load accordingly
            file_extension = file_path.lower().split('.')[-1]
            
            # Read all columns as strings to preserve leading zeros and formatting
            
            if file_extension == 'csv':
                # Read CSV with string dtype for phone/ID columns
                self.excel_data = pd.read_csv(file_path, dtype=str)
                file_type = "CSV"
            elif file_extension in ['xlsx', 'xls']:
                # Read Excel with string dtype for phone/ID columns
                self.excel_data = pd.read_excel(file_path, dtype=str)
                file_type = "Excel"
            else:
                raise ValueError(f"Format file tidak didukung: {file_extension}")
            
            # Convert NaN values to empty strings
            self.excel_data = self.excel_data.fillna('')
            
            messagebox.showinfo("Sukses", f"File {file_type} berhasil dimuat! {len(self.excel_data)} baris data ditemukan.")
            self.status_var.set(f"File {file_type} dimuat: {len(self.excel_data)} baris")
            
            # Set default row range
            self.start_row_var.set("1")
            self.end_row_var.set(str(len(self.excel_data)))
            
            # Create coordinate fields based on data columns
            self.create_coordinate_fields()
            
            # Adjust window size to fit new content
            self.root.after(100, self.fit_window_to_content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat file: {str(e)}")
    
    def create_coordinate_fields(self):
        """Create coordinate input fields based on data columns"""
        # Clear existing coordinate widgets
        for widget in self.coord_frame.winfo_children():
            widget.destroy()
        
        # Preserve submit coordinate and coord_var when resetting
        submit_coord = self.coordinates.get('submit')
        submit_coord_var = self.coord_vars.get('submit')
        
        # Reset coordinates but keep submit
        self.coordinates = {'submit': submit_coord}
            
        self.coord_vars = {}
        if submit_coord_var is not None:
            self.coord_vars['submit'] = submit_coord_var
            
        self.field_types = {}  # Store field type (text/dropdown)
        self.dropdown_configs = {}  # Store dropdown configurations
        self.field_enabled = {}  # Store which fields are enabled/disabled
        
        # Create fields for each data column
        row_index = 0
        for column in self.excel_data.columns:
            # Create safe key name for coordinate storage
            safe_key = column.lower().replace(' ', '_').replace('-', '_')
            
            # Add to coordinates dictionary
            self.coordinates[safe_key] = None
            self.field_types[safe_key] = 'text'  # Default to text
            self.dropdown_configs[safe_key] = {}
            
            # Enable/disable checkbox (default enabled)
            enabled_var = tk.BooleanVar(value=True)
            self.field_enabled[safe_key] = enabled_var
            ttk.Checkbutton(self.coord_frame, variable=enabled_var, 
                           command=lambda k=safe_key: self.on_field_enable_change(k)).grid(row=row_index, column=0, padx=(0, 5))
            
            # Create UI elements
            ttk.Label(self.coord_frame, text=f"{column}:").grid(row=row_index, column=1, sticky=tk.W, padx=(0, 10))
            
            # Field type selection
            type_var = tk.StringVar(value='text')
            self.field_types[safe_key + '_var'] = type_var
            type_combo = ttk.Combobox(self.coord_frame, textvariable=type_var, values=['text', 'dropdown'], 
                                    state="readonly", width=10)
            type_combo.grid(row=row_index, column=2, padx=(0, 5))
            type_combo.bind('<<ComboboxSelected>>', lambda e, k=safe_key: self.on_field_type_change(k))
            
            # Coordinate input
            var = tk.StringVar()
            self.coord_vars[safe_key] = var
            coord_entry = ttk.Entry(self.coord_frame, textvariable=var, width=15, state="readonly")
            coord_entry.grid(row=row_index, column=3, padx=(0, 5))
            
            # Set coordinate button
            set_btn = ttk.Button(self.coord_frame, text="Set Koordinat", 
                               command=lambda k=safe_key: self.set_coordinate(k))
            set_btn.grid(row=row_index, column=4, padx=(0, 5))
            
            # Config button for dropdown (initially hidden)
            config_btn = ttk.Button(self.coord_frame, text="Config Dropdown", 
                                  command=lambda k=safe_key: self.config_dropdown(k))
            config_btn.grid(row=row_index, column=5, padx=(0, 5))
            config_btn.grid_remove()  # Hide initially
            
            # Store UI elements for enable/disable functionality
            self.field_types[safe_key + '_var'] = type_var
            self.field_types[safe_key + '_combo'] = type_combo
            self.field_types[safe_key + '_entry'] = coord_entry
            self.field_types[safe_key + '_set_btn'] = set_btn
            self.field_types[safe_key + '_config_btn'] = config_btn
            
            row_index += 1
        

        
        # Submit button coordinate will be in Submit Button section
    
    def on_field_enable_change(self, field_key):
        """Handle field enable/disable change"""
        enabled = self.field_enabled[field_key].get()
        
        # Get UI elements
        type_combo = self.field_types[field_key + '_combo']
        coord_entry = self.field_types[field_key + '_entry']
        set_btn = self.field_types[field_key + '_set_btn']
        config_btn = self.field_types[field_key + '_config_btn']
        
        if enabled:
            # Enable all elements
            type_combo.config(state="readonly")
            set_btn.config(state="normal")
            # Show config button if dropdown type
            if self.field_types[field_key] == 'dropdown':
                config_btn.grid()
            else:
                config_btn.grid_remove()
        else:
            # Disable all elements
            type_combo.config(state="disabled")
            set_btn.config(state="disabled")
            config_btn.grid_remove()
    
    def on_field_type_change(self, field_key):
        """Handle field type change between text and dropdown"""
        type_var = self.field_types[field_key + '_var']
        config_btn = self.field_types[field_key + '_config_btn']
        enabled = self.field_enabled[field_key].get()
        
        if type_var.get() == 'dropdown':
            self.field_types[field_key] = 'dropdown'
            if enabled:  # Only show if field is enabled
                config_btn.grid()  # Show config button
        else:
            config_btn.grid_remove()  # Hide config button
            self.field_types[field_key] = 'text'
            self.dropdown_configs[field_key] = {}  # Clear dropdown config
    
    def add_custom_column(self):
        """Add a custom column with default value"""
        column_name = self.custom_column_name_var.get().strip()
        column_type = self.custom_column_type_var.get()
        default_value = self.custom_column_default_var.get().strip()
        
        if not column_name:
            messagebox.showerror("Error", "Please enter a column name")
            return
        
        if column_name in self.custom_columns:
            messagebox.showerror("Error", f"Column '{column_name}' already exists")
            return
        
        # Add to custom columns
        self.custom_columns[column_name] = {
            'type': column_type,
            'default_value': default_value,
            'config': {}
        }
        
        # Clear input fields
        self.custom_column_name_var.set("")
        self.custom_column_default_var.set("")
        
        # Refresh custom columns display
        self.refresh_custom_columns_display()
        
        messagebox.showinfo("Success", f"Custom column '{column_name}' added successfully")
    
    def refresh_custom_columns_display(self):
        """Refresh the display of custom columns"""
        # Clear existing widgets
        for widget in self.custom_columns_frame.winfo_children():
            widget.destroy()
        
        if not self.custom_columns:
            ttk.Label(self.custom_columns_frame, text="No custom columns added yet", 
                     foreground="gray").pack(pady=5)
            return
        
        # Create header
        header_frame = ttk.Frame(self.custom_columns_frame)
        header_frame.pack(fill='x', pady=(0, 5))
        
        # Configure column weights for proper alignment
        header_frame.columnconfigure(0, weight=1, minsize=120)
        header_frame.columnconfigure(1, weight=0, minsize=80)
        header_frame.columnconfigure(2, weight=1, minsize=100)
        header_frame.columnconfigure(3, weight=0, minsize=100)
        header_frame.columnconfigure(4, weight=0, minsize=120)
        
        ttk.Label(header_frame, text="Column Name", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="Type", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="Default Value", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="Koordinat", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        ttk.Label(header_frame, text="Actions", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=4, sticky=tk.W)
        
        # Create entries for each custom column
        for i, (column_name, config) in enumerate(self.custom_columns.items()):
            row_frame = ttk.Frame(self.custom_columns_frame)
            row_frame.pack(fill='x', pady=2)
            
            # Configure column weights same as header for alignment
            row_frame.columnconfigure(0, weight=1, minsize=120)
            row_frame.columnconfigure(1, weight=0, minsize=80)
            row_frame.columnconfigure(2, weight=1, minsize=100)
            row_frame.columnconfigure(3, weight=0, minsize=100)
            row_frame.columnconfigure(4, weight=0, minsize=120)
            
            ttk.Label(row_frame, text=column_name).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            ttk.Label(row_frame, text=config['type']).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
            ttk.Label(row_frame, text=config['default_value'] or "(empty)", 
                     foreground="gray" if not config['default_value'] else "black").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
            
            # Coordinate display
            coord_key = f"custom_{column_name}"
            coord_text = ""
            if coord_key in self.coordinates and self.coordinates[coord_key]:
                coord_text = str(self.coordinates[coord_key])
            
            coord_var = tk.StringVar(value=coord_text)
            if coord_key not in self.coord_vars:
                self.coord_vars[coord_key] = coord_var
            else:
                self.coord_vars[coord_key].set(coord_text)
            
            ttk.Entry(row_frame, textvariable=self.coord_vars[coord_key], width=12, state="readonly").grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
            
            # Action buttons
            action_frame = ttk.Frame(row_frame)
            action_frame.grid(row=0, column=4, sticky=tk.W)
            
            if config['type'] == 'dropdown':
                ttk.Button(action_frame, text="Config", 
                          command=lambda cn=column_name: self.config_custom_dropdown(cn)).pack(side='left', padx=(0, 5))
            
            ttk.Button(action_frame, text="Set Coord", 
                      command=lambda cn=column_name: self.set_custom_coordinate(cn)).pack(side='left', padx=(0, 5))
            ttk.Button(action_frame, text="Remove", 
                       command=lambda cn=column_name: self.remove_custom_column(cn)).pack(side='left')
    
    def config_custom_dropdown(self, column_name):
        """Configure dropdown for custom column"""
        # Use the same dropdown config window as regular columns
        self.config_dropdown(f"custom_{column_name}")
    
    def set_custom_coordinate(self, column_name):
        """Set coordinate for custom column input field"""
        coord_key = f"custom_{column_name}"
        messagebox.showinfo("Set Koordinat", 
                           f"Klik OK, lalu dalam 3 detik arahkan mouse ke posisi {column_name} dan jangan gerakkan mouse!")
        
        self.root.after(3000, lambda: self.capture_custom_coordinate(column_name))
    
    def capture_custom_coordinate(self, column_name):
        """Capture mouse coordinate for custom column"""
        coord_key = f"custom_{column_name}"
        x, y = pyautogui.position()
        self.coordinates[coord_key] = f"{x},{y}"
        
        # Update coordinate display if variable exists
        if coord_key in self.coord_vars:
            self.coord_vars[coord_key].set(f"{x},{y}")
        
        messagebox.showinfo("Koordinat Tersimpan", f"Koordinat {column_name}: ({x}, {y})")
        
        # Refresh display to show updated coordinate
        self.refresh_custom_columns_display()
    
    def remove_custom_column(self, column_name):
        """Remove a custom column"""
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove column '{column_name}'?"):
            # Remove from custom columns
            del self.custom_columns[column_name]
            
            # Remove coordinates if exists
            coord_key = f"custom_{column_name}"
            if coord_key in self.coordinates:
                del self.coordinates[coord_key]
            
            # Remove dropdown config if exists
            if coord_key in self.dropdown_configs:
                del self.dropdown_configs[coord_key]
            
            # Refresh display
            self.refresh_custom_columns_display()
            
            messagebox.showinfo("Success", f"Column '{column_name}' removed successfully")
    
    def add_preclick_button(self):
        """Add a new pre-click button"""
        try:
            delay = float(self.preclick_delay_var.get())
            if delay < 0:
                raise ValueError("Delay tidak boleh negatif")
        except ValueError as e:
            messagebox.showerror("Error", f"Nilai delay tidak valid: {str(e)}")
            return
        
        messagebox.showinfo("Set Koordinat", 
                           "Klik OK, lalu dalam 3 detik arahkan mouse ke posisi tombol dan jangan gerakkan mouse!")
        
        self.root.after(3000, lambda: self.capture_preclick_coordinate(delay))
    
    def capture_preclick_coordinate(self, delay):
        """Capture coordinate for pre-click button"""
        x, y = pyautogui.position()
        button_data = {
            'coordinate': (x, y),
            'delay': delay
        }
        self.pre_click_buttons.append(button_data)
        self.refresh_preclick_buttons_display()
        messagebox.showinfo("Koordinat Tersimpan", f"Pre-click button ditambahkan: ({x}, {y}) dengan delay {delay}s")
    
    def refresh_preclick_buttons_display(self):
        """Refresh the display of pre-click buttons list"""
        # Clear existing widgets
        for widget in self.preclick_buttons_frame.winfo_children():
            widget.destroy()
        
        if not self.pre_click_buttons:
            ttk.Label(self.preclick_buttons_frame, text="Belum ada pre-click button", 
                     foreground="gray").grid(row=0, column=0, pady=5)
            return
        
        # Header
        ttk.Label(self.preclick_buttons_frame, text="No.", font=('TkDefaultFont', 8, 'bold')).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Label(self.preclick_buttons_frame, text="Koordinat", font=('TkDefaultFont', 8, 'bold')).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Label(self.preclick_buttons_frame, text="Delay (s)", font=('TkDefaultFont', 8, 'bold')).grid(row=0, column=2, padx=5, sticky=tk.W)
        ttk.Label(self.preclick_buttons_frame, text="Aksi", font=('TkDefaultFont', 8, 'bold')).grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # List buttons
        for i, button_data in enumerate(self.pre_click_buttons):
            row = i + 1
            coord = button_data['coordinate']
            delay = button_data['delay']
            
            ttk.Label(self.preclick_buttons_frame, text=str(i + 1)).grid(row=row, column=0, padx=5, sticky=tk.W)
            ttk.Label(self.preclick_buttons_frame, text=f"({coord[0]}, {coord[1]})").grid(row=row, column=1, padx=5, sticky=tk.W)
            ttk.Label(self.preclick_buttons_frame, text=str(delay)).grid(row=row, column=2, padx=5, sticky=tk.W)
            
            # Remove button
            remove_btn = ttk.Button(self.preclick_buttons_frame, text="Hapus", 
                                  command=lambda idx=i: self.remove_preclick_button(idx))
            remove_btn.grid(row=row, column=3, padx=5, sticky=tk.W)
    
    def remove_preclick_button(self, index):
        """Remove a pre-click button by index"""
        if 0 <= index < len(self.pre_click_buttons):
            removed = self.pre_click_buttons.pop(index)
            self.refresh_preclick_buttons_display()
            coord = removed['coordinate']
            messagebox.showinfo("Button Dihapus", f"Pre-click button ({coord[0]}, {coord[1]}) telah dihapus")
        else:
            messagebox.showerror("Error", "Index button tidak valid")
    
    def config_dropdown(self, field_key):
        """Open dropdown configuration window"""
        config_window = tk.Toplevel(self.root)
        config_window.title(f"Konfigurasi Dropdown - {field_key}")
        config_window.geometry("500x400")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Instructions
        ttk.Label(config_window, text="Atur kondisi nilai dan koordinat untuk dropdown:", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Frame for conditions
        conditions_frame = ttk.Frame(config_window)
        conditions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Get existing config or create new
        current_config = self.dropdown_configs.get(field_key, {})
        
        # Store condition entries
        condition_entries = []
        
        def add_condition_row(value="", coord=""):
            row_frame = ttk.Frame(conditions_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text="Jika nilai:", width=10).pack(side=tk.LEFT, padx=(0, 5))
            value_entry = ttk.Entry(row_frame, width=15)
            value_entry.pack(side=tk.LEFT, padx=(0, 10))
            value_entry.insert(0, value)
            
            ttk.Label(row_frame, text="Klik koordinat:", width=12).pack(side=tk.LEFT, padx=(0, 5))
            coord_var = tk.StringVar(value=coord)
            coord_entry = ttk.Entry(row_frame, textvariable=coord_var, width=15, state="readonly")
            coord_entry.pack(side=tk.LEFT, padx=(0, 5))
            
            def set_coord():
                self.capture_dropdown_coordinate(coord_var)
            
            ttk.Button(row_frame, text="Set", command=set_coord).pack(side=tk.LEFT, padx=(0, 5))
            
            def remove_row():
                row_frame.destroy()
                condition_entries.remove((value_entry, coord_var))
            
            ttk.Button(row_frame, text="Hapus", command=remove_row).pack(side=tk.LEFT)
            
            condition_entries.append((value_entry, coord_var))
        
        # Add existing conditions
        for value, coord in current_config.items():
            add_condition_row(value, coord)
        
        # Add empty row if no existing conditions
        if not current_config:
            add_condition_row()
        
        # Buttons frame
        buttons_frame = ttk.Frame(config_window)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(buttons_frame, text="Tambah Kondisi", 
                  command=lambda: add_condition_row()).pack(side=tk.LEFT, padx=(0, 10))
        
        def save_config():
            # Save all conditions
            new_config = {}
            for value_entry, coord_var in condition_entries:
                value = value_entry.get().strip()
                coord = coord_var.get().strip()
                if value and coord:
                    new_config[value] = coord
            
            self.dropdown_configs[field_key] = new_config
            config_window.destroy()
            messagebox.showinfo("Sukses", f"Konfigurasi dropdown untuk {field_key} berhasil disimpan!")
        
        ttk.Button(buttons_frame, text="Simpan", command=save_config).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(buttons_frame, text="Batal", command=config_window.destroy).pack(side=tk.RIGHT)
    
    def capture_dropdown_coordinate(self, coord_var):
        """Capture coordinate for dropdown option"""
        messagebox.showinfo("Set Koordinat", 
                           "Klik OK, lalu dalam 3 detik arahkan mouse ke posisi dropdown dan jangan gerakkan mouse!")
        
        self.root.after(3000, lambda: self.capture_dropdown_position(coord_var))
    
    def capture_dropdown_position(self, coord_var):
        """Capture mouse position for dropdown coordinate"""
        x, y = pyautogui.position()
        coord_var.set(f"{x},{y}")
        messagebox.showinfo("Koordinat Tersimpan", f"Koordinat dropdown tersimpan: ({x}, {y})")
    
    def set_coordinate(self, field_name):
        """Set coordinate for a specific field"""
        messagebox.showinfo("Set Koordinat", 
                           f"Klik OK, lalu dalam 3 detik arahkan mouse ke posisi {field_name} dan jangan gerakkan mouse!")
        
        self.root.after(3000, lambda: self.capture_coordinate(field_name))
    
    def capture_coordinate(self, field_name):
        """Capture mouse coordinate"""
        x, y = pyautogui.position()
        self.coordinates[field_name] = (x, y)
        self.coord_vars[field_name].set(f"{x}, {y}")
        messagebox.showinfo("Koordinat Tersimpan", f"Koordinat {field_name}: ({x}, {y})")
    
    def start_auto_typing(self):
        """Start auto typing process"""
        if self.excel_data is None:
            messagebox.showerror("Error", "Silakan pilih file Excel/CSV terlebih dahulu")
            return
        
        # Validate and set delay value
        try:
            delay_value = float(self.delay_var.get())
            if delay_value < 0:
                raise ValueError("Delay tidak boleh negatif")
            self.submit_delay = delay_value
        except ValueError as e:
            messagebox.showerror("Error", f"Nilai delay tidak valid: {str(e)}")
            return
        
        # Check if all required coordinates are set
        required_coords = ['submit']  # Submit is always required
        
        # Add coordinates for each enabled data column only
        for column in self.excel_data.columns:
            safe_key = column.lower().replace(' ', '_').replace('-', '_')
            # Only check coordinates for enabled fields
            if safe_key in self.field_enabled and self.field_enabled[safe_key].get():
                required_coords.append(safe_key)
        
        # Add custom columns (always required since they don't have enable/disable)
        for column_name in self.custom_columns.keys():
            coord_key = f"custom_{column_name}"
            required_coords.append(coord_key)
        
        missing_coords = [coord for coord in required_coords if self.coordinates.get(coord) is None]
        if missing_coords:
            messagebox.showerror("Error", f"Koordinat belum diset: {', '.join(missing_coords)}")
            return
        
        # Validate pre-click buttons if enabled
        if self.pre_click_enabled.get() and not self.pre_click_buttons:
            messagebox.showerror("Error", "Pre-click button diaktifkan tetapi belum ada button yang ditambahkan")
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start auto typing in separate thread
        self.current_thread = threading.Thread(target=self.auto_type_process)
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def stop_auto_typing(self):
        """Stop auto typing process"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("Dihentikan")
        self.progress['value'] = 0
    
    def auto_type_process(self):
        """Main auto typing process"""
        try:
            # Get row range from user input
            try:
                start_row = int(self.start_row_var.get()) if self.start_row_var.get().strip() else 1
                end_row_input = self.end_row_var.get().strip()
                end_row = int(end_row_input) if end_row_input else len(self.excel_data)
                
                # Validate range
                if start_row < 1:
                    start_row = 1
                if end_row > len(self.excel_data):
                    end_row = len(self.excel_data)
                if start_row > end_row:
                    messagebox.showerror("Error", "Baris awal tidak boleh lebih besar dari baris akhir")
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Input baris harus berupa angka")
                return
            
            # Convert to 0-based index for pandas
            start_idx = start_row - 1
            end_idx = end_row - 1
            
            # Get subset of data based on row range
            data_subset = self.excel_data.iloc[start_idx:end_idx + 1]
            total_rows = len(data_subset)
            self.progress['maximum'] = total_rows
            
            for i, (index, row) in enumerate(data_subset.iterrows()):
                if not self.is_running:
                    break
                
                actual_row_number = start_row + i
                self.status_var.set(f"Memproses baris {actual_row_number} ({i + 1} dari {total_rows})")
                
                # Click pre-click buttons if enabled
                if self.pre_click_enabled.get() and self.pre_click_buttons:
                    try:
                        for i, button_data in enumerate(self.pre_click_buttons):
                            if not self.is_running:
                                break
                            
                            coord = button_data['coordinate']
                            delay = button_data['delay']
                            
                            pyautogui.click(coord[0], coord[1])
                            self.status_var.set(f"Pre-click button {i+1}/{len(self.pre_click_buttons)} - Baris {actual_row_number}")
                            time.sleep(delay)  # Wait with custom delay
                    except Exception as e:
                        messagebox.showerror("Error", f"Gagal mengklik pre-click button: {str(e)}")
                        break
                
                # Type each field dynamically based on data columns (only enabled fields)
                for column in self.excel_data.columns:
                    if not self.is_running:
                        break
                    
                    safe_key = column.lower().replace(' ', '_').replace('-', '_')
                    
                    # Skip if field is disabled
                    if safe_key in self.field_enabled and not self.field_enabled[safe_key].get():
                        continue
                    
                    field_type = self.field_types.get(safe_key, 'text')
                    
                    if field_type == 'dropdown':
                        # Handle dropdown field
                        self.handle_dropdown_field(safe_key, str(row[column]))
                    else:
                        # Handle text field
                        self.type_field(safe_key, str(row[column]))
                    
                    time.sleep(0.5)
                
                # Process custom columns with default values
                for column_name, config in self.custom_columns.items():
                    if not self.is_running:
                        break
                    
                    coord_key = f"custom_{column_name}"
                    default_value = config['default_value']
                    
                    if config['type'] == 'dropdown':
                        self.handle_dropdown_field(coord_key, default_value)
                    else:
                        # Handle as text field
                        self.type_field(coord_key, default_value)
                    
                    time.sleep(0.5)
                
                # Click submit button
                self.click_submit()
                time.sleep(self.submit_delay)  # Wait before next row (configurable delay)
                
                # Update progress
                self.progress['value'] = i + 1
                self.root.update_idletasks()
            
            if self.is_running:
                self.status_var.set("Selesai!")
                messagebox.showinfo("Selesai", "Auto typing selesai!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
        finally:
            self.stop_auto_typing()
    
    def type_field(self, field_name, value):
        """Type value at specified coordinate"""
        if not self.is_running:
            return
            
        coord = self.coordinates[field_name]
        if coord:
            # Parse coordinate string "x,y" to integers
            if isinstance(coord, str):
                try:
                    x, y = map(int, coord.split(','))
                except ValueError:
                    print(f"Invalid coordinate format for {field_name}: {coord}")
                    return
            else:
                x, y = coord
            
            pyautogui.click(x, y)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'a')  # Select all
            time.sleep(0.1)
            pyautogui.typewrite(value)
    
    def handle_dropdown_field(self, field_key, value):
        """Handle dropdown field selection based on configuration"""
        if not self.is_running:
            return
            
        try:
            # Get dropdown configuration for this field
            dropdown_config = self.dropdown_configs.get(field_key, {})
            
            if not dropdown_config:
                print(f"No dropdown configuration found for {field_key}")
                return
            
            # First click on the field coordinate to focus/open dropdown
            if self.coordinates.get(field_key):
                coord = self.coordinates[field_key]
                if isinstance(coord, tuple):
                    x, y = coord
                else:
                    x, y = map(int, coord.split(','))
                pyautogui.click(x, y)
                time.sleep(0.5)
            
            # Find matching value in configuration
            coord_to_click = None
            for config_value, coord_str in dropdown_config.items():
                if value.lower().strip() == config_value.lower().strip():
                    coord_to_click = coord_str
                    break
            
            # Click on the matching coordinate
            if coord_to_click:
                x, y = map(int, coord_to_click.split(','))
                pyautogui.click(x, y)
            else:
                print(f"No matching configuration found for value '{value}' in field '{field_key}'")
                
        except Exception as e:
            print(f"Error handling dropdown field {field_key}: {e}")
    

    
    def click_submit(self):
        """Click submit button"""
        if not self.is_running:
            return
            
        submit_coord = self.coordinates['submit']
        if submit_coord:
            # Parse coordinate string "x,y" to integers
            if isinstance(submit_coord, str):
                try:
                    x, y = map(int, submit_coord.split(','))
                except ValueError:
                    print(f"Invalid coordinate format for submit: {submit_coord}")
                    return
            else:
                x, y = submit_coord
            
            pyautogui.click(x, y)
            time.sleep(0.2)  # Brief pause after clicking submit

def main():
    root = tk.Tk()
    app = AutoTypingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()