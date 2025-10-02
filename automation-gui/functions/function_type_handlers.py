"""
Function type change handlers for the automation GUI
"""
import tkinter as tk

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
    elif func_type == "Set Variable":
        # Row 0: Variable Name
        self.variable_name_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.variable_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Row 1: Value Source
        self.variable_source_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.variable_source_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # Row 2: Variable Value (only for Manual Input)
        self.variable_value_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.variable_value_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
    elif func_type == "Get Variable":
        # Row 0: Variable Name to retrieve
        self.variable_name_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.variable_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
