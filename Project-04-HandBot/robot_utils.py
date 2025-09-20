import cv2
import numpy as np
import math

class Robot:
    def __init__(self):
        self.state = "neutral"
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.robot_color = (50, 50, 200)  # Blue-ish color
        self.robot_thickness = 3
        
        # Animation parameters
        self.wave_amplitude = 30
        self.dance_speed = 2
        self.rock_intensity = 20
    
    def update(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.animation_frame = 0
    
    def draw(self, canvas):
        self.animation_frame += self.animation_speed
        height, width = canvas.shape[:2]
        center_x = width // 2
        center_y = height // 2
        
        # Draw based on state
        draw_method = getattr(self, f"_draw_{self.state}", self._draw_neutral)
        draw_method(canvas, center_x, center_y)
    
    def _draw_neutral(self, canvas, x, y):
        self._draw_head(canvas, x, y-80, "neutral")
        self._draw_body(canvas, x, y)
        self._draw_limbs(canvas, x, y, arm_angle=0, leg_angle=0)
    
    def _draw_happy(self, canvas, x, y):
        self._draw_head(canvas, x, y-80, "happy")
        self._draw_body(canvas, x, y)
        self._draw_limbs(canvas, x, y, arm_angle=0.3, leg_angle=0.2)
    
    def _draw_angry(self, canvas, x, y):
        self._draw_head(canvas, x, y-80, "angry")
        self._draw_body(canvas, x, y)
        arm_angle = math.sin(self.animation_frame) * 0.5
        self._draw_limbs(canvas, x, y, arm_angle=arm_angle, leg_angle=0.5)
    
    def _draw_dance(self, canvas, x, y):
        self._draw_head(canvas, x, y-80, "happy")
        body_offset = int(15 * math.sin(self.animation_frame * self.dance_speed))
        self._draw_body(canvas, x + body_offset, y)
        
        # Animated limbs
        left_arm = math.sin(self.animation_frame * self.dance_speed) * 0.8 + 0.5
        right_arm = math.sin(self.animation_frame * self.dance_speed + math.pi) * 0.8 + 0.5
        left_leg = math.sin(self.animation_frame * self.dance_speed + math.pi/2) * 0.5
        right_leg = math.sin(self.animation_frame * self.dance_speed - math.pi/2) * 0.5
        
        self._draw_limbs(canvas, x + body_offset, y, 
                        left_arm_angle=left_arm, right_arm_angle=right_arm,
                        left_leg_angle=left_leg, right_leg_angle=right_leg)
    
    def _draw_rock(self, canvas, x, y):
        self._draw_head(canvas, x, y-80, "rock")  # Changed to rock expression
        self._draw_body(canvas, x, y)
        rock_offset = int(math.sin(self.animation_frame) * self.rock_intensity)
        self._draw_limbs(canvas, x, y, arm_angle=0.5, leg_angle=0.3, rock_offset=rock_offset)
    
    def _draw_point(self, canvas, x, y):
        self._draw_head(canvas, x, y-80, "neutral")
        self._draw_body(canvas, x, y)
        self._draw_limbs(canvas, x, y, left_arm_angle=0.8, right_arm_angle=0)
    
    def _draw_wave(self, canvas, x, y):
        self._draw_head(canvas, x, y-80, "happy")
        self._draw_body(canvas, x, y)
        wave_angle = math.sin(self.animation_frame * 2) * 0.5 + 0.5
        self._draw_limbs(canvas, x, y, left_arm_angle=wave_angle, right_arm_angle=0)
    
    def _draw_head(self, canvas, x, y, expression):
        # Head circle
        cv2.circle(canvas, (x, y), 40, self.robot_color, self.robot_thickness)
        
        # Eyes - different styles for each expression
        if expression == "angry":
            # Angry eyes (slanted down)
            cv2.line(canvas, (x-20, y-5), (x-10, y-15), self.robot_color, 2)
            cv2.line(canvas, (x+10, y-15), (x+20, y-5), self.robot_color, 2)
        elif expression == "rock":
            # Rock eyes (cool X-shaped)
            cv2.line(canvas, (x-18, y-18), (x-8, y-8), self.robot_color, 2)
            cv2.line(canvas, (x-8, y-18), (x-18, y-8), self.robot_color, 2)
            cv2.line(canvas, (x+8, y-8), (x+18, y-18), self.robot_color, 2)
            cv2.line(canvas, (x+8, y-18), (x+18, y-8), self.robot_color, 2)
        elif expression == "happy":
            # Happy eyes (normal circles, slightly squinted)
            cv2.ellipse(canvas, (x-15, y-10), (8, 5), 0, 0, 180, self.robot_color, -1)
            cv2.ellipse(canvas, (x+15, y-10), (8, 5), 0, 0, 180, self.robot_color, -1)
        else:
            # Neutral eyes (simple circles)
            cv2.circle(canvas, (x-15, y-10), 5, self.robot_color, -1)
            cv2.circle(canvas, (x+15, y-10), 5, self.robot_color, -1)
        
        # Mouth - different styles for each expression
        if expression == "happy":
            # Big smile
            cv2.ellipse(canvas, (x, y+15), (20, 10), 0, 0, 180, self.robot_color, 2)
        elif expression == "angry":
            # Frown
            cv2.ellipse(canvas, (x, y+5), (20, 10), 0, 180, 360, self.robot_color, 2)
        elif expression == "rock":
            # Cool rock mouth (slightly open with tongue)
            cv2.ellipse(canvas, (x, y+10), (15, 8), 0, 180, 360, self.robot_color, 2)
            cv2.line(canvas, (x-5, y+10), (x+5, y+10), self.robot_color, 2)
        else:
            # Neutral mouth (straight line)
            cv2.line(canvas, (x-20, y+10), (x+20, y+10), self.robot_color, 2)
    
    def _draw_body(self, canvas, x, y):
        cv2.line(canvas, (x, y-40), (x, y+20), self.robot_color, self.robot_thickness)
    
    def _draw_limbs(self, canvas, x, y, 
                   left_arm_angle=0, right_arm_angle=0,
                   left_leg_angle=0, right_leg_angle=0,
                   arm_angle=None, leg_angle=None,
                   rock_offset=0):
        # Use single angle if provided for both sides
        if arm_angle is not None:
            left_arm_angle = right_arm_angle = arm_angle
        if leg_angle is not None:
            left_leg_angle = right_leg_angle = leg_angle
        
        # Calculate arm positions
        left_arm_x = int(x - 40 * math.cos(left_arm_angle))
        left_arm_y = int(y - 20 - 40 * math.sin(left_arm_angle))
        right_arm_x = int(x + 40 * math.cos(right_arm_angle))
        right_arm_y = int(y - 20 - 40 * math.sin(right_arm_angle))
        
        # Draw arms
        cv2.line(canvas, (x, y-20), (left_arm_x, left_arm_y), self.robot_color, self.robot_thickness)
        cv2.line(canvas, (x, y-20), (right_arm_x, right_arm_y), self.robot_color, self.robot_thickness)
        
        # Special rock gesture arms (horns)
        if abs(rock_offset) > 0:
            try:
                # Left horn
                cv2.line(canvas, 
                        (left_arm_x, left_arm_y), 
                        (left_arm_x-10, left_arm_y+20+rock_offset), 
                        self.robot_color, self.robot_thickness)
                # Right horn
                cv2.line(canvas, 
                        (right_arm_x, right_arm_y), 
                        (right_arm_x+10, right_arm_y+20-rock_offset), 
                        self.robot_color, self.robot_thickness)
            except Exception as e:
                print(f"Error drawing rock gesture: {e}")
        
        # Calculate leg positions
        left_leg_x = int(x - 30 - 20 * math.sin(left_leg_angle))
        left_leg_y = int(y + 60 + 10 * math.cos(left_leg_angle))
        right_leg_x = int(x + 30 + 20 * math.sin(right_leg_angle))
        right_leg_y = int(y + 60 + 10 * math.cos(right_leg_angle))
        
        # Draw legs
        cv2.line(canvas, (x, y+20), (left_leg_x, left_leg_y), self.robot_color, self.robot_thickness)
        cv2.line(canvas, (x, y+20), (right_leg_x, right_leg_y), self.robot_color, self.robot_thickness)