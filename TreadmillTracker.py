import serial
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pyautogui
import time
import os
from pathlib import Path
from screeninfo import get_monitors
import ctypes
import sys
import json
import serial.tools
import serial.tools.list_ports


""" Simple script allowing user to read distance(km) and time(0h00) var from a pico board connected to a treadmill, via thonny. Script override W keyboard key when motion
is detected and the Override Keyboard button is pressed. Script also include a log function, and a reset log function linked to a physical button. """

# --- CONFIG ---
BAUD_RATE = 115200 
LOG_FILE = Path(__file__).parent / "gui_log.txt"
CONFIG_FILE = Path(__file__).parent / "config.json"
KEY = "screen_index" # value used to select which screen to project timer on.

# --- GLOBAL VARIABLES ---
running = True 
keyboard_enabled = False 
start_time = None 
active_timer_seconds = 0 
w_held = False  
SERIAL_PORT = None


# --- LOAD/SAVE TIMER STATE --
def load_log():
    """ interp. Loads log.txt and reads its content."""
    global active_timer_seconds
    if os.path.exists(LOG_FILE): # finds gui_log.txt 
        try:
            with open(LOG_FILE, 'r') as f:
                active_timer_seconds = int(f.read().strip()) 
        except:
            active_timer_seconds = 0 
    

def save_log(): 
    """interp. Writes in log.txt the timer 0h00 value."""
    try:
        with open(LOG_FILE, 'w') as f:
            f.write(str(active_timer_seconds))
    except:
        pass

# --- LOAD/SAVE CONFIG ---
def load_config():
    """ interp. Loads config files and returns its content."""
    # returns int.
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {}   

def save_config(cfg: dict):
    """ intep. Saves cfg value into config file. """

    CONFIG_FILE.write_text(json.dumps(cfg))


# --- TIMER DISPLAY ---  
def format_timer(seconds): 
    """ interp. Since the Timer values is written in seconds, this function formats the timer to 0h00 for easier reading."""
    # returns formated string.
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h{m:02d}"

# --- RESET TIMER FUNCTION ---
def reset_timer(): 
    """ interp. Resets the timer values, start time value, active value and save the news values into the log.txt """
    global active_timer_seconds, start_time
    active_timer_seconds = 0
    start_time = None
    timer_var.set(format_timer(active_timer_seconds))
    save_log()

# --- find COM ---
def find_pico_port():
    """ interp. Finds the name of the port COM# given by the OS, to the pico. """
    # returns str.
    for port in serial.tools.list_ports.comports():
        if port.vid == 0x2e8a and port.pid in (0x0003, 0x0005):
            return port.device
       

# --- GUI SETUP FOR TREADMILL TRACKER ---
root = tk.Tk()
root.title("Treadmill Tracker")
root.geometry("700x280")
root.minsize(350, 140)

img_dir = Path(__file__).parent.resolve()
img = tk.PhotoImage(file=str(img_dir / "TreadmillTracker_icon.png"))
root.iconphoto(False, img)

pulse_var = tk.StringVar(value="0")
distance_var = tk.StringVar(value="0.000 km")
timer_var = tk.StringVar(value="0h00")
cfg = load_config()
last_idx = cfg.get(KEY, 4)
spin_var = tk.IntVar(value=last_idx)
screen = get_monitors()
max_idx = len(screen) - 1

frame = ttk.Frame(root, padding=20)
frame.grid(sticky="nsew")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure((0, 1), weight=1)
style = ttk.Style()
style.theme_use("clam")
style.configure("Bold.TLabel", font=("Helvetica", 12, "bold"))

# All UI labels. 

ttk.Label(frame, text="Pulses:", style= "Bold.TLabel").grid(column=0, row=0, sticky="w")
ttk.Label(frame, textvariable=pulse_var, style= "Bold.TLabel").grid(column=1, row=0, sticky="w")

ttk.Label(frame, text="Distance:", style= "Bold.TLabel").grid(column=0, row=1, sticky="w")
ttk.Label(frame, textvariable=distance_var, style= "Bold.TLabel").grid(column=1, row=1, sticky="w")

ttk.Label(frame, text="Timer:", style= "Bold.TLabel").grid(column=0, row=2, sticky="w")
ttk.Label(frame, textvariable=timer_var, style= "Bold.TLabel").grid(column=1, row=2, sticky="w")

ttk.Label(frame, text="Toggle Key Override:", style="Bold.TLabel").grid(column=0, row=3, sticky= 'w')
ttk.Label(frame, text="Screen Overlay:", style= "Bold.TLabel").grid(column=2, row=0, columnspan=1, sticky='w')

# licensing info:
def show_about():
    messagebox.showinfo("About", "This software is licensed under the Creative Commons Zero v1.0 Universal License.\nNo commercial use is allowed.\nAuthor: Ines Wisseme \nDate: June 2025")

# Select Button functions.

def show_warning(msg="Monitor not found!"):
    """ interp. Warning for Monitor not found. Will trigger if user select a monitor that isn't there."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("Warning", msg)
    root.destroy()


def on_submit():
    """ interp. function used in Save Selection Button, it selects the monitor corresponding to user selection and update the overlay. If error shows warning. """
    idx = spin_var.get()   

    try:
        screen = get_monitors()[idx] 
        overlay.geometry(f"+{screen.x + 20}+{screen.y + 20}")


    except IndexError:
        show_warning()   

    
# Spinbox for screen selection. Select Button for screen selection. 
spin = ttk.Spinbox(frame, from_=0, to= max_idx, textvariable=spin_var, width=5) # in range [0, max_idx] max_idx represents the max amount of screens detected by OS.
spin.grid(row=1, column=2, padx=5, pady=10 )

spin_button = ttk.Button(frame, text="Save Selection", command=on_submit)
spin_button.grid(column=2, row=2, columnspan=1, pady=10)

# Keyboard override button function. 
def toggle_keyboard(): 
    global keyboard_enabled
    keyboard_enabled = not keyboard_enabled
    if keyboard_enabled:
        toggle_button.config(text="Keyboard: ON", background="green")
    else:
        toggle_button.config(text="Keyboard: OFF", background="SystemButtonFace")

# Keyboard override button.
toggle_button = tk.Button(frame, text="Keyboard: OFF", command=toggle_keyboard)
toggle_button.grid(column=0, row=3, columnspan=2, pady=10, padx=(160,5))

about_button = ttk.Button(frame, text = "About", command = show_about, width=6)
about_button.grid(column=2,row=4, columnspan=2, pady=50)



# --- TIMER UPDATE ---
def update_timer_label():
    """ interp. Upates timer label on GUI. """
    timer_var.set(format_timer(active_timer_seconds))
    root.after(1000, update_timer_label)

# --- SERIAL THREAD --- # Main loop.
w_held = False  

def serial_reader(): # gets info from pico via serial.
    global running, start_time, active_timer_seconds, w_held

    SERIAL_PORT = find_pico_port()

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            last_pulse_time = time.time()
            while running:
                line = ser.readline().decode('utf-8').strip()

                if line.strip() == "RESET": # if RESET (button held down for 8sec) script reset timer.
                    reset_timer()

                if "," in line:
                    parts = line.split(",")
                    if len(parts) == 2:
                        pulse_var.set(parts[0])
                        distance_var.set(f"{float(parts[1]):.3f} km")

                        # Movement detected start W key override:
                        last_pulse_time = time.time()
                        if keyboard_enabled and not w_held:
                            pyautogui.keyDown('w')
                            w_held = True

                        # Timer:
                        if start_time is None:
                            start_time = time.time()
                        else:
                            now = time.time()
                            delta = now - start_time
                            if delta >= 1:
                                active_timer_seconds += int(delta)
                                start_time = now
                                save_log()

                # Stop W key if no pulse for 0.5 seconds. Change this setting for reactivity.
                if w_held and (time.time() - last_pulse_time > 0.5):
                    pyautogui.keyUp('w')
                    w_held = False
    except serial.SerialException as e:
        print(f"Serial error: {e}")


# --- OVERLAY WINDOW ON SCREEN SETUP ---


def make_overlay():
    overlay = tk.Toplevel()
    overlay.title("Overlay")
    overlay.overrideredirect(True)
    overlay.attributes("-topmost", True)
    overlay.configure(bg="black")

    label = tk.Label(
        overlay,
        textvariable=overlay_text,
        font=("Helvetica", 24, "bold"),
        fg="white",
        bg="black"
    )
    label.pack(padx=10, pady=5)

    def make_clickthrough():
        if sys.platform == 'win32':
            hwnd = ctypes.windll.user32.GetParent(overlay.winfo_id())
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20
            WS_EX_TOPMOST = 0x00000008
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

            # Optional: set window transparency (0 = fully transparent, 255 = opaque)
            LWA_ALPHA = 0x2
            ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)

    # Delay to ensure window is initialized before applying styles
    overlay.after(100, make_clickthrough)

    return overlay

# --- UPDATE OVERLAY ---
def update_overlay():
    overlay_text.set(f"{distance_var.get()} | {timer_var.get()}")
    idx = spin_var.get()     
    screen = get_monitors()[idx] 
    overlay.geometry(f"+{screen.x + 20}+{screen.y + 20}")
    root.after(1000, update_overlay)

# --- CLEANUP ---
def on_close():
    global running
    running = False
    save_log()
    cfg[KEY] = spin_var.get()
    save_config(cfg)
    root.destroy()

# === START APP ===

load_log()
update_timer_label()

overlay_text = tk.StringVar()
overlay = make_overlay()
update_overlay()

threading.Thread(target=serial_reader, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
