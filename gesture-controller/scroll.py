import cv2
import mediapipe as mp
import pyautogui
import time

# Setup
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
draw = mp.solutions.drawing_utils

scroll_speed = 30  # Lower value for smoother scroll
scroll_delay = 0.02  # Faster refresh (in seconds)
last_scroll_time = 0

def fingers_up(hand):
    tips = [8, 12, 16, 20]
    up = []
    for tip in tips:
        tip_y = hand.landmark[tip].y
        pip_y = hand.landmark[tip - 2].y
        up.append(1 if tip_y < pip_y - 0.015 else 0)
    return up

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        finger_status = fingers_up(hand)
        index_up = finger_status[0]
        middle_up = finger_status[1]

        now = time.time()
        if now - last_scroll_time > scroll_delay:
            if index_up and middle_up:
                pyautogui.scroll(scroll_speed)
                print("↑ Smooth Scroll Up")
            else:
                pyautogui.scroll(-scroll_speed)
                print("↓ Smooth Scroll Down")
            last_scroll_time = now

    cv2.imshow("Smooth Scrolling", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
