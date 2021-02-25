from __future__ import unicode_literals

import sys, os, json
from flask import Flask, request, jsonify, make_response, abort
from flask_swagger_ui import get_swaggerui_blueprint
from cv2 import cv2
# Append MaskRCNN to sys.path.  --->  Now deprecated.
#sys.path.insert(1, os.path.join(sys.path[0], 'MaskRCNN'))
#sys.path.insert(1, os.path.join(sys.path[0], 'Bottles_Similarity_Check'))
from MaskRCNN import mrcnn
import numpy as np

app = Flask(__name__)

sessionStorage = {}

backend = mrcnn.SegmentationBackend(CUDA_is_visible=False)

# Set up swagger addresses (i.e. base and redirect)
SWAGGER_URL = '/api/v1.0/swagger-ui'
API_URL = 'http://localhost:5000/api/v1.0/swagger.json'

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'status': 400, 'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'status': 404, 'error': 'Not found'}), 404)

@app.errorhandler(405)
def not_allowed(error):
    return make_response(jsonify({'status': 405, 'error': 'Not allowed'}), 405)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'status': 500, 'error': 'Internal server error'}), 500)


@app.route("/api/v1.0/segmentation", methods=['POST'])
def segmentation():
    global backend
    if not request.json or not 'image' in request.json:
        abort(400)
    
    response = {
        'status': 200
    }

    mask, image = [], []

    result = backend.run(np.array(request.json['image']).astype(np.uint8))
    mask = result[0].tolist()
    image = result[1].tolist()
    
    response.update({"segmentation": image})
    response.update({"mask": mask})

    return jsonify(response)


@app.route("/api/v1.0/swagger.json", methods=['GET'])
def get_swagger_json():
    with open ("swagger.json") as f:
        swagger_data = json.load(f)
    f.close()
    return jsonify(swagger_data)

# Create swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, 
    API_URL,
    config={
        'app_name': "Test application"
    }
)

# Register swagger UI blueprint
app.register_blueprint(swaggerui_blueprint)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)