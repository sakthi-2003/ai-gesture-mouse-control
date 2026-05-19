# Hand Gesture Mouse Control

A real-time computer vision project that lets you control the mouse pointer using hand gestures captured through a webcam. The application uses MediaPipe for hand landmark detection, OpenCV for video processing, and PyAutoGUI for mouse control.

## Features

- Move the cursor with the index finger.
- Perform left clicks using a thumb-and-index pinch gesture.
- Scroll using index and middle finger positioning.
- Smooth cursor movement to reduce tracking jitter.
- On-screen preview with hand landmarks and status feedback.
- Safe cleanup for camera and OpenCV windows when the app exits.

## Tech Stack

- Python
- OpenCV
- MediaPipe
- PyAutoGUI

## Project Structure

```text
ai-gesture-mouse-control/
|-- main.py
|-- requirements.txt
|-- README.md
|-- .gitignore
```

## Installation

```bash
git clone https://github.com/sakthi-2003/ai-gesture-mouse-control.git
cd ai-gesture-mouse-control
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Allow webcam access when prompted. A preview window will open after the camera starts.

## Gesture Controls

| Gesture | Action |
| --- | --- |
| Index finger movement | Move cursor |
| Thumb + index pinch | Left click |
| Index and middle finger vertical movement | Scroll |
| Q or Esc key | Exit application |

## How It Works

1. OpenCV captures frames from the webcam.
2. MediaPipe detects hand landmarks in each frame.
3. The index finger landmark is mapped to screen coordinates.
4. A smoothing function reduces pointer jitter.
5. The distance between thumb and index finger triggers clicks.
6. Index and middle finger positions are used for scrolling.

## Requirements

Install dependencies from `requirements.txt`:

```bash
opencv-python
mediapipe
pyautogui
```

## Future Improvements

- Add drag-and-drop gesture support.
- Add gesture-based mode switching.
- Add a demo GIF or screenshot.
- Add configurable sensitivity and gesture thresholds.

## Author

Sakthi
