# main.py

import cv2
import mediapipe as mp
import numpy as np
from clone_engine import draw_clone
from effects import draw_trails

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)
trail_points = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    clone_canvas = np.zeros_like(frame)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        draw_clone(clone_canvas, landmarks, frame.shape)
        draw_trails(clone_canvas, landmarks, trail_points)

        # Optional: draw landmarks on webcam
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Show both windows
    cv2.imshow("Webcam Feed", frame)
    cv2.imshow("Cyber Clone", clone_canvas)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
