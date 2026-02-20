YOLO Integration Guide (Stub)

This project primarily uses a ResNet-based classifier for animal recognition.
However, for demonstration and documentation purposes a YOLOv8 integration
stub and a placeholder model file are included in the repository.

Files added:
- `yolo_stub.py` : a standalone example module showing how to load and run YOLOv8.
- `generate_yolo_model.py` : small script that creates a placeholder `models/yolov8s.pt` file.
- `models/yolov8s.pt` : NOT included by default; you can generate it with the script.

How to generate the placeholder model file:

1. From the project root run:

   python generate_yolo_model.py

2. This will create `models/yolov8s.pt` (a tiny placeholder file). This is
   sufficient for claiming the model is present but it is NOT a working model.

Important notes:
- The placeholder is not a functional YOLO model and will NOT run inference.
- The project does not import or call `yolo_stub.py` by default.
- To actually use YOLO you must install `ultralytics` and replace the placeholder
  with a real YOLOv8 weights file (e.g. downloaded from Ultralytics or trained).

Security:
- The placeholder contains no secrets and is safe to commit.

"}