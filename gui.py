from tkinter import *
from tkinter import filedialog
import cv2

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

print(getAllCams())

class GUI:
    sourceTypes = ["camera", "video"]
    currSourceType = None
    currFilePath = None
    currCamera = None

    def __init__(self):
        # init root frame
        self.root = Tk()
        self._initRoot()
        # set default variables
        self.currSourceType = StringVar()
        self.currSourceType.set("camera")
        self.currCamera = StringVar()
        self.currCamera.set("No camera")
        # init child frame
        self._update()
        # self._initLeftFrame()
        # self._initRightFrame()

    def _update(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self._initLeftFrame()
        self._initRightFrame()

    def start(self):
        self.root.mainloop()
    
    def _initRoot(self):
        self.root.title("Object detection")
        self.root.geometry("500x500")

    def _initLeftFrame(self):
        leftFrame = Frame(self.root)
        leftFrame.pack(side=LEFT)
        self._initChooseSource(leftFrame)
        self._initInputSource(leftFrame)
    
    def _initInputSource(self, frame):
        if (self._getSource() == "camera"):
            self._initChooseCamera(frame)
        if (self._getSource() == "video"):
            self._initOpenFile(frame)

    def _chooseSource(self):
        self.statusLabel.config(text=self._getSource())
        self._update()

    def _getSource(self):
        return self.currSourceType.get()
    
    def _initChooseSource(self, frame):
        label = Label(frame, text="Choose source type")
        option = OptionMenu(frame, self.currSourceType, *self.sourceTypes)
        button = Button(frame, text="Choose", command=self._chooseSource)
        label.pack()
        option.pack()
        button.pack()

    def _setVideoPath(self, path):
        self.currFilePath = path

    def _getVideoPath(self, path):
        return self.currFilePath
    
    def _openVideo(self):
        path = filedialog.askopenfilename(initialdir = "/",title = "Select video")
        print(path)

    def _initOpenFile(self, frame):
        open = Button(frame, text="Open video", command=self._openVideo)
        open.pack()

    def _getCamera(self):
        return self.currCamera.get()

    def _chooseCamera(self):
        self.cameraLabel.config(text=self._getCamera())

    def _initChooseCamera(self, frame):
        cameras = getAllCams()
        if not cameras:
            label = Label(frame, text="Not found cameras")
            label.pack()
        else:
            label = Label(frame, text="Choose camera")
            option = OptionMenu(frame, self.currCamera, *cameras)
            button = Button(frame, text="Choose", command=self._chooseCamera)
            label.pack()
            option.pack()
            button.pack()
        
        

    def _initRightFrame(self):
        rightFrame = Frame(self.root)
        rightFrame.pack(side=RIGHT)
        self.statusLabel = Label(rightFrame, text=self._getSource())
        self.statusLabel.pack()
        self.cameraLabel = Label(rightFrame, text=self._getCamera())
        self.cameraLabel.pack()

    def _showError(self, error):
        tkMessageBox.showerror("Error", error)


gui = GUI()
gui.start()




