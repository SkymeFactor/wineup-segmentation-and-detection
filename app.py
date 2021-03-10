from __future__ import unicode_literals

import sys, os, json, time
from flask import Flask, request, jsonify, make_response, abort, send_file, render_template
from io import BytesIO
from PIL import Image
from threading import Thread
import requests, string, random
from MaskRCNN import mrcnn
import numpy as np
import kafka_controller

# Create flask application
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Create mrcnn backend
backend = mrcnn.SegmentationBackend(CUDA_is_visible=False)

# Set up base url address
with open("./host", 'r') as file:
    base_url = file.read()

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

# Function that is used to automatically remove old images
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
    Image.fromarray(result[0], "RGB").save('./.temp/' + mask_name + '.jpg')
    Image.fromarray(result[1], "RGB").save('./.temp/' + segm_name + '.jpg')

    # Start the delayed deletion procedure
    Thread(target=image_autoremove, args=[mask_name, segm_name]).start()
    
    # Form response fields
    response.update({"segmentation": base_url + '/api/v1.0/get_image=' + segm_name})
    response.update({"mask": base_url + '/api/v1.0/get_image=' + mask_name})

    return jsonify(response)

@app.route("/api/v1.0/get_image=<img>", methods=['GET'])
def get_image_from_temp(img):
    path = os.path.join('./.temp/', img + '.jpg')
    # In case if image exists return it
    if os.path.isfile(path):
        return send_file(path, mimetype='image/jpg', cache_timeout=-1)
    else:
        abort(404)

@app.route("/api/v1.0/swagger.json", methods=['GET'])
def get_swagger_json():
    with open ("./static/swagger.json") as f:
        swagger_data = json.load(f)
    f.close()
    swagger_data.update({"host": base_url.replace('http://', '')})
    return jsonify(swagger_data)

@app.route('/api/v1.0/swagger_ui', methods=['GET'])
def get_swagger():
    # Render swagger-ui page
    return render_template(
        template_name_or_list='swaggerui.html',
        css = base_url + '/static/css/swagger-ui.css',
        fav32 = base_url + '/static/img/favicon-32x32.png',
        fav16 = base_url + '/static/img/favicon-16x16.png',
        bundle_js = base_url + '/static/js/swagger-ui-bundle.js',
        standalone_preset_js = base_url + '/static/js/swagger-ui-standalone-preset.js',
        swagger_json = base_url + '/api/v1.0/swagger.json'
    )

@app.route('/api/v1.0/test_kafka', methods=['GET'])
def test_kafka():
    kafka_log = kafka_controller.kafka_try_send()
    return jsonify(kafka_log)

if __name__ == "__main__":
    # Run flask app in broadcasting mode
    app.run(debug=False, host='0.0.0.0', port=5000)
