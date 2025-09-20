# clone_engine.py

import cv2
import numpy as np

POSE_CONNECTIONS = [
    (11, 13), (13, 15),     # Left arm
    (12, 14), (14, 16),     # Right arm
    (11, 12),               # Shoulders
    (23, 24),               # Hips
    (11, 23), (12, 24),     # Torso
    (23, 25), (25, 27),     # Left leg
    (24, 26), (26, 28)      # Right leg
]

def draw_clone(canvas, landmarks, frame_shape):
    h, w, _ = frame_shape

    points = []
    for lm in landmarks:
        x, y = int(lm.x * w), int(lm.y * h)
        points.append((x, y))

    for start, end in POSE_CONNECTIONS:
        x1, y1 = points[start]
        x2, y2 = points[end]
        cv2.line(canvas, (x1, y1), (x2, y2), (0, 255, 255), 3, cv2.LINE_AA)

    for x, y in points:
        cv2.circle(canvas, (x, y), 6, (255, 255, 255), -1)
