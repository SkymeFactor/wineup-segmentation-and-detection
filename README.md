# Segmantation and recognition service (segandrec-service).
## Description
ITMO project for microservices. Provides the backend service for bottles segmentation and (not yet) mark detection.
### Models used:
 - Mask-RCNN for segmentation
 - Exception (probably) for mark detection
## Ease-Of-Use
First of all, let's download the checkpoints of pre-trained mask-rcnn and unpack them into ./MaskRCNN/weights folder. You must make sure that files ./MaskRCNN/weights/variables/ and ./MaskRCNN/weights/saved_model.pb are available from here by exact same paths.

Tensorflow checkpoints are publicly available by link:
https://drive.google.com/file/d/1Y2YSaUfsKISgbVzDlibVWYbj4bTfUN_1/view?usp=sharing

Next big thing is changing the host file to contain the address you will need (e.g. http://localhost:5000)
### Run server locally:
Let's execute the following command in order to install all necessarry python libraries:

`pip3 install -r requirements.txt`

Now, run the flask backend program by executing:

`python3 app.py` or `flask run -h 0.0.0.0 -p 5000`

### Run server using docker container:
In order to build the docker image, run:

`docker build -t flask .`

Create a container and traverse the 5000 port onto the local machine:

`docker run -d -p 5000:5000 flask`

### Run client:
And finally, let's execute the example client code to test if everything works ok:

`python3 request_example.py`

As a result, I presume you will see the picture of a bottle with whitened background on your screen.

Note: if you are running NOT from docker image, make sure that you have at least following packages installed on your system:
    `Pillow`,
    `numpy`,
    `opencv-python`,
    `requests`,
    `tensorflow`
## API Documentation:
You can see more about the service API by running it on your local machine and following the swagger link:
`http://IP:PORT/api/v1.0/swagger_ui`


Segmentation has to be performed by the following scenario:
`http://IP:PORT/api/v1.0/segmentation`

As s DATA parameter you should be sending JSON structure containing link to image
### JSON Request structure:
```
JSON: {
    image: "link"
}
```
### Response structure for successful segmentations:
```
JSON: {
    status: 200
    segmentation: "link"
    mask: "link"
}
```
### Response structure for errors 400, 404, 405 and 500:
```
JSON: {
    status: int
    error: 'Text of error'
}
```
