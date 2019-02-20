import numpy
import cv2

class Object:

    # dU - changes of Speed
    # dA - changes of Acceleration
    # vec - vector of move
    # dHW - changes of Height/Width
    # tracker - tracker of current object
    
    def __init__(self, id, frame, bbox, confidence):
        self.id = id
        self.states = []
        self.states.append(bbox)
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

    def updateTracker(self, frame):
        (success, box) = self.tracker.update(frame)
        if success == True:
            self.states.append(box)
        else:
            print("Object Lost")
        return (success, box, self.id, self.confidence)

    def reinitTracker(self, frame, bbox):
        self.tracker.init(frame, bbox)
        self.tracker.update(frame)

    # def _calcdU(self):
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
    
    def getList(self):
        return self.listOfObject

    def update(self, frame):
        boxes = []
        for obj in self.listOfObject:
            boxes.append(obj.updateTracker(frame))
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


        

