"""
Treeview event handlers for the automation GUI
"""

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
