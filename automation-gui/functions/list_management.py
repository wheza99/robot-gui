import tkinter as tk

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
