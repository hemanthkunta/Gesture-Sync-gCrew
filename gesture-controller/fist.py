import cv2
import mediapipe as mp
import pyautogui
import time
from collections import deque

# Setup
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
draw = mp.solutions.drawing_utils

# Alt+Tab state
alt_tab_active = False
last_switch_time = 0
switch_cooldown = 0.6

# Motion buffer
x_buffer = deque(maxlen=5)
hand_lost_counter = 0
max_lost_frames = 10

def is_fist(hand):
    tips = [8, 12, 16, 20]
    return all(hand.landmark[tip].y > hand.landmark[tip - 2].y for tip in tips)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand_lost_counter = 0
        hand = results.multi_hand_landmarks[0]
        draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        wrist_x = hand.landmark[0].x
        x_buffer.append(wrist_x)

        if is_fist(hand):
            if not alt_tab_active:
                print("[FIST] → Alt+Tab start")
                pyautogui.keyDown('alt')
                pyautogui.press('tab')
                alt_tab_active = True
                last_switch_time = time.time()
                x_buffer.clear()
                x_buffer.append(wrist_x)
            else:
                if len(x_buffer) >= 5:
                    dx = x_buffer[-1] - x_buffer[0]
                    if abs(dx) > 0.05 and (time.time() - last_switch_time > switch_cooldown):
                        if dx > 0:
                            print("→ Moving Right")
                            pyautogui.press('right')
                        else:
                            print("← Moving Left")
                            pyautogui.press('left')
                        last_switch_time = time.time()
                        x_buffer.clear()
                        x_buffer.append(wrist_x)
        else:
            if alt_tab_active:
                print("[OPEN HAND] → Select window")
                pyautogui.keyUp('alt')
                alt_tab_active = False
                x_buffer.clear()
                time.sleep(0.4)
    else:
        hand_lost_counter += 1
        if alt_tab_active and hand_lost_counter >= max_lost_frames:
            print("[HAND LOST] → Release Alt")
            pyautogui.keyUp('alt')
            alt_tab_active = False
            x_buffer.clear()

    cv2.imshow("Alt+Tab Gesture", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
