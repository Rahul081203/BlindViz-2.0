from flask import Flask, request, jsonify
import os
import requests

IMAGE_PROCESSING_URL = "http://192.168.248.17:5000/process_image"
LANGCHAIN_QUERY_URL = "http://192.168.248.17:5500/describe/invoke"

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded_imgs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        image_data = request.data
        image_path = os.path.join(UPLOAD_FOLDER, "received_image.jpg")
        with open(image_path, "wb") as f:
            f.write(image_data)

        print("✅ Image received and saved.")

        response = requests.post(
            IMAGE_PROCESSING_URL,
            data=image_data,
            headers={"Content-Type": "application/octet-stream"}
        )
        response.raise_for_status()
        sceneDescription = response.json()
        print("✅ Image processed:", sceneDescription)

        langchain_response = requests.post(
            LANGCHAIN_QUERY_URL,
            json={"input": {
                "query": f"you are now an assistant for a blind person, describe the object name, texts, positioning and relative depth detection scene with confidence greater than 0.5. The objects, texts, their horizontal displacement from center in captured image and depth is given as follows: {sceneDescription}. converse like a human and don't tell the depth units rather describe the distance as far, near etc.. your response should be in this format eg. a object is depth and to the horizontal position. dont use words that tell the posture of a person like standing or sitting. dont forget to include the text found in the image if there is any."
                }
            }
        )
        langchain_response.raise_for_status()
        result = langchain_response.json()
        natural_response = result["output"]
        print("✅ Langchain response:", natural_response["content"])

        return jsonify({"response": natural_response["content"]}), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7600, debug=True)
