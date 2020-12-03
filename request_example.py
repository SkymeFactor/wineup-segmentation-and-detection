import requests
import numpy as np
from PIL import Image
from cv2 import cv2

# Open the image
image = Image.open("./Test_Images/test2.jpg")
width, height = image.size
np_image = np.array(image.getdata()).reshape([height, width, 3]).astype(np.uint8)

# Form the request
data = {
    "image": np_image.tolist()
}

# POST image to server and collect the response
response = requests.post("http://localhost:5000/segandrec-service/api/v1.0/segmentation", json=data)

# Check if response is valide
if response.json()['status'] == 200:
    # Print the image size
    print(np.array(response.json()["segmentation"]).astype(np.uint8).shape)
    # Draw it on your screen
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 800, 600)
    cv2.imshow("Image", cv2.cvtColor(np.array(response.json()["segmentation"]).astype(np.uint8), cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    # If the response is invalide, show the error message
    print('Error ' + str(response.json()['status']) + ': ' + response.json()['error'])