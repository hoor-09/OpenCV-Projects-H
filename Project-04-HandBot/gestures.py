import math

class GestureRecognizer:
    def __init__(self):
        self.prev_gesture = "neutral"
        self.gesture_frames = 0
        self.gesture_threshold = 5  # Number of consistent frames to confirm gesture

    def recognize(self, landmarks):
        if not landmarks:
            self.prev_gesture = "neutral"
            return "neutral"

        coords = [(lm.x, lm.y, lm.z) for lm in landmarks.landmark]
        current_gesture = self._classify_gesture(coords)

        # Only change gesture if we've seen it consistently
        if current_gesture == self.prev_gesture:
            self.gesture_frames += 1
        else:
            self.gesture_frames = 1
            self.prev_gesture = current_gesture

        if self.gesture_frames >= self.gesture_threshold:
            return current_gesture
        return "neutral"

    def _classify_gesture(self, coords):
        # Calculate finger states
        thumb_up = self._is_thumb_up(coords)
        fingers_extended = [self._is_finger_extended(coords, i) for i in range(4)]
        
        # Count extended fingers (excluding thumb)
        extended_count = sum(fingers_extended)
        
        # Gesture recognition logic
        if thumb_up and extended_count == 0:
            return "happy"
        elif extended_count == 0:
            return "angry"
        elif extended_count == 2 and fingers_extended[0] and fingers_extended[1]:  # Index+Middle
            return "dance"
        elif extended_count == 2 and fingers_extended[0] and fingers_extended[3]:  # Index+Pinky
            return "rock"
        elif extended_count == 1 and fingers_extended[0]:  # Index only
            return "point"
        elif extended_count == 4:  # All fingers
            return "wave"
        return "neutral"

    def _is_thumb_up(self, coords):
        thumb_tip = coords[4]
        thumb_ip = coords[3]
        thumb_mcp = coords[2]
        
        # Check vertical position and angle
        is_up = thumb_tip[1] < thumb_ip[1]
        angle = self._calculate_angle(thumb_mcp, thumb_ip, thumb_tip)
        return is_up and angle > 150

    def _is_finger_extended(self, coords, finger_idx):
        # finger_idx: 0=Index, 1=Middle, 2=Ring, 3=Pinky
        tip_idx = 8 + finger_idx * 4
        dip_idx = tip_idx - 1
        pip_idx = tip_idx - 2
        
        tip = coords[tip_idx]
        pip = coords[pip_idx]
        
        # Check if finger is extended (tip above PIP)
        return tip[1] < pip[1]

    def _calculate_angle(self, a, b, c):
        ba = (a[0]-b[0], a[1]-b[1], a[2]-b[2])
        bc = (c[0]-b[0], c[1]-b[1], c[2]-b[2])
        
        dot_product = ba[0]*bc[0] + ba[1]*bc[1] + ba[2]*bc[2]
        mag_ba = math.sqrt(ba[0]**2 + ba[1]**2 + ba[2]**2)
        mag_bc = math.sqrt(bc[0]**2 + bc[1]**2 + bc[2]**2)
        
        angle = math.acos(min(1, max(-1, dot_product / (mag_ba * mag_bc))))
        return math.degrees(angle)