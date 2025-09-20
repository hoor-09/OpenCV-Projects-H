import cv2
import numpy as np
import mediapipe as mp
import random
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Game constants
TABLE_WIDTH = 1000
TABLE_HEIGHT = 500
PUCK_RADIUS = 20
PADDLE_RADIUS = 30
GOAL_WIDTH = 100
GOAL_HEIGHT = 30
MAX_SCORE = 3
PADDLE_MOVEMENT_RANGE = 200

# SPEED BOOST CONSTANTS - ADD AT TOP
PUCK_SPEED_MULTIPLIER = 1.8     # Increase base puck speed
PUCK_COLLISION_BOOST = 1.4      # More speed on paddle hits
PUCK_MAX_SPEED = 25             # Higher maximum speed
PADDLE_RESPONSIVENESS = 2.5     # Faster paddle movement
PADDLE_MOVEMENT_RANGE = 280     # More range for paddles

class Puck:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = TABLE_WIDTH // 2
        self.y = TABLE_HEIGHT // 2
        base_speed = 14 * PUCK_SPEED_MULTIPLIER
        self.speed_x = random.choice([-12, -11, -10, 10, 11, 12])
        self.speed_y = random.choice([-9, -8, -7, 7, 8, 9])
        self.color = (255, 50, 50)
        self.trail = []
        
    def update(self, paddle1, paddle2):
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.trail.append((self.x, self.y))
        
        self.x += self.speed_x
        self.y += self.speed_y
        
        if self.y - PUCK_RADIUS <= 0:
            self.y = PUCK_RADIUS
            self.speed_y = abs(self.speed_y) * 1.15  # Energy boost on bounce
        elif self.y + PUCK_RADIUS >= TABLE_HEIGHT:
            self.y = TABLE_HEIGHT - PUCK_RADIUS
            self.speed_y = -abs(self.speed_y) * 1.15
            
        self.check_paddle_collision(paddle1)
        self.check_paddle_collision(paddle2)
        
        return self.check_goals()
    
    def check_paddle_collision(self, paddle):
        dist = math.sqrt((self.x - paddle.x)**2 + (self.y - paddle.y)**2)
        if dist < PUCK_RADIUS + PADDLE_RADIUS:
            angle = math.atan2(self.y - paddle.y, self.x - paddle.x)
            speed = math.sqrt(self.speed_x**2 + self.speed_y**2) * 1.50
            speed = min(speed, 20)
            
            self.speed_x = speed * math.cos(angle)
            self.speed_y = speed * math.sin(angle)
            
            overlap = PUCK_RADIUS + PADDLE_RADIUS - dist + 1
            self.x += overlap * math.cos(angle)
            self.y += overlap * math.sin(angle)
    
    def check_goals(self):
        if self.x - PUCK_RADIUS <= 0:
            if TABLE_HEIGHT//2 - GOAL_HEIGHT//2 <= self.y <= TABLE_HEIGHT//2 + GOAL_HEIGHT//2:
                return 2
        elif self.x + PUCK_RADIUS >= TABLE_WIDTH:
            if TABLE_HEIGHT//2 - GOAL_HEIGHT//2 <= self.y <= TABLE_HEIGHT//2 + GOAL_HEIGHT//2:
                return 1
        return 0

class Paddle:
    def __init__(self, base_x, is_left=True):
        self.base_x = base_x
        self.x = base_x
        self.y = TABLE_HEIGHT // 2
        self.is_left = is_left
        self.color = (0, 255, 0) if is_left else (0, 0, 255)
        self.target_x = base_x  # For instant response
        
    def update(self, x, y):
        if self.is_left:
            self.x = max(50, min(self.base_x + PADDLE_MOVEMENT_RANGE, x))
        else:
            self.x = min(TABLE_WIDTH - 50, max(self.base_x - PADDLE_MOVEMENT_RANGE, x))
        
        self.y = max(PADDLE_RADIUS, min(TABLE_HEIGHT - PADDLE_RADIUS, y))

class HockeyGame:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        
        self.puck = Puck()
        self.paddle1 = Paddle(100, True)
        self.paddle2 = Paddle(TABLE_WIDTH - 100, False)
        
        self.score1 = 0
        self.score2 = 0
        self.game_over = False
        self.winner = None
        self.game_started = False  # Added game state
        
    def detect_hands(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hand_positions = [None, None]
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                index_tip = hand_landmarks.landmark[8]
                h, w, _ = frame.shape
                x_pos = int(index_tip.x * w)
                y_pos = int(index_tip.y * h)
                
                if "Left" in handedness.classification[0].label:
                    hand_positions[0] = (x_pos, y_pos)
                else:
                    hand_positions[1] = (x_pos, y_pos)
                
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                
                cv2.circle(frame, (x_pos, y_pos), 12, (0, 255, 255), -1)
                cv2.circle(frame, (x_pos, y_pos), 6, (0, 0, 0), -1)
        
        return hand_positions
    
    def draw_start_screen(self, frame):
        """Draw the start menu screen"""
        # Create a dark overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw title
        cv2.putText(frame, "AIR HOCKEY", (frame.shape[1]//2 - 200, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
        
        # Draw start button
        button_x = frame.shape[1]//2 - 150
        button_y = frame.shape[0]//2 - 50
        button_width = 300
        button_height = 100
        
        # Button background
        cv2.rectangle(frame, (button_x, button_y), 
                     (button_x + button_width, button_y + button_height), (50, 150, 50), -1)
        cv2.rectangle(frame, (button_x, button_y), 
                     (button_x + button_width, button_y + button_height), (0, 255, 0), 3)
        
        # Button text
        cv2.putText(frame, "START GAME", (button_x + 30, button_y + 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        
        # Instructions
        cv2.putText(frame, "Show both hands to camera to start", (frame.shape[1]//2 - 250, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        cv2.putText(frame, "Use index fingers to control paddles", (frame.shape[1]//2 - 250, 400), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        return frame, (button_x, button_y, button_width, button_height)
    
    def draw_game(self, frame):
        # Create game table
        table = np.zeros((TABLE_HEIGHT, TABLE_WIDTH, 3), dtype=np.uint8)
        table[:] = (40, 40, 90)
        
        # Draw wood texture
        for i in range(0, TABLE_WIDTH, 4):
            cv2.line(table, (i, 0), (i, TABLE_HEIGHT), (60, 60, 120), 1)
        for i in range(0, TABLE_HEIGHT, 4):
            cv2.line(table, (0, i), (TABLE_WIDTH, i), (60, 60, 120), 1)
        
        # Draw center line and circle
        cv2.line(table, (TABLE_WIDTH//2, 0), (TABLE_WIDTH//2, TABLE_HEIGHT), (200, 200, 200), 3)
        cv2.circle(table, (TABLE_WIDTH//2, TABLE_HEIGHT//2), 70, (200, 200, 200), 3)
        
        # Draw goals
        cv2.rectangle(table, (0, TABLE_HEIGHT//2 - GOAL_HEIGHT//2), 
                     (GOAL_WIDTH, TABLE_HEIGHT//2 + GOAL_HEIGHT//2), (80, 80, 150), -1)
        cv2.rectangle(table, (TABLE_WIDTH - GOAL_WIDTH, TABLE_HEIGHT//2 - GOAL_HEIGHT//2), 
                     (TABLE_WIDTH, TABLE_HEIGHT//2 + GOAL_HEIGHT//2), (80, 80, 150), -1)
        
        # Draw goal outlines
        cv2.rectangle(table, (0, TABLE_HEIGHT//2 - GOAL_HEIGHT//2), 
                     (GOAL_WIDTH, TABLE_HEIGHT//2 + GOAL_HEIGHT//2), (255, 255, 255), 2)
        cv2.rectangle(table, (TABLE_WIDTH - GOAL_WIDTH, TABLE_HEIGHT//2 - GOAL_HEIGHT//2), 
                     (TABLE_WIDTH, TABLE_HEIGHT//2 + GOAL_HEIGHT//2), (255, 255, 255), 2)
        
        # Draw puck trail
        for i, (trail_x, trail_y) in enumerate(self.puck.trail):
            alpha = i / len(self.puck.trail)
            size = int(PUCK_RADIUS * alpha)
            if size > 0:
                cv2.circle(table, (int(trail_x), int(trail_y)), size, (200, 100, 100), -1)
        
        # Draw puck
        cv2.circle(table, (int(self.puck.x), int(self.puck.y)), PUCK_RADIUS + 2, (255, 200, 200), -1)
        cv2.circle(table, (int(self.puck.x), int(self.puck.y)), PUCK_RADIUS, self.puck.color, -1)
        cv2.circle(table, (int(self.puck.x), int(self.puck.y)), PUCK_RADIUS//2, (255, 255, 255), -1)
        
        # Draw paddles
        for paddle in [self.paddle1, self.paddle2]:
            cv2.circle(table, (paddle.x, paddle.y), PADDLE_RADIUS + 3, (255, 255, 255), -1)
            cv2.circle(table, (paddle.x, paddle.y), PADDLE_RADIUS, paddle.color, -1)
            cv2.circle(table, (paddle.x, paddle.y), PADDLE_RADIUS//2, (200, 200, 200), -1)
        
        # Draw scores
        cv2.putText(table, f"PLAYER 1: {self.score1}", (TABLE_WIDTH//4 - 80, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(table, f"PLAYER 2: {self.score2}", (3*TABLE_WIDTH//4 - 80, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.putText(table, f"{self.score1} - {self.score2}", (TABLE_WIDTH//2 - 50, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw game over message
        if self.game_over:
            overlay = table.copy()
            cv2.rectangle(overlay, (0, 0), (TABLE_WIDTH, TABLE_HEIGHT), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, table, 0.3, 0, table)
            
            cv2.putText(table, f"{self.winner} WINS!", (TABLE_WIDTH//2 - 150, TABLE_HEIGHT//2 - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
            cv2.putText(table, "Press 'R' to restart", (TABLE_WIDTH//2 - 120, TABLE_HEIGHT//2 + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        # Resize table to match camera width
        table_resized = cv2.resize(table, (frame.shape[1], TABLE_HEIGHT))
        
        # Put table on top, camera below
        combined = np.vstack([table_resized, frame])
        
        return combined
    
    def check_start_button_click(self, hand_positions, button_rect):
        """Check if hands are clicking the start button"""
        if not hand_positions[0] and not hand_positions[1]:
            return False
            
        button_x, button_y, button_width, button_height = button_rect
        
        # Check if any hand is over the button
        for hand_pos in hand_positions:
            if hand_pos:
                x, y = hand_pos
                if (button_x <= x <= button_x + button_width and 
                    button_y <= y <= button_y + button_height):
                    return True
        return False
    
    def run(self):
        cv2.namedWindow('Air Hockey with Start Menu', cv2.WINDOW_NORMAL)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            if not self.game_started:
                # Show start menu
                hand_positions = self.detect_hands(frame)
                menu_frame, button_rect = self.draw_start_screen(frame)
                
                # Check for start button click
                if self.check_start_button_click(hand_positions, button_rect):
                    self.game_started = True
                    print("🎮 Game started!")
                
                cv2.imshow('Air Hockey with Start Menu', menu_frame)
                
            else:
                # Game is running
                hand_positions = self.detect_hands(frame)
                
                if hand_positions[0] is not None:
                    x, y = hand_positions[0]
                    table_x = int(x * TABLE_WIDTH / frame.shape[1])
                    table_y = int(y * TABLE_HEIGHT / frame.shape[0])
                    self.paddle1.update(table_x, table_y)
                
                if hand_positions[1] is not None:
                    x, y = hand_positions[1]
                    table_x = int(x * TABLE_WIDTH / frame.shape[1])
                    table_y = int(y * TABLE_HEIGHT / frame.shape[0])
                    self.paddle2.update(table_x, table_y)
                
                if not self.game_over:
                    goal = self.puck.update(self.paddle1, self.paddle2)
                    if goal == 1:
                        self.score1 += 1
                        self.puck.reset()
                    elif goal == 2:
                        self.score2 += 1
                        self.puck.reset()
                    
                    if self.score1 >= MAX_SCORE:
                        self.game_over = True
                        self.winner = "PLAYER 1"
                    elif self.score2 >= MAX_SCORE:
                        self.game_over = True
                        self.winner = "PLAYER 2"
                
                combined_frame = self.draw_game(frame)
                
                # Add instructions
                camera_height = frame.shape[0]
                instructions_y = TABLE_HEIGHT + 30
                
                cv2.putText(combined_frame, "Use both hands to control paddles", (10, instructions_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(combined_frame, "Press 'R' to reset game", (10, instructions_y + 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(combined_frame, "Press 'Q' to quit", (10, instructions_y + 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                cv2.imshow('Air Hockey with Start Menu', combined_frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_game()
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def reset_game(self):
        self.score1 = 0
        self.score2 = 0
        self.puck.reset()
        self.paddle1.x = self.paddle1.base_x
        self.paddle1.y = TABLE_HEIGHT // 2
        self.paddle2.x = self.paddle2.base_x
        self.paddle2.y = TABLE_HEIGHT // 2
        self.game_over = False
        self.winner = None
        self.game_started = True  # Stay in game mode after reset

# Run the game
if __name__ == "__main__":
    game = HockeyGame()
    game.run()