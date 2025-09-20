import numpy as np
from collections import deque

class MotionTracker:
    def __init__(self):
        self.trajectory = deque(maxlen=30)  # Stores (x,y,timestamp)
        self.current_gesture = None
        
    def update(self, hand_landmarks, timestamp):
        # Track wrist position (landmark 0)
        wrist = (hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y)
        self.trajectory.append((*wrist, timestamp))
        
    def analyze_motion(self):
        if len(self.trajectory) < 10:
            return None
            
        # Convert to numpy array
        points = np.array(self.trajectory)
        
        # Calculate motion features
        displacement = np.linalg.norm(points[-1][:2] - points[0][:2])
        duration = points[-1][2] - points[0][2]
        speed = displacement / duration
        
        # Direction analysis
        x_diff = points[-1][0] - points[0][0]
        y_diff = points[-1][1] - points[0][1]
        
        # Pattern recognition
        if self._is_circular(points[:,:2]):
            return "circular"
        elif abs(y_diff) > 0.3 and speed > 0.5:
            return "downward" if y_diff > 0 else "upward"
        elif abs(x_diff) > 0.3:
            return "left_to_right" if x_diff > 0 else "right_to_left"
        
        return None
    
    def _is_circular(self, points):
        # Simplified circle detection
        centroid = np.mean(points, axis=0)
        radii = np.linalg.norm(points - centroid, axis=1)
        return np.std(radii) < 0.1  # Consistent radius