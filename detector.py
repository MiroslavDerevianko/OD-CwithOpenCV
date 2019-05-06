import cv2
import numpy as np
import sys

import time
import imutils
from imutils.video import VideoStream
from threading import Thread
import datetime

from models import Object 
from models import ObjectManager 



class Detector:

    sourceType = None
    currVideoPath = None
    currCamera = None

    weightPath = None
    configPath = None

    COLORS = np.random.uniform(0, 255, size=(255, 3))

    net = None

    scale = 0.0012
    conf_threshold = 0.5
    nms_threshold = 0.4
    Width = 1024
    Height = 800
    UPDATECOUNT = 10

    om = None # ObjectManager

    vs = None # video stream
    thread = None # Detector Thread
    isRunning = False

    def __init__(self):
        print("Detecor created")
        self.om = ObjectManager()

    def setTreshholdsSettings(self, minDU, maxDU, minDis, maxDis):
        self.om.setThesholdSettings(minDU, maxDU, minDis, maxDis)

    def getThresholds(self):
        return self.om.getThresholds()

    def setSourceType(self, source):
        self.sourceType = source

    def getSourceType(self):
        return self.sourceType

    def setVideoPath(self, path):
        self.currVideoPath = path

    def getVideoPath(self):
        return self.currVideoPath

    def setCamera(self, camera):
        self.currCamera = camera
    
    def getCamera(self):
        return self.currCamera

    def _setVideoStream(self):
        if self.getSourceType() == 'video':
            self.vs = cv2.VideoCapture(self.getVideoPath())
        else: 
            if self.getSourceType() == 'camera':
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
            frame = self.vs.read()
            frame = frame[1] if self.getSourceType() == "video" else frame
        else:
            raise Exception("No frame")
        # width = frame.shape[1]
        # height = frame.shape[0]
        frame = imutils.resize(frame, width=self.Width, height=self.Height)
        return frame
    
    def start(self):
        if self.isRunning == False:
            self.om.clear()
            self.thread = Thread(target=self._startDetection)
            self.thread.start()
            

    def _startDetection(self):
        self._setVideoStream()
        self._initNet()
        count = 0
        self.isRunning = True
        while True:
            frame = None
            try:
                frame = self._getFrame()
            except:
                print("Error:", sys.exc_info()[0])
                self.close()
            (h, w) = frame.shape[:2]
            if count > self.UPDATECOUNT:
                count = 0
            if count == 0:
                # create blob
                blob = cv2.dnn.blobFromImage(frame, self.scale, (416,416), (0,0,0), True, crop=False)
                # set blob to input
                self.net.setInput(blob)
                # get outputs
                outs = self.net.forward(self._getOutputLayers(self.net))
                self._performOutput(outs, w, h, frame)
            else:
                withSafeState = True if count == 4 or count == 12 else False
                objboxes = self.om.update(frame, withSafeState)
                for (success, box, id, danger) in objboxes:
                    if success is not True:
                        self.om.deleteObjById(id)
                    else:
                        (x, y, w, h) = box
                        self._drawPrediction(frame, id, danger, int(round(x)), int(round(y)), int(round(x+w)), int(round(y+h)))
            # show the output frame
            cv2.imshow("Object detector", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the 'q' key is pressed, break from the loop
            if key == ord("q"):
                break
            count += 1
        self.close()
        print("thread stopped")
        self.isRunning = False
    
    def close(self):
        cv2.destroyAllWindows()
        # if (self.vs != None):
        #     self.vs.stop()

    def _performOutput(self, outs, width, height, frame):
        boxes = []
        confidences = []
        indices = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.conf_threshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    box = (x, y, w, h)
                    boxes.append(box)
                    confidences.append(float(confidence))

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        self.om.setNewDetection(frame, boxes, confidences, indices)

    def _getOutputLayers(self, net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers
    
    def _drawPrediction(self, img, id, danger, x, y, x_plus_w, y_plus_h):
        color = self.COLORS[id]
        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
        text = str(id)
        text += " danger" if (danger) else ""
        cv2.putText(img, text, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    @staticmethod
    def getAllCams():
        index = 0
        arr = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
            cap.release()
            index += 1
        return arr