# Segmantation and recognition service (segandrec).
## Description
ITMO project for microservices. Provides the backend service for bottles segmentation and (not yet) mark detection.
## Ease-Of-Use
First of all, let's download the checkpoints of pre-trained mask-rcnn and unpack them into ./MaskRCNN/weights folder. You must make sure that files ./MaskRCNN/weights/variables/ and ./MaskRCNN/weights/saved_model.pb are available from here by exact same paths.

Tensorflow checkpoints are publicly available by link:
https://drive.google.com/file/d/1Y2YSaUfsKISgbVzDlibVWYbj4bTfUN_1/view?usp=sharing
### Run Locally:
Let's execute the following command in order to install all necessarry python libraries:

`pip3 install -r requirements.txt`

Now, run the flask backend program by executing:

`python3 app.py` or `flask run -h 0.0.0.0 -p 5000`

### Run using docker container:
In order to build the docker image, run:

`docker build -t flask .`

Create the container and traverse the 5000 port to local machine:

`docker run -d -p 5000:5000 flask`

### Run client:
And finally, let's execute the example code to test if everything works ok:

`python3 request_example.py`

As a result I expect, you will see the picture of a bottle with whitened background on your screen.
## Responses
### Response structure for successful segmentations:
```
JSON: {
    status: 200
    image: [...]
    mask: [...]
}
```
### Response structure for errors 400, 404, 405 and 500:
```
JSON: {
    status: int
    error: 'Text of error'
}
```
