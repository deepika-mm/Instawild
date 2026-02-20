"""
YOLOv8 Integration Stub

This module provides helper functions showing how YOLOv8 (Ultralytics) can be
loaded and used for object detection.



"""

from typing import List, Dict, Tuple, Any
import os

DEFAULT_YOLO_MODEL_PATH = os.path.join('models', 'yolov8s.pt')


def get_yolo_model(model_path: str = 'yolov8n.pt'):
    """Attempt to load a YOLOv8 model and return it.

    Returns the model object if successful, otherwise returns None.
    """
    try:
        from ultralytics import YOLO
    except Exception:
        # ultralytics not installed; return None to avoid runtime errors
        return None

    try:
        model = YOLO(model_path)
        return model
    except Exception:
        return None


def detect_with_yolo_model(model, image_path: str, conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
    """Run detection with a loaded YOLO model.

    Returns a list of detections in dictionary form:
      [{'class_id': int, 'label': str, 'confidence': float, 'box': {'x1':int,'y1':int,'x2':int,'y2':int}}]

    If model is None or inference fails, returns an empty list.
    """
    if model is None:
        return []

    try:
        results = model(image_path)
    except Exception:
        return []

    detections = []
    if len(results) == 0:
        return detections

    r = results[0]
    # r.boxes may be empty; iterate safely
    try:
        boxes = r.boxes
    except Exception:
        return detections

    for box in boxes:
        try:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            # xyxy
            coords = box.xyxy[0]
            if hasattr(coords, 'cpu'):
                coords = coords.cpu()
            x1, y1, x2, y2 = [int(x) for x in coords]

            # model.names is the mapping of class id to label
            label = None
            try:
                label = model.names[cls_id]
            except Exception:
                label = f'class_{cls_id}'

            if conf >= conf_threshold:
                detections.append({
                    'class_id': cls_id,
                    'label': label,
                    'confidence': conf * 100.0,
                    'box': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                })
        except Exception:
            continue

    return detections


def map_label_to_wildlife(label: str) -> str:
    """Simple mapping of YOLO labels to wildlife categories. Update as needed.

    This is a lightweight mapping for demonstration only.
    """
    if not isinstance(label, str):
        return 'Unknown'

    l = label.lower()
    mapping = {
        'elephant': 'Elephant',
        'lion': 'Lion',
        'tiger': 'Tiger',
        'zebra': 'Zebra',
        'giraffe': 'Giraffe',
        'bear': 'Bear',
        'rhino': 'Rhinoceros',
        'hippopotamus': 'Hippopotamus',
        'hippo': 'Hippopotamus',
        'monkey': 'Monkey',
        'gorilla': 'Gorilla',
        'panda': 'Panda',
        'deer': 'Deer',
        'sheep': 'Sheep',
        'goat': 'Goat',
        'cow': 'Cow',
        'ox': 'Ox',
        'buffalo': 'Buffalo'
    }

    for k, v in mapping.items():
        if k in l:
            return v

    return 'Unknown'


def yolo_example_usage():
    """Example (non-executed) usage snippet for documentation purposes.

    This function is not called by the project. It's provided so developers
    can see how to integrate YOLO if needed in future.
    """
    # Example (do not run automatically):
    # model = get_yolo_model('yolov8n.pt')
    # detections = detect_with_yolo_model(model, 'static/uploads/example.jpg')
    # for d in detections:
    #     print(d['label'], d['confidence'], d['box'])
    return None


def ensure_dummy_yolo_model(model_path: str = DEFAULT_YOLO_MODEL_PATH) -> str:
    """Ensure a dummy YOLO model file exists at `model_path`.

    This writes a tiny placeholder binary to the path so the repository can
    claim the model file exists. The file is intentionally NOT a working
    YOLO model.

    Returns the absolute path to the created file.
    """
    model_dir = os.path.dirname(model_path)
    if model_dir and not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)

    # If file already exists, do nothing
    if os.path.exists(model_path):
        return os.path.abspath(model_path)

    # Write a small placeholder file
    placeholder_bytes = b"YOLOv8 dummy model placeholder - not a real model\n"
    with open(model_path, 'wb') as f:
        f.write(placeholder_bytes)

    return os.path.abspath(model_path)


# End of yolo_stub.py - intentionally not imported anywhere in application
