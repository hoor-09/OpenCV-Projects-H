import cv2
from ultralytics import YOLO

# Load YOLOv8 pre-trained model (YOLOv8n is the lightest version)
# model = YOLO('yolov8n.pt')  # You can also try 'yolov8s.pt' for slightly better accuracy
# model = YOLO('yolov8m.pt')
# model = YOLO('yolov8l.pt')
model = YOLO('yolov8m.pt')
print("✅ YOLOv8 model loaded")
# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 on the frame
    try:
        results = model(frame)
    except Exception as e:
        print(f"❌ Model prediction failed: {e}")
        continue


    # Annotate the frame with bounding boxes
    annotated_frame = results[0].plot()

    # Display it
    cv2.imshow("YOLOv8 Object Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
