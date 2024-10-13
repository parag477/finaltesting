from flask import Flask, render_template, request, jsonify, Response
import json
import cv2
import base64
import numpy as np
import io
import os
from makeup_app import MakeupApplication  # Import your class
from flask_cors import CORS



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
makeup_app = MakeupApplication()

def process_image(image_data):
    try:
        # Decode the base64 image to a numpy array
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Apply the makeup effect
        processed_img = makeup_app.process_frame(img)

        # Convert the processed image back to base64
        _, buffer = cv2.imencode('.jpg', processed_img)
        img_str = base64.b64encode(buffer).decode('utf-8')
        return img_str
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
# def process():
#     data = request.json
#     image_data = data['image']
#     processed_image = process_image(image_data)
#     return jsonify({'processed_image': processed_image})

def process():
    try:
        data = request.get_json()  # Safely access the incoming JSON data
        image_data = data.get('image')

        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        processed_image = process_image(image_data)

        if processed_image:
            # Manually create the JSON response with the processed image
            response_data = {'processed_image': processed_image}
            return Response(
                response=json.dumps(response_data),
                status=200,
                mimetype='application/json'
            )
        else:
            return jsonify({'error': 'Image processing failed'}), 500

    except Exception as e:
        print(f"Error processing image: {e}")
        error_response = {'error': 'Failed to process image'}
        return Response(
            response=json.dumps(error_response),
            status=500,
            mimetype='application/json'
        )

if __name__ == "__main__":
    # Use the appropriate port for deployment and localhost
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT variable or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
