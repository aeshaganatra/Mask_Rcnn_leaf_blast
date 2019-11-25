import os
import sys

import cv2
import time

import mrcnn.model as modellib
from mrcnn import utils, visualize
import imutils


# Root directory of the project
from samples.leafblast.custom import CustomConfig

ROOT_DIR = os.path.abspath("./")

sys.path.append(os.path.join(ROOT_DIR, "model"))  # To find local version

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn.h5")
# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)


class InferenceConfig(CustomConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1


config = InferenceConfig()
config.display()

# Create model object in inference mode.
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

# Load weights trained on MS-COCO
model.load_weights(COCO_MODEL_PATH, by_name=True)

# COCO Class names
# Index of the class in the list is its ID. For example, to get ID of
# the teddy bear class, use: class_names.index('teddy bear')
class_names = ['leafblast']

stream = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    grabbed, frame = stream.read()
    if not grabbed:
        break

    results = model.detect([frame], verbose=1)
    r = results[0]

    boxes = r['rois']
    masks = r['masks']
    class_ids = r['class_ids']
    scores = r['scores']

    # Run detection
    start = time.time()
    masked_image = visualize.get_masked_image(frame, boxes, masks, class_ids, class_names, scores)
    end = time.time()
    print("Inference time: {:.2f}s".format(end - start))

    # Display the resulting frame
    cv2.imshow('', masked_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
stream.release()
cv2.destroyAllWindows()