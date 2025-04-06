import cv2
import mediapipe as mp
import pyautogui
import time
import math

# Setup
cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
draw = mp.solutions.drawing_utils

dragging = False
drag_threshold = 0.05

# Smoothing variables
prev_x, prev_y = 0, 0
smooth_factor = 5  # Higher = smoother, but more delay

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # Get landmarks
        thumb = hand.landmark[4]
        index = hand.landmark[8]

        # Convert to screen coords
        raw_x, raw_y = index.x * screen_w, index.y * screen_h

        # Smooth cursor movement
        curr_x = prev_x + (raw_x - prev_x) / smooth_factor
        curr_y = prev_y + (raw_y - prev_y) / smooth_factor
        pyautogui.moveTo(curr_x, curr_y)
        prev_x, prev_y = curr_x, curr_y

        # Distance for drag
        thumb_pos = (thumb.x * frame_w, thumb.y * frame_h)
        index_pos = (index.x * frame_w, index.y * frame_h)
        dist = distance(thumb_pos, index_pos)

        # Dragging logic
        if dist < drag_threshold * frame_w:
            if not dragging:
                pyautogui.mouseDown()
                dragging = True
                print("🟢 Drag Started")
        else:
            if dragging:
                pyautogui.mouseUp()
                dragging = False
                print("🔴 Drag Released")

        # Debug marker
        cv2.circle(frame, (int(index.x * frame_w), int(index.y * frame_h)), 10, (0, 255, 255), -1)

    cv2.imshow("Accurate Drag & Drop", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
