from PIL import Image
import numpy as np
import tensorflow as tf
import os
import mrcnn_utils


class SegmentationBackend():
    #-----------------------------------------------------------------------------------------
    # Initialize session
    def __init__(self, saved_model_dir='./mask-rcnn/1555659850', CUDA_is_visible=False):
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
    def run(self, image_path, max_boxes_to_draw=50, min_score_thresh=0.8):
        if not os.path.isfile(image_path):
            raise Exception(('Invalid image_path={0}.').format(image_path))
      
        with open(image_path, 'rb') as f:
          np_image_string = np.array([f.read()])
        
        image = Image.open(image_path)
        width, height = image.size
        np_image = np.array(image.getdata()).reshape([height, width, 3]).astype(np.uint8)
      
        num_detections, detection_boxes, detection_classes, detection_scores, detection_masks, image_info = self.__process_image__(
                              np_image_string)

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
        