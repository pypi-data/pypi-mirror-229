# This code block is importing various Python packages that will be used in the OCR (Optical Character
# Recognition) and facial recognition steps of the program. These packages include OpenCV (cv2),
# Pillow (Image), EasyOCR (easyocr), Pandas (pd), scikit-image (skimage), regular expressions (re),
# datetime, concurrent.futures, NumPy (np), TensorFlow (tf), VGG16 model from Keras
# (tensorflow.keras.applications.vgg16), scipy.spatial.distance, model_from_json from Keras
# (tensorflow.keras.models), subprocess, urllib.request, dlib, time, matplotlib.pyplot, facenet, json,
# io, and importlib.resources.
import base64
import cv2
import io
import numpy as np
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import easyocr
from PIL import Image
from pkg_resources import resource_filename
from scipy.spatial.distance import cosine
from skimage.transform import radon
from retinaface import RetinaFace
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import model_from_json

# front_ID='2bbc5f9b-037c-44e3-a1e2-ac968f8c065b_2022-10-27T13_40_50.949379.jpg'

class IdentityVerification:

    def __init__(self):
        """
        This is the initialization function of a class that imports a spoof model and loads an OCR
        reader.
        """
        #self.images = images
        self.spoofmodel = self.import_spoofmodel()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.reader_future = self.executor.submit(self.create_easyocr_reader)
        # front_id='2bbc5f9b-037c-44e3-a1e2-ac968f8c065b_2022-10-27T13_40_50.949379.jpg'
        # selfie='2bbc5f9b-037c-44e3-a1e2-ac968f8c065b_2022-10-27T13_40_50.949379.jpg'
        # country = 'UAE'
        # self.extract_ocr_info(front_id, selfie, country)

    def load_easyocr(self):
        return self.reader_future.result()
        
    def create_easyocr_reader(self):
        return easyocr.Reader(['en'])

    def image_conversion(self,image):  
        """
        This function decodes a base64 string data and returns an image object.
        :return: an Image object that has been created from a base64 encoded string.
        """
        image=image.split(',')[-1]
        # Decode base64 String Data
        img=Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))
        return img

    def rgb2yuv(self, img):
        """
        Convert an RGB image to YUV format.
        """
        img=np.array(img)
        return cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    
    # def crop_image_and_save(self, img_path):
    #     net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    #     classes = []
    #     with open("coco.names", "r") as f:
    #         classes = f.read().strip().split("\n")
    #     image = cv2.imread(img_path)
    #     height, width = image.shape[:2]
    #     blob = cv2.dnn.blobFromImage(image, scalefactor=1/255.0, size=(416, 416), swapRB=True, crop=False)
    #     net.setInput(blob)
    #     layer_names = net.getUnconnectedOutLayersNames()
    #     detections = net.forward(layer_names)
    #     id_card_class_index = classes.index("book")
    #     id_card_boxes = []

    #     for detection in detections[0]:
    #         scores = detection[5:]
    #         class_id = np.argmax(scores)
    #         confidence = scores[class_id]

    #         if class_id == id_card_class_index and confidence > 0.5:
    #             center_x = int(detection[0] * width)
    #             center_y = int(detection[1] * height)
    #             w = int(detection[2] * width)
    #             h = int(detection[3] * height)
    #             x = int(center_x - w / 2)
    #             y = int(center_y - h / 2)
    #             id_card_boxes.append((x, y, w, h))
        
    #     if id_card_boxes:
    # #         print("yes")
    #         largest_id_card_box = max(id_card_boxes, key=lambda box: box[2] * box[3])

    #         x, y, w, h = largest_id_card_box
    #         largest_id_card = image[y:y+h, x:x+w]
    #         img_path = "id_card_cropped.jpg"
    #         cv2.imwrite(img_path, largest_id_card)
    #         print("saved")
    #     else:
    #         largest_id_card = cv2.imread(img_path)
            
    #     return largest_id_card, img_path
    
    # def find_bright_areas(self, image):
    #     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #     thresh_image = cv2.threshold(gray_image, 210, 255, cv2.THRESH_BINARY)[1]

    #     contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #     bright_areas = []

    #     for contour in contours:
    #         bounding_box = cv2.boundingRect(contour)

    #         area = bounding_box[2] * bounding_box[3]

    #         if area > 800:
    #             bright_areas.append(bounding_box)

    #     return len(bright_areas)

    # def is_blurry(self, image, threshold=150):
    #     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    #     laplacian_variance = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
    #     return laplacian_variance < threshold
        
    # def check_image_quality(self,image_path):
    #     id_card, img_path = self.crop_image_and_save(image_path)
    #     bright_result = self.find_bright_areas(id_card)
    #     blurry_result = self.is_blurry(id_card)

    #     if bright_result>=1:
    #         print("The image has high lights.")
    #     else:
    #         print("The image brightness is fine.")

    #     if blurry_result:
    #         print("The image is blurry.")
    #     else:
    #         print("The image is not blurry.")

    def check_image_quality(self, image, brightness_threshold=128, blur_threshold=300):
        try:
            # Check if the image can be converted from RGB to YUV
            yuv_img = self.rgb2yuv(self.image_conversion(image))

        except Exception as e:
            raise Exception("Failed to convert image from RGB to YUV: " + str(e))

        try:
            # Check brightness
            brightness = np.average(yuv_img[..., 0])
            if brightness > brightness_threshold:
                raise Exception(f"Image is too bright. Brightness: {brightness}, Threshold: {brightness_threshold}")
        except Exception as e:
            raise Exception("Failed to check image brightness: " + str(e))

        try:
            # Check blurriness
            image = np.array(self.image_conversion(image))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            fm = cv2.Laplacian(gray, cv2.CV_64F).var()
            if fm < blur_threshold:
                raise Exception(f"Image is too blurry. Blurriness: {fm}, Threshold: {blur_threshold}")
        except Exception as e:
            raise Exception("Failed to check image blurriness: " + str(e))

    def import_spoofmodel(self):
        
        # load model from json
        json_path = resource_filename('ocrpackage', 'antispoofing_model.json')
        with open(json_path, 'r') as json_file:
            loaded_model_json = json_file.read()
            
        # create models
        spoofmodel = model_from_json(loaded_model_json)
        
        # load weights
        weights_path = resource_filename('ocrpackage', 'antispoofing_model.h5')
        spoofmodel.load_weights(weights_path)

        return spoofmodel

    # def get_image(self, n):
    #     with resources.open_binary('ocrapp', self.images[n]) as fp:
    #         img_data = fp.read()
    #     img = Image.open(io.BytesIO(img_data))
    #     return img


    def process_image(self,front_id):
        img = self.image_conversion(front_id)
        img = np.array(img)
        I = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = I.shape
        if (w > 640):
            I = cv2.resize(I, (640, int((h / w) * 640)))
        I = I - np.mean(I)
        sinogram = radon(I)
        r = np.array([np.sqrt(np.mean(np.abs(line) ** 2)) for line in sinogram.transpose()])
        rotation = np.argmax(r)
        im = self.image_conversion(front_id)
        angle = round(abs(90 - rotation)+0.5)
        out = im.rotate(angle, expand=True)
        return out

    def get_ocr_results(self, front_id):
        image = self.process_image(front_id)
        image_array = np.array(image)
        results = self.load_easyocr().readtext(image_array)  # Access the reader object directly
        id_infos = [ele[-2] for ele in results]
        return id_infos


    def extract_letters_before_sign(self, text, sign='<'):
        match = re.search(r'([A-Za-z]+)(?='+re.escape(sign)+')', text)
        if match:
            return match.group(1)
        else:
            return None

    # def hogDetectFaces(self,image, hog_face_detector):
    #     """
    #     The function detects faces in an image using a HOG (Histogram of Oriented Gradients) face detector
    #     and returns the biggest detected face.
        
    #     :param image: The input image on which face detection is to be performed
    #     :param hog_face_detector: The hog_face_detector is a pre-trained object detection model that uses
    #     Histogram of Oriented Gradients (HOG) features to detect faces in an image. It is provided as a
    #     parameter to the hogDetectFaces function to perform face detection on the input image
    #     :return: the biggest detected face in the input image.
    #     """

    #     _ , width, _ = image.shape

    #     output_image = image.copy()

    #     imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    #     results = hog_face_detector(imgRGB, 0)

    #     biggest_face = None
    #     max_area = 0
    #     for bbox in results:
    #         x1 = bbox.left()
    #         y1 = bbox.top()
    #         x2 = bbox.right()
    #         y2 = bbox.bottom()

    #         area = (x2 - x1) * (y2 - y1)
    #         if area > max_area:
    #             max_area = area
    #             biggest_face = image[y1:y2, x1:x2]

    #         cv2.rectangle(output_image, pt1=(x1, y1), pt2=(x2, y2), color=(0, 255, 0), thickness=width // 200)

    #     return  biggest_face
    
    def retina_resnet_detect_faces(self, image):
        # img = cv2.imread(image)
        faces = RetinaFace.detect_faces(image)

        largest_face = None
        facial_area = None
        largest_area = 0

        for face_name, face_data in faces.items():
            facial_area = face_data["facial_area"]
            area = (facial_area[2] - facial_area[0]) * (facial_area[3] - facial_area[1])
            
            if area > largest_area:
                largest_area = area
                largest_face = face_data

        if largest_face:
            facial_area = largest_face["facial_area"]
            largest_face = image[facial_area]
        
        return largest_face

    def extract_features(self,img_data, model):
        """
        This function takes image data and a model as input, resizes and preprocesses the image, and returns
        the predicted features using the model.
        
        :param img_data: img_data is an input image data that needs to be processed by the model. It is
        expected to be a numpy array representing an image
        :param model: The "model" parameter is a pre-trained deep learning model that is used to extract
        features from an image. The specific model used is a convolutional neural network (CNN) that has been trained on a large dataset of images. The
        function resizes
        :return: The function `extract_features` returns the output of the `model.predict` method applied to
        the preprocessed input image data. This output represents the extracted features of the image as
        learned by the model.
        """
        img_data = cv2.resize(img_data, (224, 224))
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_input(img_data)
        return model.predict(img_data)

    def compute_similarity(self,features1, features2):
        """
        The function computes the similarity between two sets of features using the cosine similarity
        metric.
        """
        return 1 - cosine(features1.flatten(), features2.flatten())

    def extract_face_and_compute_similarity(self,front_id, selfie):
        """
        This function extracts the biggest face from two images, extracts features from them using a
        pre-trained VGG16 model, and computes the similarity between the two images.
        
        :param n: The index of the first image to be loaded and processed, defaults to 0 (optional)
        :param m: The parameter "m" is used as an input to the function
        "extract_face_and_compute_similarity" and is set to 1 by default. It is used to specify the index of
        the second image to be loaded and compared with the first image, defaults to 1 (optional)
        :return: the similarity score between two images after detecting and extracting the biggest face
        from each image and computing their features using a pre-trained VGG16 model.
        """

        # Load the VGG16 model with pre-trained weights
        self.model = VGG16(weights='imagenet', include_top=False, pooling='avg')

        # Load the images
        image1 = np.array(self.process_image(front_id))
        image2 = np.array(self.process_image(front_id))

         # Convert the images to RGB format
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGRA2RGB)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGRA2RGB)

        # Detect faces and extract the biggest face
        biggest_face1 = self.retina_resnet_detect_faces(image1)
        biggest_face2 = self.retina_resnet_detect_faces(image2)

        if biggest_face1 is None or biggest_face2 is None:
            raise ValueError("No face detected in one or both images")

        # Extract features from the images
        image_features1 = self.extract_features(biggest_face1, self.model)
        image_features2 = self.extract_features(biggest_face2, self.model)

        # Compute the similarity between the images
        similarity = self.compute_similarity(image_features1, image_features2)

        return similarity

    def extract_ocr_info(self,front_id,selfie,country):

        id_infos= self.get_ocr_results(front_id)
        print(f"OCR results: {id_infos}")
        similarity=self.extract_face_and_compute_similarity(front_id, selfie)
        
        #last_label='Real'
        if country=='UK':
                        try:
                            date_pattern = r"(\d{1,2}\.\d{1,2}\.\d{4})"
                            dates=[]
                            for item in id_infos:
                                match = re.search(date_pattern, item)
                                if match:
                                    dates.append(match.group(1))
                            Dob=dates[0]
                            Expiry_date=dates[-1] if len(dates)<4 else dates[-2]
                            Issuing_Date=dates[1]
                            
                        except:
                            
                            date_pattern = r"(\d{1,2}-\d{1,2}-\d{2,4})" 
                            dates=[]
                            for item in id_infos:
                                match = re.search(date_pattern, item)
                                if match:
                                    dates.append(match.group(1))

                            condition=[listele for listele in [ele.split('-') for ele in dates] if len(listele[-1])>2]
                            if len(condition)>0:
                                ele_index=dates.index('-'.join([listele for listele in [ele.split('-') for ele in dates] if len(listele[-1])>2][0]))
                                element='-'.join([listele for listele in [ele.split('-') for ele in dates] if len(listele[-1])>2][0])
                                dates.pop(ele_index)
                                new_date=element[:-1]
                                dates.insert(ele_index,new_date)
                                Dob=dates[0]
                                Expiry_date=dates[-1] if len(dates)<4 else dates[-2]
                                Issuing_Date=dates[1]
                            else:
                                pass
                        try:
                            Dob=dates[0]
                        except:
                            Dob=''
                        try:
                            Expiry_date=dates[-1] if len(dates)<4 else dates[-2]
                        except:
                            Expiry_date=''
                        try:
                            Issuing_Date=dates[1]
                        except:
                            Issuing_Date=''
                        try:
                            Full_name=' '.join([ele for ele in id_infos[:id_infos.index([ele for ele in id_infos if Dob in ele][0])] if re.sub(r'\W+', ' ', ele).strip() not in ['DRIVING LICENCE', 'UK','DRIVING','LICENCE']])
                        except:
                            Full_name=''
                        #Address=''.join([ ele for ele in id_infos[id_infos.index([ele for ele in id_infos if Expiry_date in ele][0]):][pd.Series([ len(ele) for ele in id_infos[id_infos.index([ele for ele in id_infos if Expiry_date in ele][0]):]]).idxmax():] if '/' not in ele])
                        #Driver_number=[ele for ele in id_infos if (ele.startswith(Full_name[:3]) and bool(re.search(r'\d', ele)))][0]
                        try:
                            Driver_number=max([element for element in [ele for ele in id_infos if ((Full_name[:3] in ele) and bool(re.search(r'\d', ele)))][0].split(' ') ], key=len)
                        except:
                            Driver_number=''
                        try:
                            dob_index=id_infos.index([ele for ele in id_infos if Dob in ele][0])
                        except:
                            dob_index=''
                        try:
                            issuing_date_index=id_infos.index([ele for ele in id_infos if Issuing_Date in ele][0])
                            Place_of_birth=max(id_infos[dob_index:issuing_date_index],key=len)
                            pattern = r'[0-9]'
                            #Match all digits in the string and replace them with an empty string
                            Place_of_birth = re.sub(pattern, '', Place_of_birth)
                            Place_of_birth=re.sub(r'\W+', ' ', Place_of_birth).strip()
                        except:
                            Place_of_birth=''
                        #Place_of_birth=id_infos[dob_index:issuing_date_index][-1] if len(id_infos[dob_index:issuing_date_index][-1])>1 else id_infos[dob_index:issuing_date_index][-1].split(' ')[-1]

                        try:
                            driver_number_index=id_infos.index([ele for ele in id_infos if Driver_number in ele][0])
                            Dob_index=id_infos.index([ele for ele in id_infos if Dob in ele][0])
                            Place_of_birth_index=id_infos.index([ele for ele in id_infos if Place_of_birth in ele][0])
                            Issuing_Date_index=id_infos.index([ele for ele in id_infos if Issuing_Date in ele][0])
                            #Expiry_date_index=id_infos.index([ele for ele in id_infos if Expiry_date in ele][0])
                            indices=[Issuing_Date_index,Place_of_birth_index,Dob_index,driver_number_index]
                            id_infos=[i for j, i in enumerate(id_infos) if j not in indices]
                            id_infos=[ele for ele in id_infos if '/' not in ele]
                            #Address=''.join([ ele for ele in id_infos[id_infos.index([ele for ele in id_infos if Expiry_date in ele][0]):][pd.Series([ len(ele) for ele in id_infos[id_infos.index([ele for ele in id_infos if Expiry_date in ele][0]):]]).idxmax():] if '/' not in ele])
                            Address=' '.join(id_infos[id_infos.index(max(id_infos,key=len)):])
                        except:
                            id_infos=self.get_ocr_results(front_id)
                            Address=''.join([ ele for ele in id_infos[id_infos.index([ele for ele in id_infos if Expiry_date in ele][0]):][pd.Series([ len(ele) for ele in id_infos[id_infos.index([ele for ele in id_infos if Expiry_date in ele][0]):]]).idxmax():] if '/' not in ele])
                        Document_type='DRIVING LICENCE'

                        df={
                            #'last_label':last_label,
                            'Document_type':Document_type,
                            'Full_name':Full_name,
                            'Dob':Dob,
                            'Place_of_birth':Place_of_birth,
                            'Issuing_Date':Issuing_Date,
                            'Expiry_date':Expiry_date,
                            'Driver_number':Driver_number,
                            'Address':Address,
                            'similarity':similarity
                        }



        elif country=='UAE':

                        try:
                            id_number=[ele for ele in id_infos if ('ilare' in ele.lower()) or ('idare' in ele.lower())][0][15:]
                        except:
                            id_number=''

                        try:
                            card_number=[element for element in id_infos if element.isdigit() and len(element) == 9][0]
                        except:
                            card_number=''

                        date_pattern = r'\d{2}/\d{2}/\d{4}'

                        # Extract all dates from id_infos
                        dates = [match for element in id_infos for match in re.findall(date_pattern, element)]

                        dob = ''
                        expiry_date = ''

                        if len(dates) > 1:
                            dob = min(dates)
                            expiry_date = max(dates)
                        elif dates:  # If there is at least one date in the list
                            first_date = datetime.strptime(dates[0], '%d/%m/%Y')
                            if (datetime.today() - first_date).days / 365.25 > 5:
                                dob = dates[0]
                            else:
                                expiry_date = dates[0]

                        try:
                            Name=re.sub('<+', ' ', [element for element in id_infos if re.match(r'^(?=.*[A-Z])(?=.*<)(?!\d).*$', element)][0]).strip()
                        except:
                            Name=''

                        try:
                            gender=[element for element in id_infos if  re.match(r'^(?=.*[a-zA-Z0-9])(?=.*<).*$', element)and '<' in element and re.search(r'[a-zA-Z]', element) and re.search(r'[0-9]', element)][0][7]
                        except:
                            gender=''

                        try:
                            Occupation= re.sub(r'\W+', ' ', ' '.join([ele for ele in id_infos if 'occupation' in ele.lower()][0].split(' ')[1:]))
                        except:
                            Occupation=''

                        try:
                            Issuing_Place=[ele for ele in id_infos if 'Issuing Place' in ele][0].split(' ')[-1]
                        except:
                            Issuing_Place=''

                        try:
                            Employer= re.sub(r'\W+', ' ', ' '.join([ele for ele in id_infos if 'employer' in ele.lower()][0].split(' ')[1:]))
                        except:
                            Employer=''

                        try:
                            nationality=re.findall(r'\d+([a-zA-Z]+)[<\s]',[element for element in id_infos if  re.match(r'^(?=.*[a-zA-Z0-9])(?=.*<).*$', element)and '<' in element and re.search(r'[a-zA-Z]', element) and re.search(r'[0-9]', element)][0])[0]
                        except:
                            nationality=''
                            
                        if dob=='':
                            try:
                                dob= [element for element in id_infos if  re.match(r'^(?=.*[a-zA-Z0-9])(?=.*<).*$', element)and '<' in element and re.search(r'[a-zA-Z]', element) and re.search(r'[0-9]', element)][0][:6]
                                dob= f"{dob[4:6]}/{dob[2:4]}/19{dob[0:2]}"
                            except:
                                pass
                        else:
                            pass

                        df={
                            #'last_label':last_label,
                            'card_number':card_number,
                            'Name':Name,
                            'id_number':id_number,
                            'dob':dob,
                            'expiry_date':expiry_date,
                            'gender':gender,
                            'nationality':nationality,
                            'Occupation':Occupation,
                            'Employer':Employer,
                            'Issuing_Place':Issuing_Place,
                            'similarity':similarity
                        }


        else:
            pass
        
        #json_object = json.dumps(df, indent = 4) 
        return df
       
# if __name__ == '__main__':
#     front_id = sys.argv[1]
#     selfie = sys.argv[2]
#     country = 'UAE'
#     extract_ocr_info(front_id, selfie, country)
