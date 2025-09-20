import cv2
import time
from motion_analyzer import MotionTracker
from gesture_database import GESTURE_LIBRARY

class SignTranslator:
    def __init__(self):
        self.mp_hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.9,
            min_tracking_confidence=0.7
        )
        self.tracker = MotionTracker()
        self.current_phrase = []
        self.last_detection_time = time.time()
        
    def process_frame(self, frame):
        # Hand detection
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(rgb)
        
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # 1. Track motion
                self.tracker.update(landmarks, time.time())
                
                # 2. Detect static features
                hand_shape = self._get_hand_shape(landmarks)
                location = self._get_hand_location(landmarks, frame.shape)
                
                # 3. Match against gesture library
                detected_word = self._match_gesture(hand_shape, location)
                
                if detected_word:
                    self._handle_detection(detected_word)
                    
                # Visual feedback
                self._draw_gesture_info(frame, detected_word)
        
        return frame
    
    def _match_gesture(self, shape, location):
        motion_pattern = self.tracker.analyze_motion()
        
        for word, config in GESTURE_LIBRARY.items():
            # Check static gestures
            if "hand_shape" in config and config["hand_shape"] == shape:
                if "location" not in config or config["location"] == location:
                    return word
            
            # Check motion gestures
            if "sequence" in config:
                if self._match_sequence(config["sequence"], shape, motion_pattern):
                    return word
        return None
    
    def _draw_gesture_info(self, frame, word):
        # Draw motion trail
        if len(self.tracker.trajectory) > 1:
            for i in range(1, len(self.tracker.trajectory)):
                pt1 = self._landmark_to_pixel(self.tracker.trajectory[i-1], frame.shape)
                pt2 = self._landmark_to_pixel(self.tracker.trajectory[i], frame.shape)
                cv2.line(frame, pt1, pt2, (0,255,255), 2)
        
        # Display detected word
        if word:
            cv2.putText(frame, f"Detected: {word}", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 3)