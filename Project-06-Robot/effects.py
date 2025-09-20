# effects.py

import cv2

TRAIL_LENGTH = 15

def draw_trails(canvas, landmarks, trail_points):
    key_idxs = [11, 12, 13, 14, 15, 16, 23, 24]  # Arms and shoulders

    current = [(landmarks[i].x, landmarks[i].y) for i in key_idxs]
    trail_points.append(current)

    if len(trail_points) > TRAIL_LENGTH:
        trail_points.pop(0)

    h, w, _ = canvas.shape
    for i in range(len(trail_points) - 1):
        alpha = int(255 * (i + 1) / TRAIL_LENGTH)
        for p1, p2 in zip(trail_points[i], trail_points[i+1]):
            x1, y1 = int(p1[0] * w), int(p1[1] * h)
            x2, y2 = int(p2[0] * w), int(p2[1] * h)
            cv2.line(canvas, (x1, y1), (x2, y2), (0, alpha, 255), 2)
