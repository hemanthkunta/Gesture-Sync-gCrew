import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import time

# --- Configuration ---
WEBCAM_INDEX = 0         # 0 is usually the built-in webcam
FRAME_WIDTH = 640       # Processing resolution (width) - Lower can be faster
FRAME_HEIGHT = 480      # Processing resolution (height)
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size() # Get screen dimensions

# --- Gesture Parameters (Tune these!) ---
CURSOR_SMOOTHING = 5    # Higher value = smoother but slower cursor movement
CLICK_DISTANCE_THRESHOLD = 35 # Pixel distance between thumb and index finger to trigger click
MOVEMENT_DEADZONE_PERCENT = 0.15 # Percentage of frame edge to ignore for movement (reduces edge snapping)
DEBOUNCE_TIME = 0.3     # Seconds to wait between clicks

# --- Initialization ---
cap = cv2.VideoCapture(WEBCAM_INDEX)
if not cap.isOpened():
    print(f"Error: Could not open webcam index {WEBCAM_INDEX}")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

mp_hands = mp.solutions.hands
# Adjust confidence for better detection/tracking balance if needed
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

prev_cursor_x, prev_cursor_y = 0, 0 # For smoothing
is_clicking = False                # Click state flag
last_click_time = 0                # For debouncing

# Calculate movement boundaries based on deadzone
move_min_x = int(FRAME_WIDTH * MOVEMENT_DEADZONE_PERCENT)
move_max_x = int(FRAME_WIDTH * (1 - MOVEMENT_DEADZONE_PERCENT))
move_min_y = int(FRAME_HEIGHT * MOVEMENT_DEADZONE_PERCENT)
move_max_y = int(FRAME_HEIGHT * (1 - MOVEMENT_DEADZONE_PERCENT))

print("Starting Hand Tracking Control...")
print(f"Screen Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"Move cursor with index finger (Landmark 8).")
print(f"Click by bringing thumb (4) and index (8) tips together.")
print("Press 'q' to quit.")

# --- Main Loop ---
while True:
    success, img = cap.read()
    if not success:
        print("Warning: Failed to grab frame.")
        time.sleep(0.1) # Wait a bit before retrying
        continue

    # 1. Flip the image horizontally (mirror view)
    img = cv2.flip(img, 1)

    # 2. Convert BGR image to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 3. Process the image to find hands
    results = hands.process(img_rgb)

    # 4. If hands are detected
    if results.multi_hand_landmarks:
        # Use the first detected hand
        hand_landmarks = results.multi_hand_landmarks[0]

        # Draw landmarks on the original (BGR) image for visualization
        mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Get landmark coordinates (normalized 0-1 initially)
        landmarks = {}
        for id, lm in enumerate(hand_landmarks.landmark):
            # Convert normalized coordinates to pixel coordinates in the frame
            cx, cy = int(lm.x * FRAME_WIDTH), int(lm.y * FRAME_HEIGHT)
            landmarks[id] = (cx, cy)

        # --- Cursor Movement (using Index Finger Tip - Landmark 8) ---
        if 8 in landmarks:
            index_x, index_y = landmarks[8]
            cv2.circle(img, (index_x, index_y), 10, (255, 0, 255), cv2.FILLED) # Highlight tracking point

            # Map frame coordinates to screen coordinates with deadzone and interpolation
            screen_x = np.interp(index_x, (move_min_x, move_max_x), (0, SCREEN_WIDTH))
            screen_y = np.interp(index_y, (move_min_y, move_max_y), (0, SCREEN_HEIGHT))

            # Clamp values to screen boundaries just in case
            screen_x = max(0, min(SCREEN_WIDTH - 1, screen_x))
            screen_y = max(0, min(SCREEN_HEIGHT - 1, screen_y))

            # Smoothing
            current_cursor_x = prev_cursor_x + (screen_x - prev_cursor_x) / CURSOR_SMOOTHING
            current_cursor_y = prev_cursor_y + (screen_y - prev_cursor_y) / CURSOR_SMOOTHING

            # Move mouse (use duration=0 for fastest response)
            pyautogui.moveTo(int(current_cursor_x), int(current_cursor_y), duration=0)

            # Update previous location for next frame's smoothing
            prev_cursor_x, prev_cursor_y = current_cursor_x, current_cursor_y

        # --- Clicking Gesture (Thumb Tip - 4 and Index Finger Tip - 8) ---
        if 4 in landmarks and 8 in landmarks:
            thumb_x, thumb_y = landmarks[4]
            index_x, index_y = landmarks[8] # Get again (or use from above)

            # Calculate distance between thumb and index finger tips
            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 3) # Draw line between fingers

            current_time = time.time()
            # Check if distance is below threshold and enough time has passed since last click
            if distance < CLICK_DISTANCE_THRESHOLD:
                cv2.circle(img, (index_x, index_y), 10, (0, 255, 0), cv2.FILLED) # Green circle when close enough
                if not is_clicking and (current_time - last_click_time > DEBOUNCE_TIME):
                    print("CLICK!")
                    pyautogui.click()
                    is_clicking = True         # Set flag to prevent immediate re-clicks
                    last_click_time = current_time
            else:
                 # Reset click flag only when fingers are apart
                 is_clicking = False


    # 5. Display the image
    cv2.imshow("Hand Tracking Control", img)

    # 6. Check for exit key ('q')
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
print("Exiting...")
cap.release()
cv2.destroyAllWindows()
hands.close()