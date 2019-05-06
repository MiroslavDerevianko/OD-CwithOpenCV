import numpy as np
import cv2
import datetime
import math

from collections import deque

class Object:
    MAX_STATE_NUMB = 4
    MIN_CHANGE_DU = 3 # small changes we dont have detect as danger
    MAX_TIMES_CHANGE_DU = 2 # times changes speed
    MIN_DIS_VALUE = 3 # minimal values of dispercy
    MAX_TIMES_CHANGE_DIS = 2 # times changes dispercy
    # previous state of  X and Y
    prevX = None
    prevY = None
    # middle changes X and Y
    dXm = None
    dYm = None
    # dispercy Dx and Dy
    disDx = None
    disDy = None
    bbox = None
    dangerSpeed = False
    dangerAccuracy = False
    # dU - changes of Speed
    # dA - changes of Acceleration
    # vec - vector of move
    # dHW - changes of Height/Width
    # tracker - tracker of current object
    
    def __init__(self, id, frame, bbox, confidence):
        self.id = id
        # self.states = deque([], self.MAX_STATE_NUMB)
        # self.addState(bbox)
        self.confidence = confidence
        self.bbox = bbox
        # creating tracker
        # self.tracker = cv2.TrackerCSRT_create()
        self.tracker = cv2.TrackerCSRT_create()
        self.tracker.init(frame, bbox)

    def getId(self):
        return self.id

    def getParam(self):
        return (self.id, self.getLastBox(), self.confidence)
    
    def getBbox(self):
        return self.bbox

    def setBbox(self, bbox):
        self.bbox = bbox

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
        if success == True:
            # self.addState(box)
            self.bbox = box
            self.calculation(box, withSafeState)
        else:
            print("FALSE", box)
        return (success, box, self.id, self.isDanger())
    def reinitTracker(self, frame, bbox):
        self.tracker = cv2.TrackerCSRT_create()
        self.tracker.init(frame, bbox)
        # self._clearStates()
        # self.addState(bbox)
        # self._clearParams(bbox)
        self.updateTracker(frame, True)

    # def _clearStates(self):
    #     self.states.clear()

    def _clearParams(self, bbox):
        (x, y) = self._getCenter(bbox)
        self.prevX = x
        self.prevY = y
        self.dXm = None
        self.dYm = None
        self.disDx = None
        self.disDy = None
    # def addState(self, bbox):
    #     self.states.append(bbox)
    #     if (len(self.states) == self.MAX_STATE_NUMB):
    #         for i in range(0, len(self.states) -1):
    #             self.states.popleft()

    def calculation(self, bbox, withSafeState):
        self._calcDXY(bbox, withSafeState)

    def _calcDXY(self, bbox, withSafeState):
        # if withSafeState:
            (x, y) = self._getCenter(bbox)
            if self.prevX != None and self.prevY != None:
                if self.dXm != None and self.dYm != None:
                    oldDx = self.dXm
                    oldDy = self.dYm
                    currDx = abs(x - self.prevX)
                    currDy = abs(y - self.prevY)
                    if (abs(currDx) > self.MIN_CHANGE_DU and abs(oldDx) > self.MIN_CHANGE_DU) and (abs(currDy) > self.MIN_CHANGE_DU and abs(oldDy) > self.MIN_CHANGE_DU):
                        if abs(currDx) > self.MAX_TIMES_CHANGE_DU * abs(oldDx) or abs(currDy) > self.MAX_TIMES_CHANGE_DU * abs(oldDy):
                            self.dangerSpeed = True
                            print("Speed", self.id)
                            print(currDx, oldDx)
                            print(currDy, oldDy)
                    else:
                        self.dangerSpeed = False
                    
                    self.dXm = (currDx + oldDx) / 2
                    self.dYm = (currDy + oldDy) / 2
                    # self._calcDis(abs(currDx - self.dXm), abs(currDy - self.dYm))
                    self._calcDis(currDx, currDy)
                    self.prevX = x
                    self.prevY = y
                else:
                    self.dXm = abs(x - self.prevX)
                    self.dYm = abs(y - self.prevY)

            else:
                self.prevX = x
                self.prevY = y

    def _calcDis(self, disX, disY):
        if self.disDx != None and self.disDy != None:
            # newdisDx = (disX + self.disDx) / 2
            # newdisDy = (disY + self.disDy) / 2
            newdisDx = math.sqrt( disX**2 + self.dXm**2 )
            newdisDy = math.sqrt( disY**2 + self.dYm**2 )

            if abs(disX) > self.MIN_DIS_VALUE and abs(self.disDx) > self.MIN_DIS_VALUE and abs(disY) > self.MIN_DIS_VALUE and abs(self.disDy) > self.MIN_DIS_VALUE:
                if  abs(disX) > self.MAX_TIMES_CHANGE_DIS * abs(self.disDx) or abs(disY) > self.MAX_TIMES_CHANGE_DIS * abs(self.disDy):
                    self.dangerAccuracy = True
                    print("Accuracy", self.id)
                    print(disX, self.disDx)
                    print(disY, self.disDy)
            else:
                self.dangerAccuracy = False
            self.disDx = newdisDx
            self.disDy = newdisDy
        else:
            self.disDx = disX
            self.disDy = disY
    
    def isDanger(self):
        return self.dangerSpeed or self.dangerAccuracy
    
    def setThesholdSettings(self, minDU, maxDU, minDis, maxDis):
        self.MIN_CHANGE_DU = minDU
        self.MAX_TIMES_CHANGE_DU = maxDU
        self.MIN_CHANGE_DU = minDis
        self.MAX_TIMES_CHANGE_DIS = maxDis

class ObjectManager:

    # min values of x and y when new detection is currently exist in objects
    MIN_DELTA_X = 35 # percent of min change on X center
    MIN_DELTA_Y = 35 # percent of min changes on Y center
    thresholds = [3, 2, 3, 2] # default threshhold [ minDU, maxDU, minDis, maxDis ]

    def __init__(self):
        self.clear()
    
    def clear(self):
        self.emptyID = 0
        self.listOfObject = []

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

    def deleteObjById(self, id):
        print('delete')
        for i in range(0, len(self.listOfObject)):
            if (self.listOfObject[i].getId() == id):
                del self.listOfObject[i]
                break

    def updateThesholds(self):
        for obj in self.listOfObject:
            obj.setThesholdSettings(*self.thresholds)

    def setThesholdSettings(self, minDU, maxDU, minDis, maxDis):
        self.thresholds = [minDU, maxDU, minDis, maxDis]
        self.updateThesholds()

    def getThresholds(self):
        return self.thresholds

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
    
    def _getWidthAndHeight(self, box):
        (x, y, w, h) = box
        return (w, h)

    def _isExistDetection(self, detbox, objbox):
        (xd, yd) = self._getCenter(detbox)
        (xo, yo) = self._getCenter(objbox)
        # (wo, ho) = self._getWidthAndHeight(objbox)
        if abs(xo - xd) < self.MIN_DELTA_X  and abs(yo - yd) < self.MIN_DELTA_Y :
            return True
        return False 

    def _calcS(self, detbox, objbox):
        (xd, yd, wd, hd) = detbox
        (xo, yo, wo, ho) = objbox
        x1 = max(xd,xo)
        y1 = max(yd,yo)
        x2 = min(xd+wd, xo+wo)
        y2 = min(yd+hd, yo+ho)
        if x2-x1 < 0:
            return 0
        if y2-y1 < 0:
            return 0
        return (x2-x1) * (y2-y1)

    def setNewDetection(self, frame, boxes, confidences, indices):
        if len(self.listOfObject) == 0:
            for i in indices:
                newobj = Object(self._getFreeId(), frame, boxes[i[0]], confidences[i[0]])
                newobj.setThesholdSettings(*self.thresholds)
                self.listOfObject.append(newobj)
        else:
            newlist = []
            deletelist = []
            usedindices = [0] * len(indices)
            for obj in self.listOfObject:
                objbox = obj.getBbox()
                maxS = 0
                indiceId = 0
                for i in range(0, len(indices)):
                    detbox = boxes[indices[i][0]]
                    newS = self._calcS(detbox, objbox)
                    if newS > maxS and usedindices[i] == 0:
                        maxS = newS
                        indiceId = i
                if maxS > 0:
                    obj.reinitTracker(frame, boxes[indices[indiceId][0]])
                    usedindices[indiceId] += 1
            for i in range(0, len(usedindices)):
                if usedindices[i] == 0:
                    newobj = Object(self._getFreeId(), frame, boxes[indices[i][0]], confidences[indices[i][0]])
                    newlist.append(newobj)
            for i in deletelist:
                self.deleteObjById(i)
            # for i in indices:
            #     # print(len(indices))
            #     # print(len(self.listOfObject))
            #     detbox = boxes[i[0]]
            #     NotExistInEvery = True
            #     maxS = 0
            #     maxId = None
            #     for obj in self.listOfObject:
            #         objbox = obj.getBbox()
            #         newS = self._calcS(detbox, objbox)
            #         if newS > maxS:
            #             maxId = obj.id
            #             maxS = newS
            #         # if self._isExistDetection(detbox, objbox):
            #         #     obj.reinitTracker(frame, detbox)
            #         #     NotExistInEvery = False
            #         #     # print(obj.getId())
            #         #     break
            #     if maxS > 0:
            #         NotExistInEvery = False
            #         obj = list(filter(lambda x: x.id == maxId, self.listOfObject))[0]
            #         obj.reinitTracker(frame, detbox)
                
            #     if NotExistInEvery:
            #         newobj = Object(self._getFreeId(), frame, boxes[i[0]], confidences[i[0]])
            #         newlist.append(newobj)
            print("NEW LIST:", len(newlist))
            self.listOfObject.extend(newlist)