import cv2
import numpy as np

import time
import imutils
from imutils.video import VideoStream

import datetime

from models import Object 
from models import ObjectManager 

class Detector:

    sourceType = None
    currVideoPath = None
    currCamera = None

    weightPath = None
    configPath = None
    classesPath = None

    COLORS = np.random.uniform(0, 255, size=(255, 3))

    net = None

    scale = 0.0012
    Width = 800
    Height = 600
    count = 0

    om = None # ObjectManager

    vs = None # video stream

    def __init__(self):
        om = ObjectManager()

    def setSourceType(self, source):
        self.sourceType = source

    def getSourceType(self):
        return self.sourceType

    def setVideoPath(self, path):
        self.currVideoPath = path

    def getVideoPath(self):
        return self.sourceType

    def setCamera(self, camera):
        self.currCamera = camera
    
    def getCamera(self):
        return self.currCamera

    def _setVideoStream(self):
        if self.getSourceType() == 'video':
            self.vs = cv2.VideoCapture(self.getVideoPath())
        else if self.getSourceType() == 'camera':
            self.vs = VideoStream(src=self.getCamera()).start()
            time.sleep(3)
        else:
            raise Exception('Not support source type')
    
    def setSize(self, width, height):
        self.Width = width
        self.Height = height

    def setNetWeights(self, weights):
        self.weights = weights
    
    def setNetConfig(self, config):
        self.config = config
    
    def setScale(self, scale):
        self.scale = scale

    def _initNet(self):
        self.net = cv2.dnn.readNet(self.weights, self.config)
    
    def _getFrame(self):
        frame = None
        if self.vs != None: 
            frame = vs.read()
            frame = frame[1] if self.getSourceType() == "video" else frame
        else:
            raise Exception("No frame")
        Width = frame.shape[1]
        Height = frame.shape[0]
        frame = imutils.resize(frame, width=Width, height=Height)
        return frame
        
    if args.image != None:
        frame = cv2.imread(args.image)
    
    if frame is None:
        print('No frame')
        break
    Width = frame.shape[1]
    Height = frame.shape[0]
    frame = imutils.resize(frame, width=Width, height=Height)
    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]

    def start(self):


    def _getOutputLayers(self, net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers
    
    def _drawPrediction(img, class_id, danger, x, y, x_plus_w, y_plus_h):
        label = str(classes[class_id])
        color = COLORS[class_id]
        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
        text = str(class_id)
        text += " danger" if (danger) else ""
        cv2.putText(img, text, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
