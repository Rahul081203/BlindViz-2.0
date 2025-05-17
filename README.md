<p align="center">
    <img src="https://img.shields.io/badge/BlindViz%20Plus-Empowering%20Sight,%20Enhancing%20Life-blueviolet?style=for-the-badge&logo=visual-studio-code" alt="BlindViz Plus Banner"/>
</p>

<h1 align="center">🌟 BlindViz Plus</h1>
<h3 align="center"><em>Empowering Sight, Enhancing Life</em></h3>

<p align="center">
    <b>Authors:</b><br>
    Rahul Sharma &nbsp;|&nbsp; Gunjan Jarawat &nbsp;|&nbsp; Devansh Agarwal &nbsp;|&nbsp; Austin Dious
</p>

---


## 📖 Abstract

BlindViz Plus / 2.0 is an innovative assistive technology crafted to empower visually impaired individuals with greater independence and confidence. The system delivers real-time object detection, depth estimation, and natural language scene descriptions, all seamlessly converted into audio feedback for intuitive environmental awareness.

By harnessing the power of **Edge AI**, advanced models like **YOLOv8** for object detection, **DepthAnythingv2** for depth estimation, and **Large Language Models (LLMs)** for contextual understanding, BlindViz Plus achieves low latency and high energy efficiency—making it perfectly suited for wearable devices. This integration bridges the gap between users and their surroundings, enabling safe, informed navigation and fostering autonomy in daily life.

---

## 🏗️ Project Architecture

The system integrates multiple technologies into a seamless pipeline:

1. **Voice Command**: Speech-to-text (STT) using Flutter for hands-free interaction.
2. **Image Capture**: ESP32-CAM captures real-time images.
3. **Backend Processing**:
   - **Object Detection**: YOLOv8 for real-time object identification.
   - **Depth Estimation**: DepthAnythingv2 for spatial awareness.
   - **OCR**: EasyOCR for text recognition.
   - **Pose Estimation**: Mediapipe Pose for posture analysis.
4. **Natural Language Processing**: GPT-3.5-Turbo for generating human-like scene descriptions.
5. **Audio Feedback**: Text-to-speech (TTS) for delivering contextual information to users.

---

## ✨ Features

- **🔍 Real-Time Object Detection**: Identifies objects using YOLOv8 with high accuracy.
- **📏 Depth Estimation**: Provides spatial awareness using DepthAnythingv2.
- **📝 Optical Character Recognition (OCR)**: Reads text from the environment using EasyOCR.
- **🧍 Pose Estimation**: Detects human posture using Mediapipe Pose.
- **🗣️ Natural Language Descriptions**: Generates detailed scene descriptions with GPT-3.5-Turbo.
- **🎧 Audio Feedback**: Converts descriptions into speech for user-friendly interaction.

---

## 📂 Project Structure

```
BlindViz-2.0/
├── arduino_server.ino         # Arduino server code
├── camera_index.h             # Camera index configuration
├── camera_pins.h              # Camera pin configuration
├── pose_estimation.py         # Python script for pose estimation
├── server.py                  # Python server script
├── vision_api.py              # Vision API integration script
├── flutter_app/               # Flutter application
│   └── test_esp_server/       # Flutter project for ESP server
├── llm/                       # Large Language Model integration
│   ├── app.py                 # LLM application script
│   ├── client.py              # LLM client script
│   └── requirements.txt       # Python dependencies
```

> **Note:**  
> - Files and directories such as `copy/`, `__pycache__/`, model weights (`*.pt`), config files (`*.json`, `*.csv`), environment files (`llm/.env`), sample images (`*.jpg`), and `uploaded_imgs/` are excluded as per `.gitignore`.

---

## 🛠️ Installation

### 🚩 Arduino Setup
1. Open `arduino_server.ino` in the Arduino IDE.
2. Configure `camera_index.h` and `camera_pins.h` according to your ESP32-CAM hardware.
3. Connect your ESP32-CAM and upload the code.

### 📱 Flutter App
1. Navigate to the Flutter project directory:
    ```bash
    cd flutter_app/test_esp_server
    flutter pub get
    ```
2. Launch the app on your device or emulator:
    ```bash
    flutter run
    ```

### 🐍 Python Backend
1. Install required dependencies (if not already installed):
    ```bash
    pip install -r llm/requirements.txt
    pip install easyocr
    pip install torch torchvision
    pip install opencv-python
    ```
2. Start the backend services (in separate terminals or as background processes):
    ```bash
    python llm/app.py
    python pose_estimation.py
    python server.py
    python vision_api.py
    ```

---



## 📊 Experimental Results

### 🟦 YOLOv8 Object Detection
- **Precision:** 95.5%
- **Recall:** 94.3%
- **mAP@50:** 97.6%
- **mAP@50-95:** 91.9%

### 🟩 DepthAnythingv2 Depth Estimation
- **Absolute Relative Error:** 0.121
- **RMSE:** 0.480
- **δ < 1.25:** 89.2%

### 🟨 OCR (EasyOCR)
- **Word Recognition Accuracy:** 89.4%
- **Character Recognition Accuracy:** 94.8%
- **Sentence Reconstruction Accuracy:** 82.3%
---

## 🌍 Impact

BlindViz Plus directly addresses the challenges faced by visually impaired individuals by offering:

- **Enhanced Accessibility**: Delivers real-time, context-aware descriptions of surroundings.
- **Affordability**: Utilizes low-cost hardware and open-source software.
- **Energy Efficiency**: Optimized for wearable devices with extended battery life.

---

## 🚀 Future Enhancements

- **Improved Models**: Train YOLOv8 and DepthAnythingv2 on assistive-specific datasets for higher accuracy.
- **Multi-Modal Feedback**: Integrate haptic feedback for usability in noisy environments.
- **Wearable Integration**: Develop smart glasses with embedded AI processing.
- **Global Usability**: Expand language support for NLP and TTS to reach a wider audience.

---

## 🤝 Contributing

Contributions are welcome!  
To contribute, please fork the repository and submit a pull request with your proposed changes.

---

## 🙏 Acknowledgments

- **YOLOv8**: [Ultralytics](https://github.com/ultralytics/ultralytics)
- **DepthAnythingv2**: [DepthAnything](https://github.com/isl-org/Depth-Anything)
- **EasyOCR**: [Jaided AI](https://github.com/JaidedAI/EasyOCR)
- **OpenAI GPT-3.5-Turbo**: [OpenAI](https://platform.openai.com/)

---

## 📚 References

1. World Health Organization, *World Report on Vision*, 2019.
2. G. Jocher et al., *YOLOv8: Ultralytics Open Source Object Detection*, GitHub, 2023.
3. R. Ranftl et al., *Towards Robust Monocular Depth Estimation*, IEEE, 2020.
4. OpenAI, *GPT-4 Technical Report*, OpenAI, 2023.
5. Jaided AI, *EasyOCR: Ready-to-use OCR with Deep Learning*, 2020.

