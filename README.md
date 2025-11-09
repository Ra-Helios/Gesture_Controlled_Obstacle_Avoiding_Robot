# 🤖 Gesture‑Controlled Wi‑Fi Robot with Obstacle Avoidance & Live Telemetry

Control an ESP32‑powered robot using **hand gestures** with **OpenCV + MediaPipe**, sent wirelessly over **UDP Wi‑Fi**.
Two operation modes are supported:

| Mode | Directory | Description |
|------|----------|-------------|
| ✅ **Without Live Plotter** | `/Without_Live_Plotter` | Pure gesture control with obstacle avoidance |
| 📊 **With Live Plotter** | `/With_Live_Plotter` | Gesture control **+ real‑time motion & ultrasonic plotting** |

---

## ✨ Key Features

| Capability | Details |
|-----------|--------|
🎯 **Real‑time gesture recognition** | Track hand landmarks to send drive commands
📶 **Wi‑Fi UDP control** | Laptop → ESP32, fast low‑latency commands
🛑 **Automatic obstacle avoidance** | Ultrasonic braking + auto‑halt logic
📈 **Live plotting mode** | Track movement + distance in real‑time (matplotlib)
🧠 **Clean modular repo** | Separated folders for easier navigation
🔁 **Telemetry feedback** | Robot reports movement + sensor values
🛠️ **MicroPython firmware** | Lightweight & fast on ESP32

> The bot moves **Forward, Backward, Left, Right, Stop** based on gesture recognition.

---

## 📂 Repository Structure

```
📁 Gesture‑Controlled‑Bot/
├── 📁 With_Live_Plotter/
│   ├── esp32_wlp.py
│   ├── lap_gest_wlp.py
│   └── live_plotter.py
│
└── 📁 Without_Live_Plotter/
    ├── lap_gest.py
    └── esp32.py
```

---

## 🧠 System Architecture

Laptop Camera → MediaPipe Gesture Detection → UDP Packets → ESP32 Motor PWM → Robot Movement
& in live mode → Telemetry → PC → **Live Graph**

---

## 🛠️ Hardware Reference

| Component | Usage |
|----------|-------|
ESP32 | Wi‑Fi + motor control + ultrasonic
L298N/H‑Bridge | Motor driver
Ultrasonic HC‑SR04 | Obstacle detection
Laptop Camera | Gesture input

### ⚙️ ESP32 Pin Map
| Function | Pin |
|---------|----|
Motor PWM | GPIO 25, 33
Motor Dir | 26, 27, 14, 12
Ultrasonic | TRIG=5, ECHO=18

---

## 📡 Network & Config

| Setting | Value |
|--------|-------|
AP SSID | `ESP32-GestureBot`
Password | `12345678`
ESP32 IP | `192.168.4.1`
Laptop UDP target | `4210`
Telemetry (live mode) | Port `5000` to laptop IP

---

## 🚀 Setup

### 1️⃣ Install PC Requirements
```bash
pip install -r requirements.txt
# Recommanded ---> Python 3.11
```

### 2️⃣ Flash ESP32 (MicroPython)

Choose the mode folder:

✅ Without live plot → `esp32.py`

📊 With live plot → set your PC IP in `esp32_wlp.py` then upload

---

## ▶️ Run

### **Without Live Plot**
```bash
cd Without_Live_Plotter
python lap_gest.py
```

### **With Live Plot**
```bash
cd With_Live_Plotter
python live_plotter.py     # start logger first
python lap_gest_wlp.py
```

> Robot begins responding to gestures immediately. Press `Esc` to exit.

---

## 📊 Telemetry Format
```
<COMMAND>,<DIST_CM>,<TIMESTAMP_MS>

Example:
F,22,18992
OBSTACLE,9,19020
```

---

## 🧩 Future Enhancements Ideas
- Add Web UI dashboard (Flask)
- Train ML model for gesture instead of heuristics
- Add wheel encoders for accurate path mapping
- Deploy on Raspberry Pi + ESP‑Now mesh variant

---

## 💡 Tips
✅ Use good lighting for gesture detection

✅ Ensure PC connected to ESP32 Wi‑Fi

✅ Test robot on support before ground runs

---

## 🏅 Credits
- MediaPipe & OpenCV for gesture tracking
- MicroPython community for ESP32 control patterns

---
