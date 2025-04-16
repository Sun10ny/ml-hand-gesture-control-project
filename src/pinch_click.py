import cv2
import mediapipe as mp
import pyautogui
import ctypes
import time

last_minimize_time = 0
last_maximize_time = 0
minimize_delay = 2
maximize_delay = 2

prev_x, prev_y = 0, 0
smoothening = 1  # Reduced for faster cursor response
clicking = False
click_cooldown = 0.6
last_click_time = 0
exit_start_time = None

pyautogui.FAILSAFE = False  # Disable PyAutoGUI fail-safe

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def initialize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    print("Webcam is now running. Show 2 open palms for 1 sec to exit.")
    return cap

def is_fist(hand_landmarks):
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    finger_pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP
    ]
    return all(hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip].y for tip, pip in zip(finger_tips, finger_pips))

def is_open_hand(hand_landmarks):
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    finger_pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP
    ]
    return all(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y for tip, pip in zip(finger_tips, finger_pips))

def count_extended_fingers(hand_landmarks):
    extended = 0
    tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP
    ]
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            extended += 1
    return extended

def detect_click_gesture(hand_landmarks, frame_shape):
    global prev_x, prev_y, clicking, last_click_time
    h, w, _ = frame_shape
    screen_w, screen_h = pyautogui.size()

    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
    screen_x = int(index_tip.x * screen_w)
    screen_y = int(index_tip.y * screen_h)

    curr_x = prev_x + (screen_x - prev_x) / smoothening
    curr_y = prev_y + (screen_y - prev_y) / smoothening
    pyautogui.moveTo(curr_x, curr_y)
    prev_x, prev_y = curr_x, curr_y

    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5 * w
    current_time = time.time()

    if distance < 25 and not clicking and (current_time - last_click_time) > click_cooldown:
        clicking = True
        pyautogui.doubleClick()
        last_click_time = current_time
        return (index_x, index_y)
    elif distance >= 25:
        clicking = False

    return None

def process_frame(frame, hands_detector):
    global last_minimize_time, last_maximize_time
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(rgb_frame)

    open_palms = 0
    hand_count = 0

    if results.multi_hand_landmarks:
        hand_count = len(results.multi_hand_landmarks)

        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            click_point = detect_click_gesture(hand_landmarks, frame.shape)
            if click_point:
                cv2.circle(frame, click_point, 10, (0, 255, 0), -1)

            current_time = time.time()

            if is_fist(hand_landmarks):
                if current_time - last_minimize_time > minimize_delay:
                    print("Fist detected! Minimizing window...")
                    pyautogui.hotkey('win', 'down')
                    pyautogui.hotkey('win', 'down')
                    last_minimize_time = current_time

            elif is_open_hand(hand_landmarks):
                open_palms += 1
                if current_time - last_maximize_time > maximize_delay:
                    print("Open hand detected! Maximizing window...")
                    pyautogui.hotkey('win', 'up')  # Maximize only once
                    last_maximize_time = current_time

    return frame, hand_count, open_palms

def should_exit_with_two_open_palms(open_palms):
    global exit_start_time
    if open_palms >= 2:
        if exit_start_time is None:
            exit_start_time = time.time()
        elif time.time() - exit_start_time > 1:
            return True
    else:
        exit_start_time = None
    return False

def main():
    cap = initialize_camera()
    if cap is None:
        return

    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.9, min_tracking_confidence=0.9)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            processed_frame, hand_count, open_palms = process_frame(frame, hands)
            cv2.imshow("Hand Gesture Detection", processed_frame)

            if should_exit_with_two_open_palms(open_palms):
                print("Two open palms detected for 1 second. Exiting...")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Pressed 'q'. Exiting...")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam released and windows closed.")

if __name__ == "__main__":
    main()
