import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import json
import re


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
    edit_window.geometry("600x700")
    edit_window.resizable(True, True)
    edit_window.grab_set()  # Make dialog modal
    
    # Center the window
    edit_window.transient(self.root)
    
    # Create main frame with scrollbar
    main_canvas = tk.Canvas(edit_window)
    scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=main_canvas.yview)
    scrollable_frame = ttk.Frame(main_canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack canvas and scrollbar
    main_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Function name
    ttk.Label(scrollable_frame, text="Nama Fungsi:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    name_var = tk.StringVar(value=func_data.get("name", ""))
    name_entry = ttk.Entry(scrollable_frame, textvariable=name_var, width=30)
    name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
    
    # Function type
    ttk.Label(scrollable_frame, text="Jenis Fungsi:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    type_var = tk.StringVar(value=func_data["type"])
    type_combo = ttk.Combobox(scrollable_frame, textvariable=type_var, values=[
        "Click", "Type Text", "Type Text Popup", "Delay", "Hotkey", "Scroll", "Drag", "Double Click", "Right Click", "HTTP Request", "Wait for Image", "Set Variable", "Get Variable", "Start Loop"
    ], state="readonly", width=27)
    type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
    
    # Coordinates frame
    coord_frame = ttk.LabelFrame(scrollable_frame, text="Koordinat")
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
    param_frame = ttk.LabelFrame(scrollable_frame, text="Parameter")
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
    
    # Loop parameters (for Start Loop function)
    loop_count_label = ttk.Label(param_frame, text="Loop Count:")
    loop_count_var = tk.StringVar()
    loop_count_entry = ttk.Entry(param_frame, textvariable=loop_count_var, width=10)
    
    loop_delay_label = ttk.Label(param_frame, text="Loop Delay (s):")
    loop_delay_var = tk.StringVar()
    loop_delay_entry = ttk.Entry(param_frame, textvariable=loop_delay_var, width=10)
    
    loop_type_label = ttk.Label(param_frame, text="Loop Type:")
    loop_type_var = tk.StringVar()
    loop_type_combo = ttk.Combobox(param_frame, textvariable=loop_type_var, values=[
        "Fixed Count", "Infinite", "Until Condition"
    ], state="readonly", width=15)
    
    # Variable parameters (for Set Variable and Get Variable functions)
    variable_name_label = ttk.Label(param_frame, text="Variable Name:")
    variable_name_var = tk.StringVar()
    variable_name_entry = ttk.Entry(param_frame, textvariable=variable_name_var, width=20)
    
    variable_value_label = ttk.Label(param_frame, text="Variable Value:")
    variable_value_var = tk.StringVar()
    variable_value_entry = ttk.Entry(param_frame, textvariable=variable_value_var, width=30)
    
    variable_source_label = ttk.Label(param_frame, text="Value Source:")
    variable_source_var = tk.StringVar()
    variable_source_combo = ttk.Combobox(param_frame, textvariable=variable_source_var, values=[
        "Manual Input", "Clipboard", "Current Time", "Random Number", "Screen Text (OCR)", "Last Click Position"
    ], state="readonly", width=20)
    
    # Wait for Image parameters
    image_label = ttk.Label(param_frame, text="Template Image:")
    image_path_var = tk.StringVar()
    image_path_entry = ttk.Entry(param_frame, textvariable=image_path_var, width=40)
    image_browse_btn = ttk.Button(param_frame, text="Browse", command=lambda: browse_image_file_edit())
    
    image_threshold_label = ttk.Label(param_frame, text="Threshold:")
    image_threshold_var = tk.StringVar()
    image_threshold_entry = ttk.Entry(param_frame, textvariable=image_threshold_var, width=8)
    
    image_timeout_label = ttk.Label(param_frame, text="Timeout (s):")
    image_timeout_var = tk.StringVar()
    image_timeout_entry = ttk.Entry(param_frame, textvariable=image_timeout_var, width=8)
    
    def browse_image_file_edit():
        """Browse for image file in edit dialog"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Pilih Template Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if filename:
            image_path_var.set(filename)
    
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
        match = re.search(r'to \((\d+), (\d+)\)', current_param)
        if match:
            drag_x_var.set(match.group(1))
            drag_y_var.set(match.group(2))
    elif func_data["type"] == "HTTP Request":
        # Parse HTTP Request parameter (JSON format)
        try:
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
    elif func_data["type"] == "Start Loop":
        # Parse Start Loop parameter (JSON format)
        try:
            loop_params = json.loads(current_param)
            loop_count_var.set(str(loop_params.get("loop_count", 1)))
            loop_delay_var.set(str(loop_params.get("loop_delay", 1.0)))
            loop_type_var.set(loop_params.get("loop_type", "Fixed Count"))
        except (json.JSONDecodeError, KeyError):
            # Set default values if parsing fails
            loop_count_var.set("1")
            loop_delay_var.set("1.0")
            loop_type_var.set("Fixed Count")
    elif func_data["type"] == "Set Variable":
        # Parse Set Variable parameter (JSON format)
        try:
            var_params = json.loads(current_param)
            variable_name_var.set(var_params.get("name", ""))
            variable_value_var.set(var_params.get("value", ""))
            variable_source_var.set(var_params.get("source", "Manual Input"))
        except (json.JSONDecodeError, KeyError):
            # Set default values if parsing fails
            variable_name_var.set("")
            variable_value_var.set("")
            variable_source_var.set("Manual Input")
    elif func_data["type"] == "Get Variable":
        # Parse Get Variable parameter (just variable name)
        variable_name_var.set(current_param)
    elif func_data["type"] == "Wait for Image":
        # Parse Wait for Image parameter (JSON format)
        try:
            image_params = json.loads(current_param)
            image_path_var.set(image_params.get("image_path", ""))
            image_threshold_var.set(str(image_params.get("threshold", 0.8)))
            image_timeout_var.set(str(image_params.get("timeout", 30)))
        except (json.JSONDecodeError, KeyError):
            # Set default values if parsing fails
            image_path_var.set("")
            image_threshold_var.set("0.8")
            image_timeout_var.set("30")
    
    # Status label for capture feedback (moved to end of function)
    # Will be created after scrollable_frame is set up
    
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
                      http_loop_label, http_loop_entry, http_loop_delay_label, http_loop_delay_entry,
                      loop_count_label, loop_count_entry, loop_delay_label, loop_delay_entry,
                      loop_type_label, loop_type_combo, variable_name_label, variable_name_entry,
                      variable_value_label, variable_value_entry, variable_source_label, variable_source_combo,
                      image_label, image_path_entry, image_browse_btn, image_threshold_label,
                      image_threshold_entry, image_timeout_label, image_timeout_entry]:
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
        elif func_type == "Start Loop":
            loop_count_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            loop_count_entry.grid(row=0, column=1, padx=5, pady=5)
            loop_delay_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 5), pady=5)
            loop_delay_entry.grid(row=0, column=3, padx=5, pady=5)
            loop_type_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            loop_type_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        elif func_type == "Set Variable":
            variable_name_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            variable_name_entry.grid(row=0, column=1, padx=5, pady=5)
            variable_value_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 5), pady=5)
            variable_value_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)
            variable_source_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            variable_source_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        elif func_type == "Get Variable":
            variable_name_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            variable_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        elif func_type == "Wait for Image":
            image_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            image_path_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
            image_browse_btn.grid(row=0, column=3, padx=(10, 5), pady=5)
            image_threshold_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            image_threshold_entry.grid(row=1, column=1, padx=5, pady=5)
            image_timeout_label.grid(row=1, column=2, sticky=tk.W, padx=(10, 5), pady=5)
            image_timeout_entry.grid(row=1, column=3, padx=5, pady=5)
    
    type_var.trace_add("write", update_coord_visibility)
    type_var.trace_add("write", update_param_visibility)
    update_coord_visibility()  # Initial call
    update_param_visibility()  # Initial call
    
    # Delay frame
    delay_frame = ttk.LabelFrame(scrollable_frame, text="Delay")
    delay_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
    
    ttk.Label(delay_frame, text="Delay setelah (detik):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    delay_var = tk.StringVar(value=str(func_data["delay"]))
    delay_entry = ttk.Entry(delay_frame, textvariable=delay_var, width=10)
    delay_entry.grid(row=0, column=1, padx=5, pady=5)
    
    # Enabled checkbox frame
    enabled_frame = ttk.LabelFrame(scrollable_frame, text="Status")
    enabled_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)
    
    enabled_var = tk.BooleanVar(value=func_data.get('enabled', True))
    enabled_checkbox = ttk.Checkbutton(enabled_frame, text="Aktifkan fungsi ini", variable=enabled_var)
    enabled_checkbox.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    # Buttons frame
    btn_frame = ttk.Frame(scrollable_frame)
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
                
                # Construct HTTP Request parameter as JSON
                parameter = json.dumps({
                    "url": url,
                    "method": method,
                    "headers": headers,
                    "body": body,
                    "loop_count": loop_count_int,
                    "loop_delay": loop_delay_float
                })
            elif func_type == "Start Loop":
                # Validate and construct Start Loop parameter
                loop_count_str = loop_count_var.get().strip()
                loop_delay_str = loop_delay_var.get().strip()
                loop_type_str = loop_type_var.get()
                
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
                    loop_delay_float = float(loop_delay_str) if loop_delay_str else 0.0
                    if loop_delay_float < 0:
                        messagebox.showerror("Error", "Loop delay harus berupa angka positif atau nol!")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Loop delay harus berupa angka!")
                    return
                
                # Construct Start Loop parameter as JSON
                parameter = json.dumps({
                    "count": loop_count_int,
                    "delay": loop_delay_float,
                    "type": loop_type_str
                })
            elif func_type == "Set Variable":
                # Validate and construct Set Variable parameter
                var_name = variable_name_var.get().strip()
                var_value = variable_value_var.get().strip()
                var_source = variable_source_var.get()
                
                if not var_name:
                    messagebox.showerror("Error", "Nama variabel tidak boleh kosong!")
                    return
                
                # Construct Set Variable parameter as JSON
                parameter = json.dumps({
                    "name": var_name,
                    "value": var_value,
                    "source": var_source
                })
            elif func_type == "Get Variable":
                # Validate and construct Get Variable parameter
                var_name = variable_name_var.get().strip()
                
                if not var_name:
                    messagebox.showerror("Error", "Nama variabel tidak boleh kosong!")
                    return
                
                # Construct Get Variable parameter as JSON
                parameter = json.dumps({
                    "name": var_name
                })
            elif func_type == "Wait for Image":
                # Validate and construct Wait for Image parameter
                image_path = image_path_var.get().strip()
                threshold_str = image_threshold_var.get().strip()
                timeout_str = image_timeout_var.get().strip()
                
                if not image_path:
                    messagebox.showerror("Error", "Path gambar tidak boleh kosong!")
                    return
                
                # Validate threshold
                try:
                    threshold_float = float(threshold_str) if threshold_str else 0.8
                    if threshold_float < 0 or threshold_float > 1:
                        messagebox.showerror("Error", "Threshold harus antara 0 dan 1!")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Threshold harus berupa angka!")
                    return
                
                # Validate timeout
                try:
                    timeout_int = int(timeout_str) if timeout_str else 10
                    if timeout_int <= 0:
                        messagebox.showerror("Error", "Timeout harus berupa angka positif!")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Timeout harus berupa angka!")
                    return
                
                # Construct Wait for Image parameter as JSON
                parameter = json.dumps({
                    "image_path": image_path,
                    "threshold": threshold_float,
                    "timeout": timeout_int
                })
            
            # Update the function data
            self.automation_functions[func_index] = {
                "name": new_name,
                "type": func_type,
                "x": new_x,
                "y": new_y,
                "parameter": parameter,
                "delay": float(new_delay),
                "enabled": enabled_var.get()
            }
            
            # Update the functions list display
            self.update_functions_list()
            
            # Close the edit window
            edit_window.destroy()
            
            messagebox.showinfo("Success", "Fungsi berhasil diupdate!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    
    def cancel_edit():
        """Cancel editing and close dialog"""
        edit_window.destroy()
    
    # Save and Cancel buttons
    save_btn = ttk.Button(btn_frame, text="Simpan", command=save_changes)
    save_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_btn = ttk.Button(btn_frame, text="Batal", command=cancel_edit)
    cancel_btn.pack(side=tk.LEFT)
    
    # Configure column weights for proper resizing
    scrollable_frame.columnconfigure(1, weight=1)
    param_frame.columnconfigure(1, weight=1)
    
    # Add status label for feedback
    status_label = ttk.Label(scrollable_frame, text="")
    status_label.grid(row=7, column=0, columnspan=2, pady=5)
