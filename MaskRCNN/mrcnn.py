import numpy as np
import tensorflow as tf
import os
from MaskRCNN import mrcnn_utils
from cv2 import cv2


class SegmentationBackend():
    #-----------------------------------------------------------------------------------------
    # Initialize session
    def __init__(self, saved_model_dir=os.path.join(os.path.dirname(__file__), 'weights/'), CUDA_is_visible=False):
        if CUDA_is_visible == False:
          os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        self.session = tf.compat.v1.Session(graph=tf.Graph())
        _ = tf.compat.v1.saved_model.loader.load(self.session, ['serve'], saved_model_dir)

    #-----------------------------------------------------------------------------------------
    # Close session
    def __del__(self):
        self.session.close()

    #-----------------------------------------------------------------------------------------
    # Process image
    #@tf.function
    def __process_image__(self, np_image_string):
        return self.session.run(['NumDetections:0', 'DetectionBoxes:0', 'DetectionClasses:0', 'DetectionScores:0', 'DetectionMasks:0', 'ImageInfo:0'],
                              feed_dict={'Placeholder:0': np_image_string})

    #-----------------------------------------------------------------------------------------
    # Run session with image
    def run(self, np_image, max_boxes_to_draw=50, min_score_thresh=0.8):
        """Explicitly running the model on a given image.
        Parameters:
        ----------
        np_image: [height, width, depth] np.ndarray
            Numpy array containing RGB image.
        max_boxes_to_draw: int
            Determins how many segmentations can possibly be detected (default is 50).
        min_score_thresh: int,
            Determins on the minimal threshold of confidence (default is 0.8).
        Returns:
        ----------
        [mask, np_image] list, each element has np.ndarray type and original image size.
        """
        height, width, _ = np_image.shape
        
        # As far as the model has it's own built in .jpg encoder, convert the array into .jpg
        _, encoded_image = cv2.imencode('.jpg', cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR))
        encoded_image = encoded_image.tobytes()
        
        num_detections, detection_boxes, detection_classes, detection_scores, detection_masks, image_info = self.__process_image__(
                              np.array([encoded_image]) )

        num_detections = np.squeeze(num_detections.astype(np.int32), axis=(0,))
        detection_boxes = np.squeeze(detection_boxes * image_info[0, 2], axis=(0,))[0:num_detections]
        detection_scores = np.squeeze(detection_scores, axis=(0,))[0:num_detections]
        detection_classes = np.squeeze(detection_classes.astype(np.int32), axis=(0,))[0:num_detections]
        instance_masks = np.squeeze(detection_masks, axis=(0,))[0:num_detections]
        ymin, xmin, ymax, xmax = np.split(detection_boxes, 4, axis=-1)
        processed_boxes = np.concatenate([xmin, ymin, xmax - xmin, ymax - ymin], axis=-1)
        segmentations = mrcnn_utils.generate_segmentation_from_masks(instance_masks, processed_boxes, height, width)
    
        idx = []
        for i in range(min(num_detections, max_boxes_to_draw)):
            if detection_classes[i] == 44 and detection_scores[i] >= min_score_thresh:
                idx.append(i)
        
        mask = np.zeros((height, width, 3))

        for i in range(len(idx)):
            mask += segmentations[i, :, :, np.newaxis]
        
        mask = mrcnn_utils.smooth_contours_on_mask(mask)
        if not mrcnn_utils.check_background_quality(mask, np_image):
            np_image = mrcnn_utils.add_white_background(mask, np_image)

        return [mask, np_image]
        