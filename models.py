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
        self.tracker = cv2.TrackerKCF_create()
        self.tracker.init(frame, bbox)
    
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
        return (success, box, self.id, self.confidence)
    # def _calcdU(self):
    
    # def _calcdA(self):

    # def _calcdHW(self):
    


class ObjectManager:

    def __init__(self, frame, boxes, confidences, indices):
        # init start of IDs
        self.emptyID = 0
        self.listOfObject = self._createListOfObject(frame, boxes, confidences, indices)
    
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
