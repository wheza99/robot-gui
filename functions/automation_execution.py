"""
Automation Execution Module

This module contains the core automation execution functionality,
handling the sequential execution of all automation functions.
"""

import time
import json
import re
import datetime
import tkinter as tk
from tkinter import messagebox
import pyautogui
import pyperclip
import requests


def run_automation(self):
    """Execute all automation functions in sequence"""
    try:
        # Filter only enabled functions
        enabled_functions = [func for func in self.automation_functions if func.get('enabled', True)]
        total_functions = len(enabled_functions)
        
        if total_functions == 0:
            self.status_label.config(text="Tidak ada fungsi yang diaktifkan!")
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            return
        
        self.progress['maximum'] = total_functions
        
        for i, func in enumerate(enabled_functions):
            # Check for emergency stop or normal stop
            if not self.is_running or self.emergency_stop:
                break
            
            self.status_label.config(text=f"Menjalankan: {func.get('name', 'Unnamed')} ({i+1}/{total_functions})")
            self.root.update()
            
            # Execute function based on type
            if func['type'] == "Click":
                if func['x'] and func['y']:
                    pyautogui.click(func['x'], func['y'])
            
            elif func['type'] == "Double Click":
                if func['x'] and func['y']:
                    pyautogui.doubleClick(func['x'], func['y'])
            
            elif func['type'] == "Right Click":
                if func['x'] and func['y']:
                    pyautogui.rightClick(func['x'], func['y'])
            
            elif func['type'] == "Type Text":
                if func['parameter']:
                    processed_text = self.process_text_for_typing(func['parameter'])
                    self.safe_typewrite(processed_text)
            
            elif func['type'] == "Type Text Popup":
                # Show popup to get text input
                popup_result = self.show_text_input_popup(func.get('name', 'Fungsi'))
                if popup_result["confirmed"] and popup_result["text"]:
                    # Wait 2 seconds after OK is clicked before moving cursor
                    time.sleep(2)
                    
                    # Check if we should click at the original position first
                    if popup_result.get("click_before_type", True) and popup_result.get("click_position"):
                        # Move mouse back to original position and click
                        original_pos = popup_result["click_position"]
                        pyautogui.click(original_pos.x, original_pos.y)
                    
                    # Wait 1 second before typing
                    time.sleep(1)
                    # Process and type the entered text
                    processed_text = self.process_text_for_typing(popup_result["text"])
                    self.safe_typewrite(processed_text)
                elif not popup_result["confirmed"]:
                    # If cancelled, skip this function
                    continue
            
            elif func['type'] == "Hotkey":
                if func['parameter']:
                    keys = func['parameter'].replace(' ', '').split('+')
                    pyautogui.hotkey(*keys)
            
            elif func['type'] == "Delay":
                time.sleep(func['delay'])
                continue  # Skip the normal delay for this function
            
            elif func['type'] == "Scroll":
                if func['x'] and func['y']:
                    pyautogui.moveTo(func['x'], func['y'])  # Move mouse to position without clicking
                parts = func['parameter'].split()
                if len(parts) >= 2:
                    direction = parts[0]
                    amount = int(parts[1])
                    scroll_amount = amount if direction == "Up" else -amount
                    pyautogui.scroll(scroll_amount)
            
            elif func['type'] == "Drag":
                if func['x'] and func['y'] and func['parameter']:
                    # Extract target coordinates from parameter
                    coords = re.findall(r'\d+', func['parameter'])
                    if len(coords) >= 2:
                        target_x, target_y = int(coords[0]), int(coords[1])
                        # Move to start position first, then drag to target position
                        pyautogui.moveTo(func['x'], func['y'])
                        pyautogui.dragTo(target_x, target_y, duration=1, button='left')
            
            elif func['type'] == "HTTP Request":
                if func['parameter']:
                    try:
                        # Parse HTTP request parameters
                        http_params = json.loads(func['parameter'])
                        url = http_params.get('url', '')
                        method = http_params.get('method', 'GET').upper()
                        headers_str = http_params.get('headers', '{}')
                        body_str = http_params.get('body', '')
                        loop_count = http_params.get('loop_count', 1)
                        loop_delay = http_params.get('loop_delay', 1.0)
                        
                        # Parse headers and body JSON
                        headers = json.loads(headers_str) if headers_str else {}
                        body_data = json.loads(body_str) if body_str else None
                        
                        # Execute HTTP requests with looping
                        for loop_i in range(loop_count):
                            if not self.is_running:
                                break
                            
                            # Update status for loop iteration
                            if loop_count > 1:
                                self.status_label.config(text=f"Menjalankan: {func.get('name', 'Unnamed')} - Loop {loop_i+1}/{loop_count} ({i+1}/{total_functions})")
                                self.root.update()
                            
                            # Make HTTP request
                            response = None
                            if method == 'GET':
                                response = requests.get(url, headers=headers, timeout=30)
                            elif method == 'POST':
                                if body_data:
                                    response = requests.post(url, headers=headers, json=body_data, timeout=30)
                                else:
                                    response = requests.post(url, headers=headers, timeout=30)
                            elif method == 'PUT':
                                if body_data:
                                    response = requests.put(url, headers=headers, json=body_data, timeout=30)
                                else:
                                    response = requests.put(url, headers=headers, timeout=30)
                            elif method == 'DELETE':
                                response = requests.delete(url, headers=headers, timeout=30)
                            elif method == 'PATCH':
                                if body_data:
                                    response = requests.patch(url, headers=headers, json=body_data, timeout=30)
                                else:
                                    response = requests.patch(url, headers=headers, timeout=30)
                            
                            # Log response status
                            if response:
                                print(f"HTTP {method} {url} - Status: {response.status_code}")
                                if response.status_code >= 400:
                                    print(f"Response: {response.text}")
                            
                            # Apply loop delay if not the last iteration
                            if loop_i < loop_count - 1 and loop_delay > 0:
                                time.sleep(loop_delay)
                                
                    except requests.exceptions.RequestException as e:
                        print(f"HTTP Request Error: {str(e)}")
                        messagebox.showwarning("HTTP Error", f"HTTP Request gagal: {str(e)}")
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {str(e)}")
                        messagebox.showwarning("JSON Error", f"Error parsing JSON: {str(e)}")
                    except Exception as e:
                        print(f"Unexpected Error: {str(e)}")
                        messagebox.showwarning("Error", f"Error pada HTTP Request: {str(e)}")
            
            elif func['type'] == "Wait for Image":
                if func['parameter']:
                    try:
                        # Parse Wait for Image parameters
                        image_params = json.loads(func['parameter'])
                        image_path = image_params.get('image_path', '')
                        threshold = image_params.get('threshold', 0.8)
                        timeout = image_params.get('timeout', 30)
                        
                        # Update status to show waiting
                        self.status_label.config(text=f"Menunggu gambar: {func.get('name', 'Unnamed')} ({i+1}/{total_functions})")
                        self.root.update()
                        
                        # Wait for image to appear
                        success, message = self.wait_for_image(image_path, threshold, timeout)
                        
                        if success:
                            print(f"Wait for Image Success: {message}")
                        else:
                            print(f"Wait for Image Failed: {message}")
                            if "Stopped by user" not in message:
                                messagebox.showwarning("Wait for Image", f"Gambar tidak ditemukan: {message}")
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error in Wait for Image: {str(e)}")
                        messagebox.showwarning("JSON Error", f"Error parsing Wait for Image parameters: {str(e)}")
                    except Exception as e:
                        print(f"Unexpected Error in Wait for Image: {str(e)}")
                        messagebox.showwarning("Error", f"Error pada Wait for Image: {str(e)}")
            
            elif func['type'] == "Set Variable":
                if func['parameter']:
                    try:
                        # Parse Set Variable parameters
                        var_params = json.loads(func['parameter'])
                        var_name = var_params.get('variable_name', '')
                        var_source = var_params.get('variable_source', 'Manual Input')
                        var_value = var_params.get('variable_value', '')
                        
                        # Get value based on source
                        if var_source == "Manual Input":
                            value = var_value
                        elif var_source == "Clipboard":
                            value = pyperclip.paste()
                        elif var_source == "Current Time":
                            value = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            value = var_value
                        
                        # Store variable
                        self.variables[var_name] = value
                        print(f"Variable '{var_name}' set to: {value}")
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error in Set Variable: {str(e)}")
                        messagebox.showwarning("JSON Error", f"Error parsing Set Variable parameters: {str(e)}")
                    except Exception as e:
                        print(f"Unexpected Error in Set Variable: {str(e)}")
                        messagebox.showwarning("Error", f"Error pada Set Variable: {str(e)}")
            
            elif func['type'] == "Get Variable":
                if func['parameter']:
                    try:
                        # Parse Get Variable parameters
                        var_params = json.loads(func['parameter'])
                        var_name = var_params.get('variable_name', '')
                        
                        # Get variable value
                        if var_name in self.variables:
                            value = self.variables[var_name]
                            # Copy to clipboard for use
                            pyperclip.copy(str(value))
                            print(f"Variable '{var_name}' retrieved: {value} (copied to clipboard)")
                        else:
                            print(f"Variable '{var_name}' not found")
                            messagebox.showwarning("Variable Error", f"Variabel '{var_name}' tidak ditemukan!")
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error in Get Variable: {str(e)}")
                        messagebox.showwarning("JSON Error", f"Error parsing Get Variable parameters: {str(e)}")
                    except Exception as e:
                        print(f"Unexpected Error in Get Variable: {str(e)}")
                        messagebox.showwarning("Error", f"Error pada Get Variable: {str(e)}")
            
            elif func['type'] == "Start Loop":
                if func['parameter']:
                    try:
                        # Parse Start Loop parameters
                        loop_params = json.loads(func['parameter'])
                        loop_type = loop_params.get('loop_type', 'Fixed Count')
                        loop_count = int(loop_params.get('loop_count', 1))
                        loop_delay = float(loop_params.get('loop_delay', 1.0))
                        
                        # Find the matching End Loop
                        end_loop_index = None
                        loop_depth = 0
                        
                        for j in range(i + 1, len(enabled_functions)):
                            if enabled_functions[j]['type'] == "Start Loop":
                                loop_depth += 1
                            elif enabled_functions[j]['type'] == "End Loop":
                                if loop_depth == 0:
                                    end_loop_index = j
                                    break
                                else:
                                    loop_depth -= 1
                        
                        if end_loop_index is None:
                            messagebox.showwarning("Error", f"Start Loop '{func.get('name', 'Unnamed')}' tidak memiliki End Loop yang sesuai!")
                            continue
                        
                        # Get functions between Start Loop and End Loop
                        loop_functions = enabled_functions[i + 1:end_loop_index]
                        
                        # Execute loop based on type
                        if loop_type == "Fixed Count":
                            for loop_i in range(loop_count):
                                if not self.is_running or self.emergency_stop:
                                    break
                                
                                # Update status for loop iteration
                                self.status_label.config(text=f"Loop: {func.get('name', 'Unnamed')} - Iterasi {loop_i+1}/{loop_count}")
                                self.root.update()
                                
                                # Apply loop delay if not the first iteration
                                if loop_i > 0 and loop_delay > 0:
                                    time.sleep(loop_delay)
                                
                                # Execute functions within the loop
                                for loop_func in loop_functions:
                                    if not self.is_running or self.emergency_stop:
                                        break
                                    
                                    # Execute the function (reuse existing execution logic)
                                    self.execute_single_function(loop_func)
                        
                        elif loop_type == "Infinite":
                            loop_i = 0
                            while self.is_running and not self.emergency_stop:
                                loop_i += 1
                                
                                # Update status for infinite loop
                                self.status_label.config(text=f"Loop Infinite: {func.get('name', 'Unnamed')} - Iterasi {loop_i}")
                                self.root.update()
                                
                                # Apply loop delay
                                if loop_delay > 0:
                                    time.sleep(loop_delay)
                                
                                # Execute functions within the loop
                                for loop_func in loop_functions:
                                    if not self.is_running or self.emergency_stop:
                                        break
                                    
                                    # Execute the function (reuse existing execution logic)
                                    self.execute_single_function(loop_func)
                        
                        elif loop_type == "Until Condition":
                            # For now, implement as fixed count (can be extended later)
                            for loop_i in range(loop_count):
                                if not self.is_running or self.emergency_stop:
                                    break
                                
                                # Update status for conditional loop
                                self.status_label.config(text=f"Loop Kondisi: {func.get('name', 'Unnamed')} - Iterasi {loop_i+1}/{loop_count}")
                                self.root.update()
                                
                                # Apply loop delay if not the first iteration
                                if loop_i > 0 and loop_delay > 0:
                                    time.sleep(loop_delay)
                                
                                # Execute functions within the loop
                                for loop_func in loop_functions:
                                    if not self.is_running or self.emergency_stop:
                                        break
                                    
                                    # Execute the function (reuse existing execution logic)
                                    self.execute_single_function(loop_func)
                        
                        # Skip to after the End Loop
                        i = end_loop_index
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error in Start Loop: {str(e)}")
                        messagebox.showwarning("JSON Error", f"Error parsing Start Loop parameters: {str(e)}")
                    except Exception as e:
                        print(f"Unexpected Error in Start Loop: {str(e)}")
                        messagebox.showwarning("Error", f"Error pada Start Loop: {str(e)}")
            
            elif func['type'] == "End Loop":
                # End Loop is handled by Start Loop, so we skip it
                continue
            
            # Apply delay after function execution
            if func['delay'] > 0:
                time.sleep(func['delay'])
            
            # Update progress
            self.progress['value'] = i + 1
            self.root.update()
        
        if self.is_running:
            self.status_label.config(text="Automation selesai!")
            messagebox.showinfo("Selesai", "Semua fungsi automation telah dijalankan!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi error: {str(e)}")
    finally:
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


def execute_single_function(self, func):
    """Execute a single automation function"""
    try:
        if func['type'] == "Click":
            if func.get('x') and func.get('y'):
                pyautogui.click(func['x'], func['y'])
        
        elif func['type'] == "Double Click":
            if func.get('x') and func.get('y'):
                pyautogui.doubleClick(func['x'], func['y'])
        
        elif func['type'] == "Right Click":
            if func.get('x') and func.get('y'):
                pyautogui.rightClick(func['x'], func['y'])
        
        elif func['type'] == "Type Text":
            if func['parameter']:
                text = func['parameter']
                processed_text = self.process_text_for_typing(text)
                self.safe_typewrite(processed_text)
        
        elif func['type'] == "Type Text Popup":
            # Show popup for text input during execution
            popup_result = self.show_text_input_popup(func.get('name', 'Fungsi'))
            if popup_result["confirmed"] and popup_result["text"]:
                processed_text = self.process_text_for_typing(popup_result["text"])
                self.safe_typewrite(processed_text)
        
        elif func['type'] == "Hotkey":
            if func['parameter']:
                keys = func['parameter'].split('+')
                keys = [key.strip() for key in keys]
                pyautogui.hotkey(*keys)
        
        elif func['type'] == "Delay":
            delay_time = func.get('delay', 1.0)
            if delay_time > 0:
                time.sleep(delay_time)
        
        elif func['type'] == "Scroll":
            if func['parameter']:
                try:
                    scroll_params = json.loads(func['parameter'])
                    direction = scroll_params.get('direction', 'Down')
                    amount = int(scroll_params.get('amount', 3))
                    
                    if direction == "Up":
                        pyautogui.scroll(amount)
                    else:
                        pyautogui.scroll(-amount)
                except (json.JSONDecodeError, ValueError):
                    pass
        
        elif func['type'] == "Drag":
            if func.get('x') and func.get('y') and func['parameter']:
                try:
                    x1, y1 = func['x'], func['y']
                    drag_params = json.loads(func['parameter'])
                    x2 = int(drag_params.get('drag_x', 0))
                    y2 = int(drag_params.get('drag_y', 0))
                    pyautogui.drag(x2 - x1, y2 - y1, duration=1)
                except (json.JSONDecodeError, ValueError):
                    pass
        
        # Apply delay after function execution
        delay = func.get('delay', 1.0)
        if delay > 0:
            time.sleep(delay)
            
    except Exception as e:
        print(f"Error executing function {func.get('name', 'Unknown')}: {str(e)}")
        messagebox.showwarning("Error", f"Error pada fungsi {func.get('name', 'Unknown')}: {str(e)}")
