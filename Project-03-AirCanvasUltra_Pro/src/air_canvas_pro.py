import cv2
import numpy as np
import mediapipe as mp
from doodle_recognizer import DoodleRecognizer
import time

class AirCanvasPro:
    def __init__(self):
        # Initialize mediapipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Canvas setup
        self.canvas_width, self.canvas_height = 1280, 720
        self.canvas = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.strokes = []
        self.current_stroke = []
        
        # Drawing state
        self.drawing = False
        self.prev_x, self.prev_y = None, None
        self.smoothed_x, self.smoothed_y = None, None
        self.SMOOTHING_FACTOR = 0.6
        
        # Colors and tools
        self.colors = [
            (0, 0, 255),    # Red
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Purple
            (0, 0, 0)       # Black (eraser)
        ]
        self.color_names = ["Red", "Green", "Blue", "Yellow", "Purple", "Eraser"]
        self.current_color_index = 0
        self.brush_size = 7
        
        # UI Elements
        self.palette_height = 80
        self.palette_pos = (50, 50)
        self.palette_button_size = 70  # Increased size
        self.palette_button_margin = 15
        
        # Clear button
        self.clear_button_pos = (self.canvas_width - 200, 50)  # Top right
        self.clear_button_size = (150, 60)
        
        # AI Doodle Recognizer
        self.doodle_recognizer = DoodleRecognizer()
        self.ai_prediction = ""
        self.ai_confidence = 0
        self.ai_active = False
        self.ai_trigger_time = 0
        self.AI_TRIGGER_DURATION = 1.5  # seconds
        
        # Pointer visualization
        self.pointer_radius = 15
        self.pointer_color = (255, 255, 255)
        self.pointer_outline = (0, 0, 0)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
    
    def draw_palette(self, frame):
        """Draw the color palette on the canvas"""
        start_x, start_y = self.palette_pos
        button_size = self.palette_button_size
        
        for i, color in enumerate(self.colors):
            x = start_x + i * (button_size + self.palette_button_margin)
            y = start_y
            
            # Draw color button
            cv2.rectangle(frame, (x, y), (x + button_size, y + button_size), 
                         color, -1)
            
            # Highlight selected color
            if i == self.current_color_index:
                cv2.rectangle(frame, (x-3, y-3), 
                             (x + button_size + 3, y + button_size + 3),
                             (0, 0, 0), 3)
            
            # Add text for eraser
            if i == len(self.colors) - 1:
                cv2.putText(frame, "ERASE", (x + 10, y + button_size//2 + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    def draw_clear_button(self, frame):
        """Draw the clear canvas button"""
        x, y = self.clear_button_pos
        w, h = self.clear_button_size
        cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 200, 200), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
        cv2.putText(frame, "CLEAR ALL", (x + 20, y + h//2 + 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    def draw_pointer(self, frame, x, y):
        """Draw pointer on canvas"""
        cv2.circle(frame, (x, y), self.pointer_radius, 
                  self.pointer_color, -1)
        cv2.circle(frame, (x, y), self.pointer_radius, 
                  self.pointer_outline, 2)
        
        # Draw small inner circle with current color
        current_color = self.colors[self.current_color_index]
        cv2.circle(frame, (x, y), self.pointer_radius//2, 
                  current_color, -1)
    
    def draw_ui(self, frame):
        """Draw UI elements on the canvas"""
        # Draw palette
        self.draw_palette(frame)
        
        # Draw clear button
        self.draw_clear_button(frame)
        
        # Draw current tool info
        cv2.putText(frame, f"Tool: {self.color_names[self.current_color_index]}", 
                   (50, self.canvas_height - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Draw AI instructions
        cv2.putText(frame, "Pinch & Hold to Analyze", 
                   (self.canvas_width - 350, self.canvas_height - 30),  # Bottom right
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 0, 128), 2)
        
        # Draw AI prediction if available
        if self.ai_prediction:
            cv2.putText(frame, f"AI: {self.ai_prediction} ({self.ai_confidence:.0f}%)", 
                        (self.canvas_width - 400, self.canvas_height - 70),  # Above instruction
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 128), 2)
    
    def process_gestures(self, landmarks):
        """Process hand gestures and update drawing state"""
        lm = landmarks.landmark
        fingers = self.fingers_up(lm)
        
        # Get index finger tip position (smoothed)
        index_x = int(lm[8].x * self.canvas_width)
        index_y = int(lm[8].y * self.canvas_height)
        
        # Smooth the coordinates
        if self.smoothed_x is None or self.smoothed_y is None:
            self.smoothed_x, self.smoothed_y = index_x, index_y
        else:
            self.smoothed_x = int(self.SMOOTHING_FACTOR * self.smoothed_x + 
                                (1 - self.SMOOTHING_FACTOR) * index_x)
            self.smoothed_y = int(self.SMOOTHING_FACTOR * self.smoothed_y + 
                                (1 - self.SMOOTHING_FACTOR) * index_y)
        
        # Check for clear button press
        if self.check_clear_button(self.smoothed_x, self.smoothed_y):
            self.clear_canvas()
            return
        
        # Check for color selection in palette
        if not self.drawing:
            self.check_color_selection(self.smoothed_x, self.smoothed_y)
        
        # Drawing logic
        if fingers == [0, 1, 0, 0, 0]:  # Only index finger up
            if not self.drawing:
                self.current_stroke = []
                self.drawing = True
            
            if self.prev_x is not None:
                color = (255, 255, 255) if self.current_color_index == len(self.colors) - 1 else self.colors[self.current_color_index]
                thickness = 20 if self.current_color_index == len(self.colors) - 1 else self.brush_size
                
                cv2.line(self.canvas, (self.prev_x, self.prev_y), 
                        (self.smoothed_x, self.smoothed_y), color, thickness)
                self.current_stroke.append(((self.prev_x, self.prev_y), 
                                          (self.smoothed_x, self.smoothed_y), 
                                          color, thickness))
            
            self.prev_x, self.prev_y = self.smoothed_x, self.smoothed_y
        else:
            if self.drawing:
                self.strokes.append(self.current_stroke)
                self.current_stroke = []
                self.drawing = False
                self.prev_x, self.prev_y = None, None
        
        # Check for AI trigger (thumb and index pinch)
        if self.is_pinch(lm):
            if not self.ai_active:
                if self.ai_trigger_time == 0:
                    self.ai_trigger_time = time.time()
                elif time.time() - self.ai_trigger_time >= self.AI_TRIGGER_DURATION:
                    self.analyze_doodle()
                    self.ai_trigger_time = 0
        else:
            self.ai_trigger_time = 0
    
    def check_clear_button(self, x, y):
        """Check if clear button is pressed"""
        btn_x, btn_y = self.clear_button_pos
        btn_w, btn_h = self.clear_button_size
        
        return (btn_x <= x <= btn_x + btn_w and 
                btn_y <= y <= btn_y + btn_h)
    
    def clear_canvas(self):
        """Clear the entire canvas"""
        self.canvas[:] = 255
        self.strokes = []
        self.current_stroke = []
        self.drawing = False
        self.prev_x, self.prev_y = None, None
        self.ai_prediction = ""
        print("[CLEAR] Canvas cleared")
    
    def check_color_selection(self, x, y):
        """Check if user is selecting a color from the palette"""
        start_x, start_y = self.palette_pos
        button_size = self.palette_button_size
        
        for i in range(len(self.colors)):
            btn_x = start_x + i * (button_size + self.palette_button_margin)
            btn_y = start_y
            
            if (btn_x <= x <= btn_x + button_size and 
                btn_y <= y <= btn_y + button_size):
                self.current_color_index = i
                print(f"[TOOL] Selected: {self.color_names[i]}")
                break
    
    def analyze_doodle(self):
        """Analyze the current drawing with AI"""
        self.ai_active = True
        print("[AI] Analyzing drawing...")
        
        # Save temp image
        temp_path = "temp_doodle.png"
        cv2.imwrite(temp_path, self.canvas)
        
        # Get prediction
        prediction, confidence = self.doodle_recognizer.predict(temp_path)
        self.ai_prediction = prediction
        self.ai_confidence = confidence * 100
        
        # Clean up
        import os
        os.remove(temp_path)
        self.ai_active = False
        print(f"[AI] Prediction: {prediction} ({confidence:.2f} confidence)")
    
    def fingers_up(self, landmarks):
        """Check which fingers are up"""
        tips = [4, 8, 12, 16, 20]
        fingers = []
        
        # Thumb (different logic)
        fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)
        
        # Other fingers
        for tip in tips[1:]:
            fingers.append(1 if landmarks[tip].y < landmarks[tip - 2].y else 0)
        
        return fingers
    
    def is_pinch(self, landmarks):
        """Check if thumb and index finger are pinching"""
        thumb = landmarks[4]
        index = landmarks[8]
        dist = ((thumb.x - index.x)**2 + (thumb.y - index.y)**2)**0.5
        return dist < 0.05
    
    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Flip and convert to RGB
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            results = self.hands.process(rgb)
            
            # Create output canvas
            output = self.canvas.copy()
            self.draw_ui(output)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                        self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2))
                    
                    # Process gestures
                    self.process_gestures(hand_landmarks)
                    
                    # Get pointer position
                    pointer_x = int(hand_landmarks.landmark[8].x * self.canvas_width)
                    pointer_y = int(hand_landmarks.landmark[8].y * self.canvas_height)
                    
                    # Draw pointer on both windows
                    self.draw_pointer(frame, 
                                    int(hand_landmarks.landmark[8].x * frame.shape[1]),
                                    int(hand_landmarks.landmark[8].y * frame.shape[0]))
                    self.draw_pointer(output, pointer_x, pointer_y)
            
            # Show windows
            cv2.imshow("Hand Tracking", frame)
            cv2.imshow("Air Canvas Pro", output)
            
            # Exit conditions
            if (cv2.waitKey(1) & 0xFF == 27 or
                cv2.getWindowProperty("Air Canvas Pro", cv2.WND_PROP_VISIBLE) < 1 or
                cv2.getWindowProperty("Hand Tracking", cv2.WND_PROP_VISIBLE) < 1):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = AirCanvasPro()
    app.run()