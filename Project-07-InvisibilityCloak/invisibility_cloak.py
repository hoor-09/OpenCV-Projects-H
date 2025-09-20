import cv2
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)

# Check camera
if not cap.isOpened():
    print("❌ Camera error!")
    exit()

print("✅ Camera working!")

# Variables
background = None
background_captured = False

# Blue range - adjust as needed
lower_blue = np.array([90, 80, 40])
upper_blue = np.array([140, 255, 200])

print("🎮 Press 'c' to capture background (make sure it's clear!)")
print("🎮 Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Clean up mask
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Apply invisibility effect if background captured
    output = frame.copy()
    if background_captured:
        # 🔥 CRITICAL FIX: Use simple bitwise operations instead of alpha blending
        mask_inv = cv2.bitwise_not(mask)
        
        # Extract background and foreground
        bg_part = cv2.bitwise_and(background, background, mask=mask)
        fg_part = cv2.bitwise_and(frame, frame, mask=mask_inv)
        
        # Combine for final output
        output = cv2.add(bg_part, fg_part)
        
        status = "INVISIBILITY ACTIVE - Working!"
        color = (0, 255, 0)
        
        # Show detection stats
        blue_pixels = np.sum(mask == 255)
        total_pixels = mask.size
        detection_percent = (blue_pixels / total_pixels) * 100
        cv2.putText(output, f"Detection: {detection_percent:.1f}%", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    else:
        status = "PRESS 'c' TO CAPTURE BACKGROUND"
        color = (0, 0, 255)
    
    # Display info
    cv2.putText(output, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    if background_captured:
        cv2.putText(output, "Wave blue cloth to disappear!", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imshow('Realistic Invisibility Cloak', output)
    cv2.imshow('Mask Debug', mask)
    
    # Controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):  # Capture background
        background = frame.copy()
        # Minimal blur for realism
        background = cv2.GaussianBlur(background, (3, 3), 0)
        background_captured = True
        print("✅ Background captured!")

cap.release()
cv2.destroyAllWindows()