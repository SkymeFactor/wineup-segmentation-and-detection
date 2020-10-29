from PIL import Image
import numpy as np
import mrcnn
from cv2 import cv2

if __name__ == "__main__":

    # TODO: parse these arguments
    image_path = 'my_test.jpg'
    output_image_path = 'test_results.jpg'

    backend = mrcnn.SegmentationBackend()
    mask, image = backend.run(image_path)
    del backend

    Image.fromarray(image.astype(np.uint8)).save(output_image_path)
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 800, 600)
    cv2.imshow("Image", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
