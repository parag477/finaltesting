from flask import Flask, render_template, request, jsonify
import cv2
import base64
import numpy as np
import io
from makeup_app import MakeupApplication  # Import your class

app = Flask(__name__)
makeup_app = MakeupApplication()

def process_image(image_data):
    # Decode the image
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Apply makeup effect
    processed_img = makeup_app.process_frame(img)

    # Convert the processed image back to base64
    _, buffer = cv2.imencode('.jpg', processed_img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return img_str

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    image_data = data['image']
    processed_image = process_image(image_data)
    return jsonify({'processed_image': processed_image})

if __name__ == "__main__":
    app.run(debug=True)
