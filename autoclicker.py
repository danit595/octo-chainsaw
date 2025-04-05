import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import keyboard

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("300x150")
        
        self.clicking = False
        self.click_thread = None
        
        # Create and set up GUI elements
        self.create_widgets()
        
        # Setup hotkey
        keyboard.on_press_key('f6', lambda _: self.toggle_clicking())
        
    def create_widgets(self):
        # Delay input frame
        delay_frame = ttk.Frame(self.root)
        delay_frame.pack(pady=10)
        
        ttk.Label(delay_frame, text="Delay (ms):").pack(side=tk.LEFT, padx=5)
        self.delay_input = ttk.Entry(delay_frame, width=10)
        self.delay_input.insert(0, "1000")
        self.delay_input.pack(side=tk.LEFT, padx=5)
        
        # Toggle button
        self.toggle_button = ttk.Button(
            self.root,
            text="Start",
            command=self.toggle_clicking
        )
        self.toggle_button.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Status: Stopped")
        self.status_label.pack(pady=10)
        
    def toggle_clicking(self):
        if not self.clicking:
            try:
                delay = int(self.delay_input.get())
                if delay < 1:
                    raise ValueError("Delay must be positive")
                
                self.clicking = True
                self.toggle_button.config(text="Stop")
                self.status_label.config(text="Status: Running")
                
                self.click_thread = threading.Thread(target=self.clicking_loop, args=(delay,))
                self.click_thread.daemon = True
                self.click_thread.start()
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number for delay.")
        else:
            self.clicking = False
            self.toggle_button.config(text="Start")
            self.status_label.config(text="Status: Stopped")
            
    def clicking_loop(self, delay):
        while self.clicking:
            pyautogui.click()
            time.sleep(delay / 1000.0)
            
    def on_closing(self):
        self.clicking = False
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=1.0)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == '__main__':
    main() 