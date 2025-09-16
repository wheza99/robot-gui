import tkinter as tk
from tkinter import ttk, scrolledtext
import datetime

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple GUI - 10 Buttons & Log")
        self.root.geometry("600x500")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Simple GUI Application", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.LabelFrame(main_frame, text="Control Buttons", padding="10")
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Define button functions and their corresponding PyAutoGUI commands
        self.button_functions = [
            ("Click", "pyautogui.click(x, y)"),
            ("Type Text", "pyautogui.typewrite('text')"),
            ("Press Key", "pyautogui.press('key')"),
            ("Hotkey", "pyautogui.hotkey('ctrl', 'c')"),
            ("Scroll", "pyautogui.scroll(clicks)"),
            ("Drag", "pyautogui.drag(x, y, duration=1)"),
            ("Screenshot", "pyautogui.screenshot()"),
            ("Position", "pyautogui.position()"),
            ("Move Mouse", "pyautogui.moveTo(x, y)"),
            ("Double Click", "pyautogui.doubleClick(x, y)")
        ]
        
        # Create 10 buttons in 2 columns
        for i in range(10):
            row = i // 2
            col = i % 2
            function_name, command = self.button_functions[i]
            button = ttk.Button(buttons_frame, text=function_name, 
                              command=lambda cmd=command, name=function_name: self.button_clicked(name, cmd))
            button.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Configure buttons frame grid
        for i in range(2):
            buttons_frame.columnconfigure(i, weight=1)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, width=40, height=20, 
                                                 wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure log frame grid
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Clear log button
        clear_button = ttk.Button(log_frame, text="Clear Log", command=self.clear_log)
        clear_button.grid(row=1, column=0, pady=(10, 0))
        
        # Initial log message
        self.add_log("Application started successfully")
    
    def button_clicked(self, function_name, command):
        """Handle button click events"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] {function_name}: {command}"
        self.add_log(message)
    
    def add_log(self, message):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Auto scroll to bottom
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear all log messages"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.add_log("Log cleared")

def main():
    root = tk.Tk()
    app = SimpleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()