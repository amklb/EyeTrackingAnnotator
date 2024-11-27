import numpy as np
import pandas as pd
import win32gui, win32ui, win32con
from PIL import Image
from time import sleep
import cv2 as cv
import os
import random
from datetime import datetime
import csv



# This code is taken from https://github.com/moises-dias/yolo-opencv-detector
class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name=None):
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

       
    
        # Get the window size
        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        self.w = right - left
        self.h = bottom - top
        
    

    def get_screenshot(self):
         # Get the window's device context
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        
        # Create a bitmap compatible with the device context
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
    
        # Copy the contents of the window into the bitmap
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (0, 0), win32con.SRCCOPY)
    
        # Extract bitmap bits as a byte array
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
    
        # Reshape the data into the right format (height, width, 4 channels)
        img.shape = (self.h, self.w, 4)
    
        # Clean up the DCs and bitmap object
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
    
        # Convert from BGRA to RGB by reordering the channels
        #img = img[..., [2, 1, 0]]  # Swap Blue and Red channels to get RGB
        img = img[...,:3]
        img = np.ascontiguousarray(img)

        return img

    def generate_image_dataset(self):
        if not os.path.exists("images"):
            os.mkdir("images")
        while(True):
            img = self.get_screenshot()
            im = Image.fromarray(img[..., [2, 1, 0]])
            im.save(f"./images/img_{len(os.listdir('images'))}.jpeg")
            sleep(0.08)
    def get_window_size(self):
        return (self.w, self.h)
    

class ImageProcessor:
    W = 0
    H = 0
    net = None
    ln = None
    classes = {}
    colors = []

    def __init__(self, img_size, cfg_file, weights_file):
        np.random.seed(42)
        self.net = cv.dnn.readNetFromDarknet(cfg_file, weights_file)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i-1] for i in self.net.getUnconnectedOutLayers()]
        self.W = img_size[0]
        self.H = img_size[1]
        
        with open('yolov4-tiny/obj.names', 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            self.classes[i] = line.strip()
        
        # If you plan to utilize more than six classes, please include additional colors in this list.
        self.colors = [
            (0, 0, 255), 
            (0, 255, 0), 
            (255, 0, 0), 
            (255, 255, 0), 
            (255, 0, 255), 
            (0, 255, 255)
        ]
        

    def proccess_image(self, img):

        blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.ln)
        outputs = np.vstack(outputs)
        
        coordinates = self.get_coordinates(outputs, 0.5)

        self.draw_identified_objects(img, coordinates)

        return coordinates

    def get_coordinates(self, outputs, conf):

        boxes = []
        confidences = []
        classIDs = []

        for output in outputs:
            scores = output[5:]
            
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > conf:
                x, y, w, h = output[:4] * np.array([self.W, self.H, self.W, self.H])
                p0 = int(x - w//2), int(y - h//2)
                boxes.append([*p0, int(w), int(h)])
                confidences.append(float(confidence))
                classIDs.append(classID)

        indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf-0.1)

        if len(indices) == 0:
            return []

        coordinates = []
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            coordinates.append({'x': x, 'y': y, 'w': w, 'h': h, 'class': classIDs[i], 'class_name': self.classes[classIDs[i]]})
        return coordinates

    def draw_identified_objects(self, img, coordinates):
        for coordinate in coordinates:
            x = coordinate['x']
            y = coordinate['y']
            w = coordinate['w']
            h = coordinate['h']
            classID = coordinate['class']
            
            color = self.colors[classID]
            
            cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv.putText(img, self.classes[classID], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv.imshow('window',  img)





# This code is modified by me for desired output
window_name = ""
cfg_file_name = r"C:\Users\agata\EyeTrackingAnnotator\yolov4-tiny\yolov4-tiny-custom.cfg"
weights_file_name = r"C:\Users\agata\EyeTrackingAnnotator\yolov4-tiny\yolov4-tiny-custom_last.weights"

wincap = WindowCapture()
improc = ImageProcessor(wincap.get_window_size(), cfg_file_name, weights_file_name)

start_date = int(datetime.now().timestamp() * 1000)
buffer_df = []
 
while(True):
    timestamp_millis = int(datetime.now().timestamp() * 1000) - start_date
    ss = wincap.get_screenshot()
        
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
    
    coordinates = improc.proccess_image(ss)

    if len(coordinates) > 0:    
        for i in range(len(coordinates)):
            coordinates[i]["time"] = timestamp_millis
            buffer_df.append(coordinates[i])
        
        
    sleep(0.02)
        
    
object_df = pd.DataFrame(buffer_df)
object_df.to_csv(r'C:\Users\agata\EyeTrackingAnnotator\data\data_obj.txt', sep='\t', index=False)
print('Finished.')