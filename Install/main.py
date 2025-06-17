from machine import Pin
import time

PULSES_PER_KM = 6667  # Adjust as needed
LOG_FILE = "log.txt"

pulse_pin = Pin(20, Pin.IN, Pin.PULL_UP)  # Main sensor
button = Pin(2, Pin.IN, Pin.PULL_UP)      # Clear log button
led = Pin("LED", Pin.OUT)

pulse_count = 0
distance_km = 0.0

LONG_PRESS_DURATION = 6000  # milliseconds

def load_log():
    global pulse_count, distance_km
    try:
        with open(LOG_FILE, "r") as f:
            line = f.readline()
            if "," in line:
                pulse_count, distance_km = line.strip().split(",")
                pulse_count = int(pulse_count)
                distance_km = float(distance_km)
    except:
        pulse_count = 0
        distance_km = 0.0

def save_log():
    try:
        with open(LOG_FILE, "w") as f:
            f.write(f"{pulse_count},{distance_km:.3f}\n")
    except:
        pass

def clear_log():
    global pulse_count, distance_km
    pulse_count = 0
    distance_km = 0.0
    save_log()
    print("RESET")
    print("0,0.000")

def check_long_press():
    if button.value() == 0:
        press_start = time.ticks_ms()
        while button.value() == 0:
            if time.ticks_diff(time.ticks_ms(), press_start) > LONG_PRESS_DURATION:
                clear_log()
                while button.value() == 0:
                    time.sleep_ms(10)
                time.sleep(1)
                return

# main:
load_log()
print(f"{pulse_count},{distance_km:.3f}")

last_state = pulse_pin.value()

while True:
    check_long_press()

    current_state = pulse_pin.value()
    if last_state == 1 and current_state == 0:
        pulse_count += 1
        distance_km = pulse_count / PULSES_PER_KM
        save_log()
        print(f"{pulse_count},{distance_km:.3f}")
        led.toggle()
        time.sleep_ms(20)

    last_state = current_state

