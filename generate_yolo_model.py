
from yolo_stub import ensure_dummy_yolo_model

if __name__ == '__main__':
    path = ensure_dummy_yolo_model()
    print(f"Dummy YOLO model created at: {path}")
