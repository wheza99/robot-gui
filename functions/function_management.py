"""
Function management handlers for the automation GUI
"""
import json
import os
from tkinter import messagebox

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
        elif func_type == "Start Loop":
            loop_type = self.loop_type_combo.get()
            loop_count = self.loop_count_entry.get().strip()
            loop_delay = self.loop_delay_entry.get().strip()
            
            if not loop_type:
                messagebox.showwarning("Warning", "Pilih jenis loop!")
                return
            
            if not loop_count:
                messagebox.showwarning("Warning", "Masukkan jumlah loop!")
                return
            
            if not loop_delay:
                messagebox.showwarning("Warning", "Masukkan delay loop!")
                return
            
            try:
                loop_count_int = int(loop_count)
                loop_delay_float = float(loop_delay)
                
                if loop_count_int < 1:
                    messagebox.showwarning("Warning", "Jumlah loop harus minimal 1!")
                    return
                
                if loop_delay_float < 0:
                    messagebox.showwarning("Warning", "Delay loop tidak boleh negatif!")
                    return
                
            except ValueError:
                messagebox.showwarning("Warning", "Jumlah loop harus berupa angka dan delay harus berupa angka!")
                return
            
            parameter = json.dumps({
                "loop_type": loop_type,
                "loop_count": loop_count_int,
                "loop_delay": loop_delay_float
            })
        elif func_type == "End Loop":
            # End Loop doesn't need parameters
            parameter = ""
        
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
