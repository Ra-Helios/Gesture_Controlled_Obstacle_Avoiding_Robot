import network
import socket
import time
from machine import Pin, PWM
import machine
import random

# Motor Pins
ENA = PWM(Pin(25))
IN1 = Pin(26, Pin.OUT)
IN2 = Pin(27, Pin.OUT)
IN3 = Pin(14, Pin.OUT)
IN4 = Pin(12, Pin.OUT)
ENB = PWM(Pin(33))
ENA.freq(5000)
ENB.freq(5000)

# Ultrasonic
TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

OBSTACLE_THRESHOLD = 15  # cm
last_cmd = "S"

# Wi-Fi AP
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32-GestureBot", password="12345678")
print("Access Point Created:", ap.ifconfig()[0])

# UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 4210))
sock.settimeout(0.05)
print("UDP Server ready to receive commands\n")


# --- Motor Movement Functions ---
def stop_robot():
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.off()
    ENA.duty(0)
    ENB.duty(0)


def move_forward(speed=800):
    IN1.on()
    IN2.off()
    IN3.on()
    IN4.off()
    ENA.duty(speed)
    ENB.duty(speed)


def move_backward(speed=800):
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.on()
    ENA.duty(speed)
    ENB.duty(speed)


def turn_left(speed=700):
    IN1.off()
    IN2.on()
    IN3.on()
    IN4.off()
    ENA.duty(speed)
    ENB.duty(speed)


def turn_right(speed=700):
    IN1.on()
    IN2.off()
    IN3.off()
    IN4.on()
    ENA.duty(speed)
    ENB.duty(speed)


# --- Ultrasonic Distance ---
def get_distance():
    TRIG.off()
    time.sleep_us(2)
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()
    try:
        t = machine.time_pulse_us(ECHO, 1, 30000)
        return int((t * 0.0343) / 2)
    except OSError:
        return -1


# --- Improved Avoid-Obstacle Sequence ---
def avoid_obstacle():
    print("⚠️ Obstacle detected! Executing avoidance sequence...")
    stop_robot()
    time.sleep(0.5)
    print("Taking a small step backward...")
    move_backward(600)
    time.sleep(0.6)
    stop_robot()
    time.sleep(0.3)

    direction = random.choice(["left", "right"])
    if direction == "left":
        print("Turning Left to avoid obstacle.")
        turn_left(700)
    else:
        print("Turning Right to avoid obstacle.")
        turn_right(700)
    time.sleep(0.7)

    print("Moving forward again.")
    move_forward()
    time.sleep(0.8)
    stop_robot()


print("ESP32 Gesture Bot Ready!\n")

# --- Main Loop ---
while True:
    try:
        # Non-blocking receive for gesture commands
        data, addr = sock.recvfrom(128)
        last_cmd = data.decode().strip().upper()
    except OSError:
        pass  # No new command → keep previous one

    distance = get_distance()
    print(f"Command: {last_cmd} | Distance: {distance} cm")

    # Run obstacle check continuously
    if 0 < distance < OBSTACLE_THRESHOLD:
        avoid_obstacle()
        last_cmd = "S"
        continue

    # Execute gesture command
    if last_cmd == "F":
        move_forward()
    elif last_cmd == "B":
        move_backward()
    elif last_cmd == "L":
        turn_left()
    elif last_cmd == "R":
        turn_right()
    elif last_cmd == "S":
        stop_robot()

    time.sleep_ms(100)
