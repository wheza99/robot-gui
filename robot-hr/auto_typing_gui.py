import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import threading

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Typing Robot - HR")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Create main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(main_frame, text="Robot HR Auto Typing", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description label
        desc_label = tk.Label(main_frame, 
                             text="Klik tombol di bawah untuk menjalankan auto typing\nuntuk filter salary minimum 3,000,000",
                             font=("Arial", 10), justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))
        
        # Run button
        self.run_button = tk.Button(main_frame, text="Jalankan Auto Typing", 
                                   command=self.start_auto_typing,
                                   font=("Arial", 12, "bold"),
                                   bg="#4CAF50", fg="white",
                                   width=20, height=2)
        self.run_button.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Siap untuk dijalankan", 
                                    font=("Arial", 10), fg="green")
        self.status_label.pack(pady=(10, 0))
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def start_auto_typing(self):
        """Start auto typing in a separate thread"""
        self.run_button.config(state="disabled", text="Sedang Berjalan...")
        self.status_label.config(text="Auto typing sedang berjalan...", fg="orange")
        
        # Start auto typing in separate thread to prevent GUI freeze
        thread = threading.Thread(target=self.run_auto_typing)
        thread.daemon = True
        thread.start()
    
    def run_auto_typing(self):
        """Execute the auto typing sequence"""
        try:
            # Give user 3 seconds to prepare
            for i in range(3, 0, -1):
                self.root.after(0, lambda i=i: self.status_label.config(
                    text=f"Mulai dalam {i} detik...", fg="orange"))
                time.sleep(1)
            
            # Execute the auto typing sequence
            pyautogui.click(787, 751)   # lihat terhubung
            time.sleep(0.5)
            pyautogui.click(1580, 725)  # buka filter
            time.sleep(0.5)
            pyautogui.click(1900, 946)  # scroll down
            time.sleep(0.5)
            pyautogui.click(1520, 657)  # input min salary 
            time.sleep(0.5)
            pyautogui.typewrite('3000000')  # min salary 
            time.sleep(0.5)
            pyautogui.click(1779, 998)  # terapkan
            time.sleep(0.5)
            pyautogui.click(49, 781)    # select all
            
            # Update status on completion
            self.root.after(0, self.on_completion_success)
            
        except Exception as e:
            # Handle errors
            self.root.after(0, lambda: self.on_completion_error(str(e)))
    
    def on_completion_success(self):
        """Called when auto typing completes successfully"""
        self.run_button.config(state="normal", text="Jalankan Auto Typing")
        self.status_label.config(text="Auto typing selesai!", fg="green")
        messagebox.showinfo("Sukses", "Auto typing berhasil dijalankan!")
    
    def on_completion_error(self, error_msg):
        """Called when auto typing encounters an error"""
        self.run_button.config(state="normal", text="Jalankan Auto Typing")
        self.status_label.config(text="Terjadi kesalahan", fg="red")
        messagebox.showerror("Error", f"Terjadi kesalahan: {error_msg}")


def main():
    root = tk.Tk()
    app = SimpleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()