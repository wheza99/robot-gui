"""
Text handling functions for the automation GUI
"""
import pyautogui
import pyperclip
import re

def safe_typewrite(self, text):
    """Enhanced typing method that handles special characters and emoticons better"""
    if not text:
        return
        
    try:
        # Try normal typewrite first
        pyautogui.typewrite(text)
    except Exception as e:
        # If normal typewrite fails, try character by character
        print(f"Normal typewrite failed: {e}. Trying character by character...")
        for char in text:
            try:
                if char == '\n':
                    # Handle newline with Enter key
                    pyautogui.press('enter')
                elif char == '\t':
                    # Handle tab with Tab key
                    pyautogui.press('tab')
                else:
                    # Try to type the character
                    pyautogui.typewrite(char)
            except Exception as char_error:
                # If character can't be typed, try using clipboard
                try:
                    pyperclip.copy(char)
                    pyautogui.hotkey('ctrl', 'v')
                except Exception as clipboard_error:
                    print(f"Could not type character '{char}': {char_error}, clipboard error: {clipboard_error}")
                    # Skip this character if all methods fail

def process_text_for_typing(self, text):
    """Process text to handle escape sequences, special characters, and variable placeholders"""
    if not text:
        return text
        
    # Handle variable placeholders first (format: ${variable_name})
    def replace_variable(match):
        var_name = match.group(1)
        if var_name in self.variables:
            return str(self.variables[var_name])
        else:
            # Return placeholder as-is if variable not found
            return match.group(0)
    
    # Replace variable placeholders
    processed_text = re.sub(r'\$\{([^}]+)\}', replace_variable, text)
    
    # Handle common escape sequences
    processed_text = processed_text.replace('\\n', '\n')  # New line
    processed_text = processed_text.replace('\\t', '\t')  # Tab
    processed_text = processed_text.replace('\\r', '\r')  # Carriage return
    processed_text = processed_text.replace('\\\\', '\\')  # Literal backslash
    
    return processed_text
