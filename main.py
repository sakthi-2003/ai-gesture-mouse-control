"""Hand gesture mouse controller using OpenCV, MediaPipe, and PyAutoGUI."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

import cv2
import mediapipe as mp
import pyautogui


CAMERA_INDEX = 0
MAX_NUM_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7
CLICK_DISTANCE_PIXELS = 35
CLICK_COOLDOWN_SECONDS = 0.35
SCROLL_DISTANCE_PIXELS = 45
SCROLL_COOLDOWN_SECONDS = 0.08
SCROLL_AMOUNT = 5
POINTER_SMOOTHING = 0.25
WINDOW_NAME = "Hand Gesture Mouse Control"


@dataclass
class Point:
    x: int
    y: int


def calculate_distance(first: Point, second: Point) -> float:
    """Return the Euclidean distance between two image points."""
    return math.hypot(second.x - first.x, second.y - first.y)


def landmark_to_point(landmark, frame_width: int, frame_height: int) -> Point:
    """Convert a normalized MediaPipe landmark to a pixel coordinate."""
    return Point(
        x=int(landmark.x * frame_width),
        y=int(landmark.y * frame_height),
    )


def map_to_screen(point: Point, frame_width: int, frame_height: int) -> Point:
    """Map a camera-frame point to the current screen resolution."""
    screen_width, screen_height = pyautogui.size()
    return Point(
        x=int(screen_width * point.x / frame_width),
        y=int(screen_height * point.y / frame_height),
    )


def smooth_pointer(target: Point, previous: Point | None) -> Point:
    """Smooth pointer movement to reduce jitter from hand tracking noise."""
    if previous is None:
        return target

    return Point(
        x=int(previous.x + (target.x - previous.x) * POINTER_SMOOTHING),
        y=int(previous.y + (target.y - previous.y) * POINTER_SMOOTHING),
    )


def draw_overlay(frame, index_tip: Point | None, is_clicking: bool) -> None:
    """Draw concise status information on the preview window."""
    status = "Click" if is_clicking else "Move"
    color = (0, 200, 0) if is_clicking else (255, 170, 0)

    cv2.putText(
        frame,
        "Pinch thumb + index to click | Press Q to quit",
        (20, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        f"Mode: {status}",
        (20, 64),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2,
        cv2.LINE_AA,
    )

    if index_tip is not None:
        cv2.circle(frame, (index_tip.x, index_tip.y), 10, color, cv2.FILLED)


def run_mouse_controller() -> None:
    """Start the camera loop and control the mouse from hand landmarks."""
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Could not open the webcam. Check camera permissions.")

    previous_pointer: Point | None = None
    last_click_time = 0.0
    last_scroll_time = 0.0

    try:
        with mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE,
        ) as hands:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                frame = cv2.flip(frame, 1)
                frame_height, frame_width, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                index_tip = None
                is_clicking = False

                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                    )

                    landmarks = hand_landmarks.landmark
                    index_tip = landmark_to_point(
                        landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP],
                        frame_width,
                        frame_height,
                    )
                    thumb_tip = landmark_to_point(
                        landmarks[mp_hands.HandLandmark.THUMB_TIP],
                        frame_width,
                        frame_height,
                    )
                    middle_tip = landmark_to_point(
                        landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
                        frame_width,
                        frame_height,
                    )

                    pointer_target = map_to_screen(index_tip, frame_width, frame_height)
                    pointer = smooth_pointer(pointer_target, previous_pointer)
                    pyautogui.moveTo(pointer.x, pointer.y)
                    previous_pointer = pointer

                    pinch_distance = calculate_distance(index_tip, thumb_tip)
                    now = time.monotonic()

                    if (
                        pinch_distance < CLICK_DISTANCE_PIXELS
                        and now - last_click_time >= CLICK_COOLDOWN_SECONDS
                    ):
                        pyautogui.click()
                        last_click_time = now
                        is_clicking = True

                    scroll_gap = middle_tip.y - index_tip.y
                    if (
                        not is_clicking
                        and abs(scroll_gap) > SCROLL_DISTANCE_PIXELS
                        and now - last_scroll_time >= SCROLL_COOLDOWN_SECONDS
                    ):
                        direction = 1 if scroll_gap < 0 else -1
                        pyautogui.scroll(direction * SCROLL_AMOUNT)
                        last_scroll_time = now

                draw_overlay(frame, index_tip, is_clicking)
                cv2.imshow(WINDOW_NAME, frame)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()


def main() -> None:
    run_mouse_controller()


if __name__ == "__main__":
    main()
