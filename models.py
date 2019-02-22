import numpy
import cv2
import datetime
import math

from collections import deque

class Object:

    MAX_STATE_NUMB = 4
    # dU - changes of Speed
    # dA - changes of Acceleration
    # vec - vector of move
    # dHW - changes of Height/Width
    # tracker - tracker of current object
    
    def __init__(self, id, frame, bbox, confidence):
        self.id = id
        self.states = deque([], self.MAX_STATE_NUMB)
        self.addState(bbox)
        self.confidence = confidence
        # creating tracker
        # self.tracker = cv2.TrackerKCF_create()
        self.tracker = cv2.TrackerCSRT_create()
        self.tracker.init(frame, bbox)

    def getParam(self):
        return (self.id, self.getLastBox(), self.confidence)

    def getLastBox(self):
        return self.states[len(self.states) - 1]

    def _getCenter(self, box):
        (x, y, w, h) = box
        center_x = x + w / 2
        center_y = y + h / 2
        return [center_x, center_y]

    def _getWidthAndHeight(self, box):
        (x, y, w, h) = box
        return (w, h)

    def updateTracker(self, frame, withSafeState):
        (success, box) = self.tracker.update(frame)
        if success == True and withSafeState:
            self.addState(box)
        return (success, box, self.id, self.confidence)

    def reinitTracker(self, frame, bbox):
        self.tracker.init(frame, bbox)
        self.tracker.update(frame)

    def addState(self, bbox):
        self.states.append(bbox)
        if (len(self.states) == self.MAX_STATE_NUMB):
            self.calculation(self.states)
            for i in range(0, len(self.states) -1):
                self.states.popleft()

    def _calcLength(self, centerA, centerB):
        (x1, y1) = centerA
        (x2, y2) = centerB
        return math.sqrt((x2 -x1)**2 + (y2 - y1)**2)

    def _calcAngle(self, centerA, centerB):
        (x1, y1) = centerA
        (x2, y2) = centerB
        return (y2 - y1) / math.sqrt((x2 -x1)**2 + (y2 - y1)**2)
        
    def calculation(self, states):
        dU = self._calcdU(states)

    def _calcdU(self, states):
        changesdU = []
        changesAngle = []
        changesHW = []
        for i in range(0, len(states) - 1):
            changesdU.append(self._calcLength(self._getCenter(states[i]), self._getCenter(states[i + 1])))
            changesAngle.append(self._calcAngle(self._getCenter(states[i]), self._getCenter(states[i + 1])))
        print(self.id, changesdU)
        print(changesAngle)
    # def _calcdA(self):
    # def _calcdHW(self):
    
class ObjectManager:

    # min values of x and y when new detection is currently exist in objects
    MIN_DELTA_X = 15
    MIN_DELTA_Y = 15

    def __init__(self):
        # init start of IDs
        self.emptyID = 0
        self.listOfObject = []
        self.lastCalulationTime = None
    
    def getList(self):
        return self.listOfObject

    def update(self, frame, withSafeState):
        boxes = []
        for obj in self.listOfObject:
            boxes.append(obj.updateTracker(frame, withSafeState))
        return boxes

    def _getFreeId(self):
        id = self.emptyID
        self.emptyID += 1
        return id

    def _createListOfObject(self, frame, boxes, confidences, indices):
        listobj = []
        for i in indices:
            obj = Object(self._getFreeId(), frame, boxes[i[0]], confidences[i[0]])
            listobj.append(obj)
        return listobj

    def _getCenter(self, box):
        (x, y, w, h) = box
        center_x = x + w / 2
        center_y = y + h / 2
        return [center_x, center_y]

    def _isExistDetection(self, detbox, objbox):
        (xd, yd) = self._getCenter(detbox)
        (xo, yo) = self._getCenter(objbox)
        if abs(xo - xd) < self.MIN_DELTA_X:
            return True
        if abs(yo - yd) < self.MIN_DELTA_Y:
            return True
        return False 

    def setNewDetection(self, frame, boxes, confidences, indices):
        if len(self.listOfObject) == 0:
            for i in indices:
                newobj = Object(self._getFreeId(), frame, boxes[i[0]], confidences[i[0]])
                self.listOfObject.append(newobj)
        else:
            newlist = []
            for i in indices:
                # print(len(indices))
                # print(len(self.listOfObject))
                detbox = boxes[i[0]]
                NotExistInEvery = True
                for obj in self.listOfObject:
                    objbox = obj.getLastBox()
                    if self._isExistDetection(detbox, objbox):
                        obj.reinitTracker(frame, detbox)
                        NotExistInEvery = False
                        break
                
                if NotExistInEvery:
                    newobj = Object(self._getFreeId(), frame, boxes[i[0]], confidences[i[0]])
                    newlist.append(newobj)
            print("NEW LIST:", len(newlist))
            self.listOfObject.extend(newlist)