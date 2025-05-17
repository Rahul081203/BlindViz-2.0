import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
import base64

app = Flask(__name__)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

landmark_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
connection_spec = mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)

def process_pose_on_person(person_crop):
    rgb_person = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_person)
    return result.pose_landmarks if result.pose_landmarks else None

def extract_landmarks_from_pose(pose_landmarks):
    if pose_landmarks is None:
        return None
    landmarks = []
    for landmark in pose_landmarks.landmark:
        landmarks.append({
            'x': landmark.x,
            'y': landmark.y,
            'z': landmark.z,
            'visibility': landmark.visibility
        })
    return landmarks

@app.route('/pose_estimation', methods=['POST'])
def pose_estimation():
    data = request.json
    if 'image' not in data:
        return jsonify({"error": "No image data found."}), 400
    try:
        image_data = base64.b64decode(data['image'])
        np_img = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({"error": f"Failed to decode image. Error: {str(e)}"}), 400
    pose_landmarks = process_pose_on_person(img)
    if pose_landmarks:
        landmarks = extract_landmarks_from_pose(pose_landmarks)
        return jsonify({'pose_landmarks': landmarks})
    return jsonify({"error": "Pose estimation failed."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
