from ultralytics import YOLO
import cv2 as cv
import os


class ImageDetection:
    def __init__(self, image_path, model_path="yolo11n.pt"):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image path '{image_path}' does not exist.")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path '{model_path}' does not exist.")

        self.image_path = image_path
        self.model = YOLO(model_path)

    def image_detection(self):
        # Load the image
        image = cv.imread(self.image_path)
        if image is None:
            raise ValueError(f"Failed to load image from path: {self.image_path}")

        # Perform detection
        results = self.model(image)

        # Parse detections
        detections = []
        class_names = self.model.names  # Get class names from the model
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

        return detections
    
    def draw_bonding_box(self):

        image = cv.imread(self.image_path)
        
        draw_image = cv.rectangle(image,(287,684),(495,803),255,2)
        result_image = cv.putText(draw_image,"boat",(287,684-10),cv.FONT_HERSHEY_COMPLEX,1,255,2)
        cv.imshow("result",result_image)
        cv.waitKey(0)



# Example Usage
if __name__ == "__main__":

    try:
        detector = ImageDetection(r"Images\\bg.png", "yolo11n.pt")
        detections = detector.image_detection()
        print('this is coord',detections)
        detector.draw_bonding_box()
        frist_coordinate = detections[0]["coordinates"]
        print("This is frist coordinate",frist_coordinate)

        
        # Print all detections
        for detection in detections:
            print(f"Label: {detection['label']}, Coordinates: {detection['coordinates']}, Confidence: {detection['confidence']}")

    except Exception as e:
        print(f"Error: {e}")
