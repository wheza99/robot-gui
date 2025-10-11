"""
Parameter visibility handlers for the automation GUI
"""

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
        self.image_preview_label, self.image_preview,
        self.variable_name_label, self.variable_name_entry, self.variable_value_label, self.variable_value_entry,
        self.variable_source_label, self.variable_source_combo
    ]
    for widget in widgets_to_hide:
        widget.grid_remove()
