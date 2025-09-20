import cv2
import numpy as np
import mediapipe as mp
import time
from datetime import datetime

class FocusDetector:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Metrics
        self.start_time = time.time()
        self.focus_time = 0
        self.distraction_count = 0
        self.productivity_score = 100
        self.distraction_history = []
        self.last_update = time.time()
        
    def detect_distractions(self, frame):
        distractions = []
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Face detection
        face_results = self.face_mesh.process(rgb_frame)
        pose_results = self.pose.process(rgb_frame)
        
        # 1. Looking away detection
        if self.detect_looking_away(face_results):
            distractions.append("looking_away")
            
        # 2. Phone use detection (simplified)
        if self.detect_phone_use(pose_results, face_results):
            distractions.append("phone_use")
            
        # 3. No face detected (away from screen)
        if not face_results.multi_face_landmarks:
            distractions.append("away_from_screen")
            
        return distractions
    
    def detect_looking_away(self, face_results):
        if not face_results.multi_face_landmarks:
            return True
            
        face_landmarks = face_results.multi_face_landmarks[0].landmark
        
        # Simple head position estimation
        nose_tip = face_landmarks[1]  # Nose tip
        left_eye = face_landmarks[33]  # Left eye corner
        right_eye = face_landmarks[263]  # Right eye corner
        
        # Calculate head position
        head_position_x = (left_eye.x + right_eye.x) / 2
        
        # If head is turned significantly
        if abs(head_position_x - 0.5) > 0.3:  # Adjusted threshold
            return True
            
        return False
    
    def detect_phone_use(self, pose_results, face_results):
        if not pose_results.pose_landmarks or not face_results.multi_face_landmarks:
            return False
            
        # Get hand landmarks
        left_wrist = pose_results.pose_landmarks.landmark[15]  # Left wrist
        right_wrist = pose_results.pose_landmarks.landmark[16]  # Right wrist
        
        # Get face position (nose)
        nose = face_results.multi_face_landmarks[0].landmark[1]
        
        # Check if hands are near face
        for wrist in [left_wrist, right_wrist]:
            distance = np.sqrt((wrist.x - nose.x)**2 + (wrist.y - nose.y)**2)
            if distance < 0.2:  # Adjust threshold as needed
                return True
                
        return False
    
    def update_metrics(self, distractions):
        current_time = time.time()
        time_elapsed = current_time - self.last_update
        
        if distractions:
            self.distraction_count += len(distractions)
            # Penalize based on distraction count
            score_deduction = min(50, len(distractions) * 10)
            self.productivity_score = max(0, self.productivity_score - score_deduction)
            
            self.distraction_history.append({
                'timestamp': datetime.now().isoformat(),
                'distractions': distractions,
                'score': self.productivity_score,
                'duration': time_elapsed
            })
        else:
            # Reward focus time
            score_increase = min(5, time_elapsed * 0.1)
            self.productivity_score = min(100, self.productivity_score + score_increase)
            self.focus_time += time_elapsed
            
        self.last_update = current_time
        
        return {
            'productivity_score': round(self.productivity_score, 1),
            'distraction_count': self.distraction_count,
            'focus_time': round(self.focus_time, 1),
            'current_distractions': distractions,
            'session_duration': round(current_time - self.start_time, 1)
        }
    
    def get_session_report(self):
        return {
            'start_time': self.start_time,
            'total_focus_time': self.focus_time,
            'total_distractions': self.distraction_count,
            'final_score': self.productivity_score,
            'distraction_history': self.distraction_history
        }
    
    def reset(self):
        self.__init__()