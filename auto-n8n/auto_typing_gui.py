import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import threading

class SimpleGUI:
    pyautogui.click(1169, 551) # click docker
    pyautogui.click(87, 422) # click container sidebar
    pyautogui.click(1751, 222) # click add container

def main():
    root = tk.Tk()
    app = SimpleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()