import cv2
import argparse
import numpy as np

import time
import imutils
from imutils.video import VideoStream

import datetime

from models import Object 
from models import ObjectManager 

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', help = 'path to input image')
ap.add_argument('-v', '--video', help= 'path to input video')
ap.add_argument('-wc', '--webcam', type=bool, help="use a webcam")
ap.add_argument('-c', '--config', required=True, help = 'path to yolo config file')
ap.add_argument('-w', '--weights', required=True, help = 'path to yolo pre-trained weights')
ap.add_argument('-cl', '--classes', required=True, help = 'path to text file containing class names')
ap.add_argument("-conf", "--confidence", type=float, default=0.5, help="minimum probability to filter weak detections")
args = ap.parse_args()


def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, str(class_id), (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

classes = None

with open(args.classes, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

net = cv2.dnn.readNet(args.weights, args.config)

# print("[INFO] starting video stream, please wait...")
# vs = VideoStream(src=0).start()
# time.sleep(3)

class_ids = []
confidences = []
boxes = []
conf_threshold = 0.5
nms_threshold = 0.4

# scale = 0.00292
scale = 0.0012
Width = 800
Height = 600
count = 0

# create a multitracker to object tracking
multiTracker = None

# create ObjectManager
om = ObjectManager()

vs = None
frame = None

if args.video != None: 
    vs = cv2.VideoCapture(args.video)
if args.webcam == True:
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(3)

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 1000 pixels
    if vs != None: 
        frame = vs.read()
        frame = frame[1] if args.video else frame
        
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
    # blob = cv2.dnn.blobFromImage(cv2.resize(frame, (416, 416)), 0.5, (416, 416), (103.93, 116.77, 123.68))
    blob = cv2.dnn.blobFromImage(frame, scale, (416,416), (0,0,0), True, crop=False)
    if count > 15:
        count = 0
    if count == 0:
        # multiTracker = cv2.MultiTracker_create()
        boxes = []
        confidences = []
        # pass the blob through the network and obtain the detections and predictions
        net.setInput(blob)
        start = datetime.datetime.now()
        outs = net.forward(get_output_layers(net))
        end = datetime.datetime.now()
        print(end-start)
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > conf_threshold:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    # draw_prediction(frame, class_id, confidence, round(x), round(y), round(x+w), round(y+h))
                    box = (x, y, w, h)
                    # tracker = cv2.TrackerKCF_create()
                    # multiTracker.add(tracker, frame, box)
                    boxes.append(box)
                    # class_ids.append(class_id)
                    confidences.append(float(confidence))
                    # boxes.append([x, y, w, h])
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        om.setNewDetection(frame, boxes, confidences, indices)
    
        # for i in indices:
        #     box = boxes[i[0]]
        #     (x, y, w, h) = box
        #     confidence = confidences[i[0]]
        #     draw_prediction(frame, class_id, confidence, round(x), round(y), round(x+w), round(y+h))
        #     tracker = cv2.TrackerKCF_create()
        #     multiTracker.add(tracker, frame, box)
    else:
        # (success, boxes) = multiTracker.update(frame)
        # for bb in enumerate(boxes):
        #     (success, box) = bb
        #     (x, y, w, h) = box
        #     draw_prediction(frame, 0, 1, int(round(x)), int(round(y)), int(round(x+w)), int(round(y+h)))
        withSafeState = True if count == 4 or count == 8 or count == 12 or count == 15 else False
        objboxes = om.update(frame, withSafeState)
        # print(objboxes)
        for (success, box, id, confidence) in objboxes:
            # print(success, box)
            (x, y, w, h) = box
            draw_prediction(frame, id, confidence, int(round(x)), int(round(y)), int(round(x+w)), int(round(y+h)))
    # show the output frame
    cv2.imshow("Object detector", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, break from the loop
    if key == ord("q"):
        break
    count += 1
    # print(count)

# cleanup and closing frame
cv2.destroyAllWindows()
vs.stop()

# image = cv2.imread(args.image)

# Width = image.shape[1]
# Height = image.shape[0]
# scale = 0.00392

# blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

# net.setInput(blob)

# outs = net.forward(get_output_layers(net))

# class_ids = []
# confidences = []
# boxes = []
# conf_threshold = 0.5
# nms_threshold = 0.4


# for out in outs:
#     for detection in out:
#         scores = detection[5:]
#         class_id = np.argmax(scores)
#         confidence = scores[class_id]
#         if confidence > 0.5:
#             center_x = int(detection[0] * Width)
#             center_y = int(detection[1] * Height)
#             w = int(detection[2] * Width)
#             h = int(detection[3] * Height)
#             x = center_x - w / 2
#             y = center_y - h / 2
#             class_ids.append(class_id)
#             confidences.append(float(confidence))
#             boxes.append([x, y, w, h])


# indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

# for i in indices:
#     i = i[0]
#     box = boxes[i]
#     x = box[0]
#     y = box[1]
#     w = box[2]
#     h = box[3]
#     draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

# cv2.imshow("object detection", image)
# cv2.waitKey()
    
# cv2.imwrite("object-detection.jpg", image)
# cv2.destroyAllWindows()