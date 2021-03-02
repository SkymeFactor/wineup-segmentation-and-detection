from __future__ import unicode_literals

import sys, os, json, time
from flask import Flask, request, jsonify, make_response, abort, send_file, render_template
from flask_swagger_ui import get_swaggerui_blueprint
from cv2 import cv2
from io import BytesIO
from PIL import Image
from threading import Thread
import requests, string, random
# Append MaskRCNN to sys.path.  --->  Now deprecated.
#sys.path.insert(1, os.path.join(sys.path[0], 'MaskRCNN'))
#sys.path.insert(1, os.path.join(sys.path[0], 'Bottles_Similarity_Check'))
from MaskRCNN import mrcnn
import numpy as np

app = Flask(__name__)

sessionStorage = {}

backend = mrcnn.SegmentationBackend(CUDA_is_visible=False)

# Set up swagger addresses (i.e. base and redirect)
base_url = 'http://77.234.215.138:18080/ml4-recommendation-service'
SWAGGER_URL = '/api/v1.0/swagger-ui'
API_URL = base_url + '/api/v1.0/swagger.json'

@app.route('/api/v1.0/docs', methods=['GET'])
def get_swagger():
    return render_template('swaggerui.html')

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'status': 400, 'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'status': 404, 'error': 'Not found'}), 404)

@app.errorhandler(405)
def not_allowed(error):
    return make_response(jsonify({'status': 405, 'error': 'Not allowed'}), 405)

@app.errorhandler(422)
def unprocessable_entity(error):
    return make_response(jsonify({'status': 422, 'error': 'Unprocessable Entity'}), 422)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'status': 500, 'error': 'Internal server error'}), 500)

def image_autoremove(mask_name, segm_name):
    abs_mask_name = './.temp/' + mask_name + '.jpg'
    abs_segm_name = './.temp/' + segm_name + '.jpg'
    
    time.sleep(30)
    
    if os.path.isfile(abs_mask_name):
        os.remove(abs_mask_name)
    if os.path.isfile(abs_segm_name):
        os.remove(abs_segm_name)
    
    return

@app.route("/api/v1.0/segmentation", methods=['POST'])
def segmentation():
    # Inherit the global backend
    global backend
    # Check if we have a valid request structure
    if not request.json or not 'image' in request.json:
        abort(400)
    # Create response's basic structure
    response = {
        'status': 200
    }

    #mask, image = [], []
    #print(request.json)

    # Obtain the image by link
    fileRequest = requests.get(request.json['image'])
    # If image doesn't exist, raise http error
    if fileRequest.status_code == 200:
        image = Image.open(BytesIO(fileRequest.content))
    else:
        abort(422)
    # Get image size
    width, height = image.size
    # Run the segmentation
    result = backend.run(np.array(image.getdata()).reshape([height, width, 3]).astype(np.uint8))
    
    # Debugging code.   --->  Now deprecated.
    #image.show()
    #print(width, height)
    #result = backend.run(np.array(request.json['image']).astype(np.uint8))
    #mask = result[0].tolist()
    #image = result[1].tolist()

    # Lambda function for generating random names
    random_str = lambda: ''.join([random.choice(string.ascii_letters + string.digits) for i in range(20)])

    # Pick up some random names that aren't in the folder
    while True: 
        segm_name = random_str()
        if not os.path.isfile('./.temp/' + segm_name + '.jpg'):
            break
    while True: 
        mask_name = random_str()
        if not os.path.isfile('./.temp/' + mask_name + '.jpg'):
            break
    
    # Save images
    cv2.imwrite('./.temp/' + mask_name + '.jpg', result[0])
    cv2.imwrite('./.temp/' + segm_name + '.jpg', result[1])

    # Start the delayed deletion procedure
    Thread(target=image_autoremove, args=[mask_name, segm_name]).start()
    
    # Form response fields
    response.update({"segmentation": base_url + '/api/v1.0/get_image=' + segm_name})
    response.update({"mask": base_url + '/api/v1.0/get_image=' + mask_name})

    return jsonify(response)

@app.route("/api/v1.0/get_image=<img>", methods=['GET'])
def get_image_from_temp(img):
    path = os.path.join('./.temp/', img + '.jpg')
    if os.path.isfile(path):
        return send_file(path, mimetype='image/jpg', cache_timeout=-1)
    else:
        abort(404)

@app.route("/api/v1.0/get_files_num", methods=['GET'])
def get_files_num():
    return str(len(os.listdir('./.temp')))

@app.route("/api/v1.0/swagger.json", methods=['GET'])
def get_swagger_json():
    with open ("swagger.json") as f:
        swagger_data = json.load(f)
    f.close()
    return jsonify(swagger_data)

if __name__ == "__main__":
    # Create swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, 
        API_URL,
        config={
            'app_name': "Segmentation and recognition service"
        }
    )
    # Register swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint)
    app.run(debug=True, host='0.0.0.0', port=5000)