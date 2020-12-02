from __future__ import unicode_literals

import sys, os
from flask import Flask, request, jsonify, make_response, abort
from cv2 import cv2
# Append MaskRCNN to sys.path.  --->  Now deprecated.
#sys.path.insert(1, os.path.join(sys.path[0], 'MaskRCNN'))
#sys.path.insert(1, os.path.join(sys.path[0], 'Bottles_Similarity_Check'))
from MaskRCNN import mrcnn
import numpy as np

app = Flask(__name__)

sessionStorage = {}

backend = mrcnn.SegmentationBackend(CUDA_is_visible=False)

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


@app.route("/segandrec/api/v1.0/segmentation", methods=['POST'])
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

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)