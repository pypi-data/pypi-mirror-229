import cv2
from ocrpackage import f_utils
import dlib
import numpy as np
from ocrpackage.f_orientation_detection import detect_face_orientation


# instaciar detectores
frontal_face_detector    = dlib.get_frontal_face_detector()
profile_detector         = detect_face_orientation()

def detect_liveness(im):
    
    gray = gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # face detection
    rectangles = frontal_face_detector(gray, 0)
    boxes_face = f_utils.convert_rectangles2array(rectangles,im)
    if len(boxes_face)!=0:
        # use only the biggest face
        areas = f_utils.get_areas(boxes_face)
        index = np.argmax(areas)
        rectangles = rectangles[index]
        boxes_face = [list(boxes_face[index])]

    # -------------------------------------- profile_detection ---------------------------------------
    '''
    input:
        - imagen gray
    output:
        - status: "ok"
        - profile: ["right"] or ["left"]
        - box: [[579, 170, 693, 284]]
    '''
    box_orientation, orientation = profile_detector.face_orientation(gray)

    # -------------------------------------- output ---------------------------------------
    output = {
        'box_face_frontal': boxes_face,
        'box_orientation': box_orientation,
        'orientation': orientation,
    }
    return output

