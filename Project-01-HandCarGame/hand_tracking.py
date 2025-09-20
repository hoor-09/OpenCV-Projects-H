import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Webcam capture
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Detect hand
        results = hands.process(image_rgb)

        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=7),  # Dots
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=7))  # Lines


                # Draw node numbers
                for i, landmark in enumerate(hand_landmarks.landmark):
                    h, w, _ = image.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.putText(image, str(i), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX,
                                0.4, (0, 255, 0), 1)

        cv2.imshow('Hand Tracking', image)

        if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
            break

cap.release()
cv2.destroyAllWindows()
