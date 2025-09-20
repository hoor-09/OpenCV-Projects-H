import cv2
import mediapipe as mp
import numpy as np
from letters import LETTER_MAPPINGS

class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,  # Detect both hands
            min_detection_confidence=0.8,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_letter = None
        self.letter_stable_frames = 0
        self.stability_threshold = 5  # Require 5 consistent frames

    def detect_hands(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results

    def _get_finger_state(self, landmarks, tip_idx, pip_idx):
        return landmarks[tip_idx].y < landmarks[pip_idx].y

    def classify_gesture(self, landmarks):
        # Finger states (True = extended, False = bent)
        thumb_up = self._get_finger_state(landmarks, 4, 3)
        index_up = self._get_finger_state(landmarks, 8, 6)
        middle_up = self._get_finger_state(landmarks, 12, 10)
        ring_up = self._get_finger_state(landmarks, 16, 14)
        pinky_up = self._get_finger_state(landmarks, 20, 18)

        # Space detection (open palm)
        if all([index_up, middle_up, ring_up, pinky_up]) and not thumb_up:
            return " "

        # Letter classification
        if thumb_up and not any([index_up, middle_up, ring_up, pinky_up]):
            current_letter = "A"
        elif index_up and not any([middle_up, ring_up, pinky_up]):
            current_letter = "B" if not thumb_up else "D"
        # ... (add all other letter conditions from LETTER_MAPPINGS)
        else:
            current_letter = None

        # Stability check
        if current_letter == self.prev_letter:
            self.letter_stable_frames += 1
        else:
            self.letter_stable_frames = 0
            self.prev_letter = current_letter

        return current_letter if self.letter_stable_frames >= self.stability_threshold else None