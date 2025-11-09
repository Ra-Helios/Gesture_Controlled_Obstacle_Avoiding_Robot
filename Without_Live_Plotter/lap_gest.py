import cv2
import mediapipe as mp
import socket
import time

ESP32_IP = "192.168.4.1"  # Default IP of ESP32 AP
ESP32_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Connecting to ESP32 at {ESP32_IP}:{ESP32_PORT}")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

gesture_map = {"forward": "F", "backward": "B", "left": "L", "right": "R", "stop": "S"}
last_sent = None
send_interval = 0.6
last_time = time.time()


# ----- Simplified Gesture Detection -----
def detect_gesture(landmarks):
    # Detect finger states (True = finger up / False = down)
    index_up = landmarks[8][1] < landmarks[6][1]
    middle_up = landmarks[12][1] < landmarks[10][1]
    ring_up = landmarks[16][1] < landmarks[14][1]
    pinky_up = landmarks[20][1] < landmarks[18][1]
    thumb_up = (
        landmarks[4][0] < landmarks[3][0]
    )  # left thumb → open, right thumb → adjust if mirror reversed

    # Gesture Definition Table
    if index_up and middle_up and not ring_up and not pinky_up:
        return "forward"
    elif all([index_up, middle_up, ring_up, pinky_up, thumb_up]):
        return "backward"
    elif index_up and not any([middle_up, ring_up, pinky_up, thumb_up]):
        return "right"
    elif thumb_up and not any([index_up, middle_up, ring_up, pinky_up]):
        return "left"
    else:
        return "stop"


print("Gesture system ready. Connect to ESP32 Wi-Fi (192.168.4.1)")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    gesture = "stop"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            h, w, _ = frame.shape
            lm = [(int(p.x * w), int(p.y * h)) for p in hand_landmarks.landmark]
            gesture = detect_gesture(lm)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Send to ESP32 only when gesture changes
    if gesture != last_sent and (time.time() - last_time > send_interval):
        cmd = gesture_map[gesture]
        try:
            sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))
            print(f"Sent command: {cmd} ({gesture})")
        except Exception as e:
            print("Send failed:", e)
        last_sent = gesture
        last_time = time.time()

    cv2.putText(
        frame,
        f"Gesture: {gesture}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 100),
        3,
    )
    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
sock.close()
