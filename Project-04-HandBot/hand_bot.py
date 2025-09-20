import cv2
import mediapipe as mp
import numpy as np
from gestures import GestureRecognizer
from robot_utils import Robot

def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.5)
    
    recognizer = GestureRecognizer()
    robot = Robot()
    
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        robot_canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                gesture = recognizer.recognize(hand_landmarks)
                robot.update(gesture)
                
                # Display debug info
                cv2.putText(frame, f"Gesture: {gesture}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            robot.update("neutral")
        
        robot.draw(robot_canvas)
        
        # Display mood text
        mood_text = robot.state.upper()
        text_size = cv2.getTextSize(mood_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = (robot_canvas.shape[1] - text_size[0]) // 2
        cv2.putText(robot_canvas, mood_text, (text_x, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        cv2.imshow('Hand Gestures', frame)
        cv2.imshow('Robot', robot_canvas)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()