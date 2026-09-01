from ultralytics import YOLO
from config  import MODEL_PATH, DETECTION_THRESHOLD
import cv2


class DetectionService:
    def __init__(self, model_path: str =MODEL_PATH):
        self.model = YOLO(model_path)
        self.class_names = {0: "no_helmet", 1: "helmet"}

    def detect(self, frame):
        results = self.model(frame)[0]

        detections_classes = []
        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result

            if score >= DETECTION_THRESHOLD:
                class_name = self.class_names[int(class_id)]    
                detections_classes.append(class_name)

                #Draw bounding box and label on the frame
                cv2.rectangle(frame, (int(x1), int(y1), int(x2),int(y2)), (0, 255, 0), 2) 
                cv2.putText(frame, f"{class_name} {score:.2f}", (int(x1), int(y1) -10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 2)

        return frame, detections_classes
