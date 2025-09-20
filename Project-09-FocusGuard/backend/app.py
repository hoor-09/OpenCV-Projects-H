from flask import Flask, jsonify, request
import cv2
import base64
import numpy as np
import time
from datetime import datetime
import mediapipe as mp

app = Flask(__name__)

# Add CORS headers manually for local development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

class FocusDetector:
    def __init__(self):
        # Initialize MediaPipe solutions
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
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
        self.last_face_detection = time.time()
        
    def detect_distractions(self, frame):
        distractions = []
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Face detection for looking away
        face_results = self.face_mesh.process(rgb_frame)
        
        # Hand detection for phone use
        hand_results = self.hands.process(rgb_frame)
        
        # 1. No face detected (away from screen)
        if not face_results.multi_face_landmarks:
            if time.time() - self.last_face_detection > 2:  # Only after 2 seconds
                distractions.append("away_from_screen")
            return distractions
        else:
            self.last_face_detection = time.time()
        
        # 2. Looking away detection
        face_landmarks = face_results.multi_face_landmarks[0].landmark
        
        # Use nose and eye landmarks to detect head orientation
        nose_tip = face_landmarks[1]
        left_eye_inner = face_landmarks[133]
        right_eye_inner = face_landmarks[362]
        
        # Calculate head position
        head_center_x = (left_eye_inner.x + right_eye_inner.x) / 2
        head_offset = abs(head_center_x - 0.5)  # 0.5 is center
        
        if head_offset > 0.3:  # Head turned significantly
            distractions.append("looking_away")
        
        # 3. Phone use detection (hands near face)
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Get wrist position
                wrist = hand_landmarks.landmark[0]
                
                # Check if hand is near face
                hand_face_distance = abs(wrist.x - nose_tip.x) + abs(wrist.y - nose_tip.y)
                
                if hand_face_distance < 0.3:  # Hand is close to face
                    distractions.append("phone_use")
                    break
        
        # 4. Yawning detection (mouth openness)
        mouth_top = face_landmarks[13]
        mouth_bottom = face_landmarks[14]
        mouth_openness = abs(mouth_bottom.y - mouth_top.y)
        
        if mouth_openness > 0.1:  # Mouth is open
            distractions.append("yawning")
        
        return distractions
    
    def update_metrics(self, distractions):
        current_time = time.time()
        time_elapsed = current_time - self.last_update
        
        if distractions:
            self.distraction_count += len(distractions)
            score_deduction = min(30, len(distractions) * 8)
            self.productivity_score = max(0, self.productivity_score - score_deduction)
            
            self.distraction_history.append({
                'timestamp': datetime.now().isoformat(),
                'distractions': distractions,
                'score': self.productivity_score,
                'duration': time_elapsed
            })
        else:
            # Gradual score recovery when focused
            score_increase = min(10, time_elapsed * 2)
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

# Global detector instance
detector = FocusDetector()

@app.route('/')
def index():
    return jsonify({"message": "FocusGuard API is running!", "status": "ready"})

@app.route('/api/process-frame', methods=['POST'])
def process_frame():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
            
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid image data"}), 400
        
        # Detect distractions
        distractions = detector.detect_distractions(frame)
        
        # Update metrics
        metrics = detector.update_metrics(distractions)
        
        return jsonify({
            "success": True,
            "metrics": metrics,
            "distractions": distractions,
            "message": "Frame processed successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "message": "Processing failed"}), 500

@app.route('/api/session-report', methods=['GET'])
def get_session_report():
    try:
        report = detector.get_session_report()
        return jsonify({
            "success": True,
            "report": report,
            "message": "Session report generated"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    try:
        detector.reset()
        return jsonify({
            "success": True,
            "message": "Session reset successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "FocusGuard API",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = 5001
    print(f"🚀 Starting FocusGuard server on http://localhost:{port}")
    print(f"📊 Open frontend/index.html in your browser")
    print(f"🔧 Real-time face and hand detection enabled")
    print(f"❤️  Health check: http://localhost:{port}/api/health")
    app.run(debug=True, port=port, host='0.0.0.0')