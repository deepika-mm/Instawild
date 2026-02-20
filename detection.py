
import cv2
import numpy as np
from PIL import Image
import os


MODEL_PATH = os.path.join('models', 'yolov8s.pt')

def detect_animal(image_path):
    
    
    USE_RESNET = True  # Recommended - Install: pip install torch torchvision
    USE_YOLO = False   # Advanced option
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {
                'animal': 'Unknown',
                'confidence': 0.0,
                'wound_detected': False,
                'behavior': 'Unknown'
            }
        
        if USE_RESNET:
            detected_animal, confidence, bbox = detect_with_resnet(image_path, img)
        elif USE_YOLO:
            detected_animal, confidence, bbox = detect_with_yolo(image_path, img)
        else:
            detected_animal, confidence = analyze_image_features(img)
            height, width = img.shape[:2]
            bbox = {
                'x': int(width * 0.2),
                'y': int(height * 0.2),
                'width': int(width * 0.6),
                'height': int(height * 0.6)
            }
        
        wound_detected = detect_wounds(img)
        behavior = analyze_behavior_pattern(img)
        
        result = {
            'animal': detected_animal,
            'confidence': round(confidence, 2),
            'wound_detected': wound_detected,
            'behavior': behavior,
            'bounding_box': bbox,
            'image_dimensions': {'width': img.shape[1], 'height': img.shape[0]}
        }
        
        return result
        
    except Exception as e:
        print(f"Error in detection: {e}")
        return {
            'animal': 'Error',
            'confidence': 0.0,
            'wound_detected': False,
            'behavior': 'Unknown'
        }

def detect_with_resnet(image_path, img):
    """
    Detects animals using pre-trained ResNet model from ImageNet.
    Recognizes 1000+ classes including many wildlife species.
    """
    try:
        import torch
        from torchvision import models, transforms
        from PIL import Image as PILImage
        
        # Load pre-trained ResNet model
        model = models.resnet50(pretrained=True)
        model.eval()
        
        # Image preprocessing
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        # Load and preprocess image - handle both RGB and grayscale
        try:
            input_image = PILImage.open(image_path)
            if input_image.mode != 'RGB':
                input_image = input_image.convert('RGB')
        except Exception as e:
            print(f"Image loading error: {e}. Falling back to feature analysis.")
            return analyze_image_features(img) + ({},)
            
        input_tensor = preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0)
        
        # Move to same device as model
        device = next(model.parameters()).device
        input_batch = input_batch.to(device)
        
        # Prediction
        with torch.no_grad():
            output = model(input_batch)
        
        # Get probabilities
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
        # Load ImageNet labels
        LABELS = get_imagenet_labels()
        
        # Get top prediction - ensure valid index
        top_prob, top_catid = torch.topk(probabilities, 1)
        idx = int(top_catid[0])
        confidence = float(top_prob[0]) * 100
        confidence = min(100.0, confidence)  # Cap at 100%
        
        # Safe label access
        if idx < len(LABELS):
            predicted_label = LABELS[idx]
        else:
            predicted_label = f'ImageNet Class {idx}'
        
        # Map to wildlife categories
        animal_name = map_to_wildlife(predicted_label)
        
        # Estimate bounding box (ResNet doesn't provide bbox, so we estimate)
        height, width = img.shape[:2]
        bbox = {
            'x': int(width * 0.15),
            'y': int(height * 0.15),
            'width': int(width * 0.7),
            'height': int(height * 0.7)
        }
        
        return animal_name, confidence, bbox
        
    except ImportError:
        print("PyTorch not installed. Install with: pip install torch torchvision")
        return analyze_image_features(img) + ({
            'x': 0, 'y': 0, 
            'width': img.shape[1], 
            'height': img.shape[0]
        },)
    except Exception as e:
        print(f"ResNet detection error: {e}")
        height, width = img.shape[:2]
        return 'Detection Error', 0.0, {
            'x': 0, 'y': 0, 'width': width, 'height': height
        }

def get_imagenet_labels():
    """
    Returns ImageNet class labels with focus on wildlife species.
    Maps key ImageNet indices to animal names.
    """
    # Map of key ImageNet indices to animal names
    wildlife_map = {
        287: 'Cheetah', 288: 'Leopard', 289: 'Snow Leopard', 290: 'Jaguar', 291: 'Lion', 292: 'Tiger',
        293: 'Cougar', 294: 'Brown Bear', 295: 'American Black Bear', 296: 'Polar Bear', 297: 'Sloth Bear',
        340: 'Zebra', 341: 'Hog', 342: 'Wild Boar', 343: 'Warthog', 344: 'Hippopotamus',
        345: 'Ox', 346: 'Water Buffalo', 347: 'Bison', 348: 'Ram', 349: 'Bighorn Sheep',
        350: 'Ibex', 351: 'Hartebeest', 352: 'Impala', 353: 'Gazelle',
        354: 'Arabian Camel', 355: 'Llama', 365: 'Orangutan', 366: 'Gorilla', 367: 'Chimpanzee',
        368: 'Gibbon', 369: 'Siamang', 370: 'Guenon', 371: 'Patas Monkey', 372: 'Baboon',
        373: 'Macaque', 374: 'Langur', 375: 'Colobus', 376: 'Proboscis Monkey',
        377: 'Marmoset', 378: 'Capuchin', 379: 'Howler Monkey', 380: 'Titi', 381: 'Spider Monkey',
        382: 'Squirrel Monkey', 383: 'Madagascar Cat', 384: 'Indri', 385: 'Indian Elephant',
        386: 'African Elephant', 387: 'Red Panda', 388: 'Giant Panda',
        356: 'Weasel', 357: 'Mink', 358: 'Polecat', 359: 'Black Footed Ferret',
        360: 'Otter', 361: 'Skunk', 362: 'Badger', 363: 'Armadillo', 364: 'Three Toed Sloth'
    }
    
    labels = ['Unknown'] * 1000
    for idx, name in wildlife_map.items():
        if idx < 1000:
            labels[idx] = name
    
    return labels

def map_to_wildlife(predicted_label):
    """
    Maps ImageNet predictions to wildlife categories.
    """
    label_lower = predicted_label.lower()
    
    # Direct matches
    wildlife_map = {
        'elephant': 'Elephant',
        'lion': 'Lion',
        'tiger': 'Tiger',
        'leopard': 'Leopard',
        'cheetah': 'Cheetah',
        'zebra': 'Zebra',
        'giraffe': 'Giraffe',
        'bear': 'Bear',
        'wolf': 'Wolf',
        'fox': 'Fox',
        'deer': 'Deer',
        'gazelle': 'Gazelle',
        'impala': 'Impala',
        'buffalo': 'Buffalo',
        'bison': 'Bison',
        'gorilla': 'Gorilla',
        'chimpanzee': 'Chimpanzee',
        'monkey': 'Monkey',
        'panda': 'Panda',
        'hippo': 'Hippopotamus',
        'rhino': 'Rhinoceros',
        'hyena': 'Hyena',
    }
    
    # Check for matches
    for key, value in wildlife_map.items():
        if key in label_lower:
            return value
    
    # If it contains 'cat' or 'dog' but not domestic
    if ('cat' in label_lower or 'feline' in label_lower) and 'house' not in label_lower:
        return 'Wild Cat'
    if 'canine' in label_lower or ('dog' in label_lower and 'wild' in label_lower):
        return 'Wild Dog'
    
    # Return as-is if it seems like an animal
    if any(word in label_lower for word in ['animal', 'mammal', 'bird', 'reptile']):
        return predicted_label.title()
    
    # Default to "Unknown Wildlife" if not recognized
    return f"Unknown ({predicted_label.title()})"


def detect_with_yolo(image_path, img):
    """
    YOLO detection with unknown animal handling.
    """
    try:
        from ultralytics import YOLO
        import numpy as np
        
        # Define known wildlife species
        KNOWN_WILDLIFE = {
            'elephant', 'lion', 'tiger', 'leopard', 'cheetah',
            'bear', 'wolf', 'deer', 'zebra', 'giraffe',
            'rhino', 'hippo', 'buffalo', 'antelope', 'gazelle',
            'hyena', 'fox', 'wild dog', 'monkey', 'gorilla',
            'crocodile', 'snake', 'bird',
        }
        
        # Load YOLO model (you can use custom trained model)
        model = YOLO('yolov8n.pt')  # Or your custom wildlife model
        
        results = model(image_path)
        
        if len(results) > 0 and len(results[0].boxes) > 0:
            # Get the first detection (highest confidence)
            box = results[0].boxes[0]
            class_id = int(box.cls[0])
            confidence = min(100.0, float(box.conf[0]) * 100)  # Cap at 100%
            
            # Get class name from model
            detected_class = model.names[class_id].lower()
            
            # Check if it's a known wildlife animal
            if any(wildlife in detected_class for wildlife in KNOWN_WILDLIFE):
                animal_name = detected_class.title()
            elif 'animal' in detected_class or 'mammal' in detected_class:
                # Generic animal detected but species unknown
                animal_name = 'Unknown Wildlife'
            else:
                # Object detected but not recognized as wildlife
                animal_name = f'Unidentified ({detected_class})'
            
            # Get bounding box coordinates - safely convert to numpy
            try:
                box_coords = box.xyxy[0]
                if hasattr(box_coords, 'cpu'):
                    box_coords = box_coords.cpu()
                box_array = np.array(box_coords).astype(int)
                x1, y1, x2, y2 = box_array
            except Exception as e:
                print(f"Error extracting YOLO bbox: {e}")
                height, width = img.shape[:2]
                x1, y1, x2, y2 = 0, 0, width, height
            
            bbox = {
                'x': int(x1),
                'y': int(y1),
                'width': int(x2 - x1),
                'height': int(y2 - y1)
            }
            
            return animal_name, confidence, bbox
        else:
            # No detection
            height, width = img.shape[:2]
            return 'No Animal Detected', 0.0, {
                'x': 0, 'y': 0, 'width': width, 'height': height
            }
            
    except ImportError:
        print("YOLO not installed. Using simulation mode.")
        return analyze_image_features(img) + ({
            'x': 0, 'y': 0, 
            'width': img.shape[1], 
            'height': img.shape[0]
        },)
    except Exception as e:
        print(f"YOLO detection error: {e}")
        height, width = img.shape[:2]
        return 'Detection Error', 0.0, {
            'x': 0, 'y': 0, 'width': width, 'height': height
        }

def analyze_image_features(img):
    """
    Analyzes image color patterns and features to identify likely animal.
    Uses HSV color analysis for basic detection as fallback.
    WARNING: This is a fallback method with limited accuracy. Confidence scores are intentionally low.
    """
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        avg_hue = np.mean(hsv[:, :, 0])
        avg_saturation = np.mean(hsv[:, :, 1])
        avg_value = np.mean(hsv[:, :, 2])
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        avg_gray = np.mean(gray)
        
        # Improved animal detection based on color patterns
        if avg_saturation > 150 and avg_hue > 0 and avg_hue < 10:
            animal = 'Tiger'
            confidence = 45.0
        elif avg_saturation > 100 and avg_hue > 25 and avg_hue < 35:
            animal = 'Lion'
            confidence = 42.0
        elif avg_gray > 180:
            animal = 'Polar Bear'
            confidence = 40.0
        elif avg_saturation < 50 and avg_gray > 120:
            animal = 'Elephant'
            confidence = 48.0
        elif avg_saturation > 120 and avg_hue > 100 and avg_hue < 140:
            animal = 'Gorilla'
            confidence = 38.0
        elif avg_hue > 140 and avg_hue < 170:
            animal = 'Hippopotamus'
            confidence = 35.0
        elif avg_gray < 70:
            animal = 'Black Bear'
            confidence = 39.0
        elif avg_saturation > 80 and avg_hue > 35 and avg_hue < 77:
            animal = 'Giraffe'
            confidence = 37.0
        else:
            animal = 'Unknown Wildlife'
            confidence = 25.0
        
        return animal, min(100.0, confidence)
    except Exception as e:
        print(f"Error analyzing image features: {e}")
        return 'Unknown', 10.0

def detect_wounds(img):
    """
    Detects potential wounds based on red color patches and irregular patterns.
    """
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 | mask2
        
        red_pixels = cv2.countNonZero(red_mask)
        total_pixels = img.shape[0] * img.shape[1]
        red_percentage = (red_pixels / total_pixels) * 100
        
        return red_percentage > 2.0
    except Exception as e:
        print(f"Error detecting wounds: {e}")
        return False

def analyze_behavior_pattern(img):
    """
    Analyzes image brightness and contrast to infer behavior.
    This is a heuristic method with limited accuracy.
    """
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        contrast = np.std(gray)
        
        if contrast > 60:
            behavior = 'Alert'
        elif avg_brightness < 80:
            behavior = 'Resting'
        elif avg_brightness > 150:
            behavior = 'Calm'
        elif contrast > 45:
            behavior = 'Hunting'
        else:
            behavior = 'Feeding'
        
        return behavior
    except Exception as e:
        print(f"Error analyzing behavior: {e}")
        return 'Unknown'
