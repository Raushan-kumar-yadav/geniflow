from ultralytics import YOLO
import cv2
import torch

# Load the YOLO model
def load_model(model_path):
    try:
        model = YOLO(model_path)  # Replace with the path to your YOLO model file
        # Check for GPU availability
        if torch.cuda.is_available():
            model.to('cuda')  # Use GPU if available
        else:
            model.to('cpu')  # Fallback to CPU
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Perform object detection
def detect_objects(model, image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not read the image.")
        return []

    try:
        # Perform detection
        results = model(image)

        # Extract detection results
        detections = []
        class_names = model.names  # Get class names from the model
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box coordinates
            confidence = box.conf[0].item()  # Confidence score
            class_id = int(box.cls[0].item())  # Class ID
            label = class_names[class_id]  # Class label
            detections.append({
                "label": label,
                "coordinates": (x1, y1, x2, y2),
                "confidence": confidence
            })

        # Annotate image with bounding boxes and labels
        for detection in detections:
            x1, y1, x2, y2 = detection["coordinates"]
            label = detection["label"]
            confidence = detection["confidence"]

            # Draw the bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Put the label and confidence
            cv2.putText(image, f"{label} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Show the image with annotations
        cv2.imshow("Detections", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return detections
    except Exception as e:
        print(f"Error during detection: {e}")
        return []

# Main function
def main():
    # Replace with the correct model path and image path
    model_path = 'yolo11n.pt'  # Path to your YOLO model file
    image_path = r"Images\\12.png"  # Replace with the path to your image file

    # Load the YOLO model
    model = load_model(model_path)
    if model is None:
        return

    # Detect objects in the image
    detections = detect_objects(model, image_path)
    if detections:
        for det in detections:
            print(f"Label: {det['label']}, Coordinates: {det['coordinates']}, Confidence: {det['confidence']:.2f}")
    else:
        print("No detections found.")

if __name__ == "__main__":
    main()
