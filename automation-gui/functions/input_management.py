import tkinter as tk

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
