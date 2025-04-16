# 🤖 Hand Gesture Control Using Python & Mediapipe

Control your PC using just your hand gestures! This project uses your webcam and computer vision to detect hand gestures and perform actions like minimizing/maximizing windows, clicking, and more.

## 📸 Features

- Control the mouse with your index finger
- Double click with a simple pinch gesture
- Minimize windows with a **fist**
- Maximize windows with an **open hand**
- Exit the app by showing **two open hands**
- Smooth performance and fast gesture response

---

## ✋ Supported Gestures

| Gesture | Action |
|--------|--------|
| 👊 **Fist** | Minimizes the active window |
| 🖐️ **Open Hand** | Maximizes the active window to full screen |
| 🤏 **Pinch (Thumb + Index)** | Moves mouse and double-clicks |
| 🖐️🖐️ **Two Open Hands (for 1 sec)** | Exits the application |

---

## 🛠️ Requirements

- Python 3.7+
- OpenCV
- Mediapipe
- PyAutoGUI

Install dependencies using pip:

```bash
pip install opencv-python mediapipe pyautogui

How to Run
Clone the repository:

bash
Copy code
git clone https://github.com/Sun10ny/ml-hand-gesture-control-project.git
cd ml-hand-gesture-control-project
Run the script:

bash
Copy code
python src/pinch_click.py
Grant permission for camera access if prompted.

📂 Project Structure
bash
Copy code
ml-hand-gesture-control-project/
│
├── src/
│   └── pinch_click.py         # Main gesture control code
├── README.md                  # This file
└── requirements.txt           # (Optional) Dependencies

Notes
Works best in good lighting conditions.

Make sure the webcam has a clear view of your hand.

If cursor gets stuck in a corner, it might trigger PyAutoGUI's safety feature. Just move your hand away or disable it in the code (pyautogui.FAILSAFE = False is already set).

Future Ideas
Add swipe gestures for media control (next/previous)

Volume control with pinch zoom gestures

Integration with Smart Home or IoT
