import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import keyboard
import threading
import time
import json
import os
from datetime import datetime
import mouse
from pathlib import Path

class OctoAutoClicker:
    VERSION = "1.0.1"
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"OctoAutoClicker v{self.VERSION}")
        self.root.resizable(False, False)
        
        # Add version label
        version_label = ttk.Label(self.root, text=f"Version {self.VERSION}", font=("Helvetica", 8))
        version_label.grid(row=1, column=0, sticky="SE", padx=5, pady=2)
        
        # State variables
        self.clicking = False
        self.click_thread = None
        self.click_count = 0
        self.recording = False
        self.current_macro = []
        self.record_thread = None
        self.playback_thread = None
        self.is_playing = False
        
        # Create macros directory if it doesn't exist
        self.macros_dir = Path("macros")
        self.macros_dir.mkdir(exist_ok=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Auto Clicker tab
        self.clicker_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.clicker_tab, text="Auto Clicker")
        
        # Macro Recording tab
        self.macro_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.macro_tab, text="Macro Recording")
        
        # Setup both tabs
        self._setup_clicker_tab()
        self._setup_macro_tab()
        
        # Register hotkeys
        keyboard.on_press_key("F6", lambda _: self.toggle_clicking())
        keyboard.on_press_key("F7", lambda _: self.toggle_recording())
        keyboard.on_press_key("esc", lambda _: self.emergency_stop())
        
        # Set PyAutoGUI settings
        pyautogui.FAILSAFE = True

    def _setup_clicker_tab(self):
        # Main frame
        main_frame = ttk.Frame(self.clicker_tab, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Click interval frame
        interval_frame = ttk.LabelFrame(main_frame, text="Click Interval", padding="5")
        interval_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Hours
        ttk.Label(interval_frame, text="Hours:").grid(row=0, column=0, padx=5)
        self.hours_var = tk.StringVar(value="0")
        ttk.Entry(interval_frame, width=8, textvariable=self.hours_var).grid(row=0, column=1, padx=5)
        
        # Minutes
        ttk.Label(interval_frame, text="Minutes:").grid(row=0, column=2, padx=5)
        self.minutes_var = tk.StringVar(value="0")
        ttk.Entry(interval_frame, width=8, textvariable=self.minutes_var).grid(row=0, column=3, padx=5)
        
        # Seconds
        ttk.Label(interval_frame, text="Seconds:").grid(row=0, column=4, padx=5)
        self.seconds_var = tk.StringVar(value="0")
        ttk.Entry(interval_frame, width=8, textvariable=self.seconds_var).grid(row=0, column=5, padx=5)
        
        # Milliseconds
        ttk.Label(interval_frame, text="Milliseconds:").grid(row=0, column=6, padx=5)
        self.milliseconds_var = tk.StringVar(value="100")
        ttk.Entry(interval_frame, width=8, textvariable=self.milliseconds_var).grid(row=0, column=7, padx=5)
        
        # Click options frame
        click_options_frame = ttk.LabelFrame(main_frame, text="Click Options", padding="5")
        click_options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Mouse button selection
        ttk.Label(click_options_frame, text="Mouse Button:").grid(row=0, column=0, padx=5)
        self.mouse_button_var = tk.StringVar(value="left")
        mouse_button_combo = ttk.Combobox(click_options_frame, textvariable=self.mouse_button_var, 
                                        values=["left", "right", "middle"], width=10, state="readonly")
        mouse_button_combo.grid(row=0, column=1, padx=5)
        
        # Click type selection
        ttk.Label(click_options_frame, text="Click Type:").grid(row=0, column=2, padx=5)
        self.click_type_var = tk.StringVar(value="single")
        click_type_combo = ttk.Combobox(click_options_frame, textvariable=self.click_type_var,
                                      values=["single", "double"], width=10, state="readonly")
        click_type_combo.grid(row=0, column=3, padx=5)
        
        # Repeat options frame
        repeat_frame = ttk.LabelFrame(main_frame, text="Repeat Options", padding="5")
        repeat_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Repeat type
        self.repeat_type_var = tk.StringVar(value="until_stopped")
        ttk.Radiobutton(repeat_frame, text="Repeat until stopped", 
                       variable=self.repeat_type_var, value="until_stopped").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(repeat_frame, text="Repeat", 
                       variable=self.repeat_type_var, value="repeat_times").grid(row=0, column=1, padx=5)
        
        self.repeat_times_var = tk.StringVar(value="1")
        self.repeat_times_entry = ttk.Entry(repeat_frame, width=8, textvariable=self.repeat_times_var)
        self.repeat_times_entry.grid(row=0, column=2, padx=5)
        ttk.Label(repeat_frame, text="times").grid(row=0, column=3, padx=5)
        
        # Click position frame
        position_frame = ttk.LabelFrame(main_frame, text="Click Position", padding="5")
        position_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Position type
        self.position_type_var = tk.StringVar(value="current")
        ttk.Radiobutton(position_frame, text="Current Position", 
                       variable=self.position_type_var, value="current").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(position_frame, text="Pick Position", 
                       variable=self.position_type_var, value="pick").grid(row=0, column=1, padx=5)
        
        # X, Y coordinates
        ttk.Label(position_frame, text="X:").grid(row=0, column=2, padx=5)
        self.x_pos_var = tk.StringVar(value="0")
        ttk.Entry(position_frame, width=6, textvariable=self.x_pos_var).grid(row=0, column=3, padx=5)
        
        ttk.Label(position_frame, text="Y:").grid(row=0, column=4, padx=5)
        self.y_pos_var = tk.StringVar(value="0")
        ttk.Entry(position_frame, width=6, textvariable=self.y_pos_var).grid(row=0, column=5, padx=5)
        
        # Pick position button
        self.pick_pos_button = ttk.Button(position_frame, text="Pick Position", command=self.pick_position)
        self.pick_pos_button.grid(row=0, column=6, padx=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Start/Stop button
        self.start_stop_button = ttk.Button(status_frame, text="Start (F6)", command=self.toggle_clicking)
        self.start_stop_button.grid(row=0, column=0, padx=5)
        
        # Click counter
        self.click_counter_label = ttk.Label(status_frame, text="Clicks: 0")
        self.click_counter_label.grid(row=0, column=1, padx=5)
        
    def _setup_macro_tab(self):
        main_frame = ttk.Frame(self.macro_tab, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Recording controls frame
        recording_frame = ttk.LabelFrame(main_frame, text="Recording Controls", padding="5")
        recording_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Record button
        self.record_button = ttk.Button(recording_frame, text="Start Recording (F7)", 
                                      command=self.toggle_recording)
        self.record_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Save frame
        save_frame = ttk.Frame(recording_frame)
        save_frame.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(save_frame, text="Macro Name:").grid(row=0, column=0, padx=5)
        self.macro_name_var = tk.StringVar()
        self.macro_name_entry = ttk.Entry(save_frame, textvariable=self.macro_name_var, width=20)
        self.macro_name_entry.grid(row=0, column=1, padx=5)
        
        self.save_button = ttk.Button(save_frame, text="Save Macro", 
                                    command=self.save_macro, state="disabled")
        self.save_button.grid(row=0, column=2, padx=5)
        
        # Playback frame
        playback_frame = ttk.LabelFrame(main_frame, text="Playback Controls", padding="5")
        playback_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Macro list
        self.macro_listbox = tk.Listbox(playback_frame, height=6, width=40)
        self.macro_listbox.grid(row=0, column=0, rowspan=3, padx=5, pady=5)
        
        # Scrollbar for macro list
        scrollbar = ttk.Scrollbar(playback_frame, orient="vertical", 
                                command=self.macro_listbox.yview)
        scrollbar.grid(row=0, column=1, rowspan=3, sticky="ns")
        self.macro_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Playback controls
        controls_frame = ttk.Frame(playback_frame)
        controls_frame.grid(row=0, column=2, padx=5)
        
        self.play_button = ttk.Button(controls_frame, text="Play Macro", 
                                    command=self.play_macro)
        self.play_button.grid(row=0, column=0, pady=2)
        
        self.delete_button = ttk.Button(controls_frame, text="Delete Macro", 
                                      command=self.delete_macro)
        self.delete_button.grid(row=1, column=0, pady=2)
        
        # Refresh macro list
        self.refresh_macro_list()
        
    def get_click_interval(self):
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
            milliseconds = int(self.milliseconds_var.get())
            
            total_seconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000)
            return max(0.001, total_seconds)  # Ensure minimum interval of 1ms
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for the time interval.")
            return None
            
    def pick_position(self):
        self.root.iconify()  # Minimize window
        time.sleep(1)  # Give user time to move mouse
        x, y = pyautogui.position()
        self.root.deiconify()  # Restore window
        self.x_pos_var.set(str(x))
        self.y_pos_var.set(str(y))
        
    def perform_click(self):
        try:
            if self.position_type_var.get() == "pick":
                try:
                    x = int(self.x_pos_var.get())
                    y = int(self.y_pos_var.get())
                    pyautogui.moveTo(x, y)
                except ValueError:
                    messagebox.showerror("Error", "Invalid X,Y coordinates")
                    return False
                    
            button = self.mouse_button_var.get()
            # Map button names to PyAutoGUI's expected values
            button_map = {
                "left": "left",
                "right": "right",
                "middle": "middle"
            }
            mapped_button = button_map.get(button, "left")
            
            if self.click_type_var.get() == "double":
                pyautogui.doubleClick(button=mapped_button)
            else:
                pyautogui.click(button=mapped_button)
            return True
        except pyautogui.FailSafeException:
            messagebox.showinfo("Auto-Clicker Paused", 
                "The auto-clicker was paused because the mouse moved to a screen corner.\n"
                "This is a safety feature. To resume, move the mouse away from the corner and start again.")
            self.emergency_stop()
            return False
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while clicking: {str(e)}")
            self.emergency_stop()
            return False
            
    def clicking_loop(self):
        interval = self.get_click_interval()
        if interval is None:
            self.clicking = False
            return
            
        max_clicks = None
        if self.repeat_type_var.get() == "repeat_times":
            try:
                max_clicks = int(self.repeat_times_var.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number of repetitions")
                self.clicking = False
                return
                
        while self.clicking:
            if self.perform_click():
                self.click_count += 1
                self.click_counter_label.config(text=f"Clicks: {self.click_count}")
                
                if max_clicks and self.click_count >= max_clicks:
                    self.clicking = False
                    break
                    
            time.sleep(interval)
            
    def toggle_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.click_thread = threading.Thread(target=self.clicking_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
            self.start_stop_button.config(text="Stop (F6)")
        else:
            self.clicking = False
            self.start_stop_button.config(text="Start (F6)")
            
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.recording = True
        self.current_macro = []
        self.record_button.config(text="Stop Recording (F7)")
        self.save_button.config(state="disabled")
        
        def record_loop():
            start_time = time.time()
            last_position = pyautogui.position()
            
            while self.recording:
                current_time = time.time() - start_time
                current_position = pyautogui.position()
                
                # Record mouse movement if position changed
                if current_position != last_position:
                    self.current_macro.append({
                        'type': 'move',
                        'x': current_position[0],
                        'y': current_position[1],
                        'time': current_time
                    })
                    last_position = current_position
                
                # Check for mouse clicks
                for button in ['left', 'right', 'middle']:
                    if mouse.is_pressed(button=button):
                        self.current_macro.append({
                            'type': 'click',
                            'button': button,
                            'time': current_time
                        })
                        # Wait for button release to avoid multiple records
                        while mouse.is_pressed(button=button) and self.recording:
                            time.sleep(0.01)
                
                time.sleep(0.01)  # Reduce CPU usage
                
        self.record_thread = threading.Thread(target=record_loop)
        self.record_thread.daemon = True
        self.record_thread.start()
            
    def stop_recording(self):
        self.recording = False
        self.record_button.config(text="Start Recording (F7)")
        if self.current_macro:
            self.save_button.config(state="normal")
            
    def save_macro(self):
        name = self.macro_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the macro")
            return
            
        filename = self.macros_dir / f"{name}.json"
        with open(filename, 'w') as f:
            json.dump(self.current_macro, f)
            
        self.save_button.config(state="disabled")
        self.macro_name_var.set("")
        self.refresh_macro_list()
        
    def refresh_macro_list(self):
        self.macro_listbox.delete(0, tk.END)
        if self.macros_dir.exists():
            for macro_file in self.macros_dir.glob("*.json"):
                self.macro_listbox.insert(tk.END, macro_file.stem)
                
    def play_macro(self):
        selection = self.macro_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a macro to play")
            return
            
        macro_name = self.macro_listbox.get(selection[0])
        macro_file = self.macros_dir / f"{macro_name}.json"
        
        try:
            with open(macro_file, 'r') as f:
                macro_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load macro: {str(e)}")
            return
            
        if self.is_playing:
            self.is_playing = False
            self.play_button.config(text="Play Macro")
            return
            
        def playback_loop():
            self.is_playing = True
            self.play_button.config(text="Stop Playback")
            
            try:
                start_time = time.time()
                last_event_time = 0
                
                for event in macro_data:
                    if not self.is_playing:
                        break
                        
                    # Wait for the correct timing
                    current_time = time.time() - start_time
                    sleep_time = event['time'] - last_event_time
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    # Execute the event
                    if event['type'] == 'move':
                        pyautogui.moveTo(event['x'], event['y'])
                    elif event['type'] == 'click':
                        pyautogui.click(button=event['button'])
                    
                    last_event_time = event['time']
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error during playback: {str(e)}")
            finally:
                self.is_playing = False
                self.play_button.config(text="Play Macro")
                
        self.playback_thread = threading.Thread(target=playback_loop)
        self.playback_thread.daemon = True
        self.playback_thread.start()
        
    def delete_macro(self):
        selection = self.macro_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a macro to delete")
            return
            
        macro_name = self.macro_listbox.get(selection[0])
        macro_file = self.macros_dir / f"{macro_name}.json"
        
        try:
            macro_file.unlink()
            self.refresh_macro_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete macro: {str(e)}")
            
    def emergency_stop(self):
        if self.clicking:
            self.clicking = False
            self.start_stop_button.config(text="Start (F6)")
            self.click_count = 0
            self.click_counter_label.config(text="Clicks: 0")
        if self.recording:
            self.stop_recording()
        if self.is_playing:
            self.is_playing = False
            self.play_button.config(text="Play Macro")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = OctoAutoClicker()
    app.run() 