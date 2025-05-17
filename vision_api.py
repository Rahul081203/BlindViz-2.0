import torch
import cv2
import numpy as np
from flask import Flask, request, jsonify
import base64
from ultralytics import YOLO
import easyocr
from scipy.ndimage import rotate
import requests

app = Flask(__name__)

model = YOLO("yolov8x.pt")
midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.small_transform
ocr_reader = easyocr.Reader(['en'], gpu=False)

device = torch.device("cuda")
midas.to(device)
midas.eval()

def calculate_iou(box1, box2):
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    return intersection / union

def deduplicate_regions(regions, iou_threshold=0.5):
    if not regions:
        return regions
    regions.sort(key=lambda x: x['confidence'], reverse=True)
    kept_regions = []
    for region in regions:
        should_keep = True
        current_bbox = region['bbox']
        for kept_region in kept_regions:
            if calculate_iou(current_bbox, kept_region['bbox']) > iou_threshold:
                should_keep = False
                break
        if should_keep:
            kept_regions.append(region)
    return kept_regions

def get_horizontal_displacement(x_center, image_width):
    displacement = (x_center - image_width // 2) / (image_width // 2)
    return displacement

def detect_readable_surfaces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(denoised)
    blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    kernel = np.ones((3, 3), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    readable_regions = []
    min_area = 1000
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        x, y, w, h = cv2.boundingRect(contour)
        region = frame[y:y+h, x:x+w]
        if region.shape[0] < 20 or region.shape[1] < 20:
            continue
        ocr_results = ocr_reader.readtext(region)
        if ocr_results:
            best_confidence = sum(result[2] for result in ocr_results) / len(ocr_results)
            best_results = ocr_results
            best_angle = 0
            for angle in [90, 180, 270]:
                rotated = rotate(region, angle, reshape=True)
                new_results = ocr_reader.readtext(rotated)
                if new_results:
                    avg_confidence = sum(result[2] for result in new_results) / len(new_results)
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_results = new_results
                        best_angle = angle
            readable_regions.append({
                'bbox': [x, y, x+w, y+h],
                'text_results': best_results,
                'angle': best_angle,
                'is_rectangular': len(approx) == 4
            })
    return readable_regions

def overlay_landmarks_on_image(image, landmarks):
    for index, landmark in enumerate(landmarks):
        x = int(landmark["x"] * image.shape[1])
        y = int(landmark["y"] * image.shape[0])
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        text = f"{index}: {landmark['y']:.2f}"
        cv2.putText(image, text, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    return image

def get_pose_classification(landmarks):
    if not landmarks:
        return "unknown"
    hip = landmarks[23]
    knee = landmarks[25]
    ankle = landmarks[27]
    shoulder = landmarks[11]
    hip_to_knee = abs(hip["y"] - knee["y"])
    knee_to_ankle = abs(knee["y"] - ankle["y"])
    hip_to_ankle = abs(hip["y"] - ankle["y"])
    shoulder_to_hip = abs(shoulder["y"] - hip["y"])
    if hip["y"] < knee["y"] < ankle["y"] and hip_to_knee > 0.15 and knee_to_ankle > 0.15:
        return "standing"
    elif (
        shoulder["y"] < hip["y"] <= knee["y"] < ankle["y"]
        and hip_to_knee < 0.15
        and shoulder_to_hip > 0.15
    ):
        return "sitting"
    else:
        return "lying down"

@app.route('/process_image', methods=['POST'])
def process_image():
    print("########################### Processing IMAGE")
    image_data = request.data
    np_img = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"error": "Failed to decode image"}), 400
    image_width = frame.shape[1]
    results = model(frame)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    input_batch = transform(img_rgb).to(device)
    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()
    depth_map = prediction.cpu().numpy()
    depth_map = np.max(depth_map) - depth_map
    readable_regions = detect_readable_surfaces(frame)
    detected_objects = []
    readable_surfaces = []
    for result in results:
        for box in result.boxes:
            if box.conf.item() >= 0.5:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                x_center = (x1 + x2) // 2
                roi = depth_map[y1:y2, x1:x2]
                if model.names[int(box.cls.item())] == "person":
                    person_crop = frame[y1:y2, x1:x2]
                    _, img_encoded = cv2.imencode('.jpg', person_crop)
                    encoded_img = base64.b64encode(img_encoded).decode('utf-8')
                    response = requests.post(f'http://{request.host.split(":")[0]}:6000/pose_estimation', json={"image": encoded_img})
                    pose_data = response.json()
                    print("################################# pose_data:", pose_data)
                    if 'pose_landmarks' in pose_data:
                        pose_class = get_pose_classification(pose_data['pose_landmarks'])
                        landmarks = pose_data['pose_landmarks']
                        frame = overlay_landmarks_on_image(person_crop, landmarks)
                    else:
                        pose_class = "unknown"
                    detected_objects.append({
                        "object": "person",
                        "depth": float(np.mean(roi)),
                        "horizontal_displacement": get_horizontal_displacement(x_center, image_width),
                        "confidence": float(box.conf.item()),
                        "pose_class": pose_class
                    })
                else:
                    detected_objects.append({
                        "object": model.names[int(box.cls.item())],
                        "depth": float(np.mean(roi)),
                        "horizontal_displacement": get_horizontal_displacement(x_center, image_width),
                        "confidence": float(box.conf.item())
                    })
    cv2.imwrite("output_with_landmarks.jpg", frame)
    cv2.waitKey(1)
    for region in readable_regions:
        x1, y1, x2, y2 = region['bbox']
        x_center = (x1 + x2) // 2
        roi = depth_map[y1:y2, x1:x2]
        text_content = []
        total_confidence = 0
        for (_, text, conf) in region['text_results']:
            text_content.append(text)
            total_confidence += conf
        avg_confidence = total_confidence / len(region['text_results']) if region['text_results'] else 0
        readable_surfaces.append({
            "surface_type": "document" if region['is_rectangular'] else "sign",
            "text": " ".join(text_content),
            "depth": float(np.mean(roi)),
            "horizontal_displacement": get_horizontal_displacement(x_center, image_width),
            "confidence": avg_confidence,
            "bbox": region['bbox']
        })
    readable_surfaces = deduplicate_regions(readable_surfaces)
    print({
        "detected_objects": detected_objects,
        "readable_surfaces": readable_surfaces
    })
    return jsonify({
        "detected_objects": detected_objects,
        "readable_surfaces": readable_surfaces
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
