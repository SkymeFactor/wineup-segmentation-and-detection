import os
import json
import random
import string
import time
import typing
from io import BytesIO
from threading import Thread

import flask
import numpy as np
import requests
from PIL import Image

import config
import kafka_controller
from MaskRCNN import mrcnn


# Create flask application
app = flask.Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Create mrcnn backend
backend = mrcnn.SegmentationBackend(CUDA_is_visible=False)

kafka_thread = Thread(target=kafka_controller.serve, name='kafka_thread')


@app.errorhandler(400)
def bad_request(error) -> flask.Response:
    return flask.make_response(
        flask.jsonify({'status': 400, 'error': 'Bad request'}), 400
    )


@app.errorhandler(404)
def not_found(error: typing.Any) -> flask.Response:
    return flask.make_response(
        flask.jsonify({'status': 404, 'error': 'Not found'}), 404
    )


@app.errorhandler(405)
def not_allowed(error: typing.Any) -> flask.Response:
    return flask.make_response(
        flask.jsonify({'status': 405, 'error': 'Not allowed'}), 405
    )


@app.errorhandler(422)
def unprocessable_entity(error: typing.Any) -> flask.Response:
    return flask.make_response(
        flask.jsonify({'status': 422, 'error': 'Unprocessable Entity'}), 422
    )


@app.errorhandler(500)
def internal_error(error: typing.Any) -> flask.Response:
    return flask.make_response(
        flask.jsonify({'status': 500, 'error': 'Internal server error'}), 500
    )


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
def segmentation() -> flask.Response:
    # Inherit the global backend
    global backend
    # Check if we have a valid request structure
    if not flask.request.json or 'image' not in flask.request.json:
        return flask.abort(400)

    # Obtain the image by link
    file_request = requests.get(flask.request.json['image'])
    # If image doesn't exist, raise http error
    if file_request.status_code == 200:
        image = Image.open(BytesIO(file_request.content))
    else:
        return flask.abort(422)
    # Get image size
    width, height = image.size
    # Run the segmentation
    result = backend.run(
        np.array(image.getdata()).reshape([height, width, 3]).astype(np.uint8))

    # Lambda function for generating random names
    def random_str() -> str:
        return ''.join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(20)]
        )

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

    return flask.jsonify({
        'status': 200,
        'segmentation': config.RECOMMENDATION_GET_IMAGE_ENDPOINT + segm_name,
        'mask': config.RECOMMENDATION_GET_IMAGE_ENDPOINT + mask_name,
    })


@app.route("/api/v1.0/get_image=<img_name>", methods=['GET'])
def get_image_from_temp(img_name: str) -> flask.Response:
    path = os.path.join('./.temp/', img_name + '.jpg')
    # In case if image exists return it
    if os.path.isfile(path):
        return flask.send_file(path, mimetype='image/jpg', cache_timeout=-1)
    else:
        return flask.abort(404)


@app.route("/api/v1.0/swagger.json", methods=['GET'])
def get_swagger_json():
    with open("./static/swagger.json") as f:
        swagger_data = json.load(f)
    swagger_data.update(
        {"host": config.RECOMMENDATION_SERVICE_HOST.replace('http://', '')}
    )
    return flask.jsonify(swagger_data)


@app.route('/api/v1.0/swagger_ui', methods=['GET'])
def get_swagger() -> flask.Response:
    # Render swagger-ui page
    static_url_prefix = f'{config.RECOMMENDATION_SERVICE_HOST}/static'
    return flask.render_template(
        template_name_or_list='swaggerui.html',
        css=f'{static_url_prefix}/css/swagger-ui.css',
        fav32=f'{static_url_prefix}/img/favicon-32x32.png',
        fav16=f'{static_url_prefix}/img/favicon-16x16.png',
        bundle_js=f'{static_url_prefix}/js/swagger-ui-bundle.js',
        standalone_preset_js=f'{static_url_prefix}/js/swagger-ui-standalone-preset.js',
        swagger_json=f'{static_url_prefix}/v1.0/swagger.json'
    )


@app.route('/api/v1.0/test_kafka', methods=['GET'])
def test_kafka() -> str:
    wine_id = flask.request.args.get('wine_id', '1')
    kafka_controller.send_event_from_catalog(wine_id)
    return "Sent kafka message"


if __name__ == "__main__":
    # Run flask app in broadcasting mode
    kafka_thread.start()
    app.run(debug=False, host='0.0.0.0', port=5000)
