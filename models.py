import numpy

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
        self.tracker = cv2.TrackerKCF_create()
        self.tracker.init(frame, box)
    
    # creating Tracker
    def createTracker(self):
        self tracker = cv2.TrackerKCF_create()

    def _getCenter(self, box):
        (x, y, w, h) = box
        center_x = x + w / 2
        center_y = y + h / 2
        return [center_x, center_y]

    def updateTracker(self, frame):
        self.tracker.update(frame)
    def _calcdU(self):
    
    def _calcdA(self):

    def _calcdHW(self):
    


class ObjectManager:

    def __init__(self):
        self.listOfObject = 

    def _createListOfObject(self, boxes, confidences, frame)