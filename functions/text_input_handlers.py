"""
Text input popup handlers for the automation GUI
"""
import tkinter as tk
from tkinter import ttk
import pyautogui

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
