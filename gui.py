from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import cv2
from detector import Detector

class GUI:
    sourceTypes = ["camera", "video"]
    currSourceType = None
    currFilePath = None
    currCamera = None
    currWeightsPath = None
    currConfigPath = None

    buttonOpts = {"width":10, "padx":2, "pady":2}
    labelOpts = {"anchor":W, "width":20, "padx":2, "pady":2}

    isCreated = False
    isRunning = False
    detector = None



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

    def _update(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self._initLeftFrame()
        self._initRightFrame()

    def start(self):
        self.root.mainloop()
    
    def _initRoot(self):
        self.root.title("Object detection")
        self.root.geometry("800x400")

    def _setIsCreated(self, status):
        self.isCreated = status
        self._update()

    def _initLeftFrame(self):
        leftFrame = Frame(self.root)
        leftFrame.grid(row=0, column=0, sticky=N, padx=10, pady=10)
        labelSourceConfig = Label(leftFrame, text="Source configs").grid(row=0, column=0, columnspan=3, pady=10)
        self._initChooseSource(leftFrame)
        self._initInputSource(leftFrame)
        labelNetConfig = Label(leftFrame, text="Network configs").grid(row=3, column=0, columnspan=3, pady=10)
        self._initOpenWeights(leftFrame)
        self._initOpenConfig(leftFrame)
        self._initCreateBtn(leftFrame)
    
    def _initInputSource(self, frame):
        if (self._getSource() == "camera"):
            self._initChooseCamera(frame)
        if (self._getSource() == "video"):
            self._initOpenFile(frame)

    def _chooseSource(self):
        # self.statusLabel.config(text=self._getSource())
        self._update()

    def _getSource(self):
        return self.currSourceType.get()
    
    def _initChooseSource(self, frame):
        label = Label(frame, **self.labelOpts, text="Choose source type")
        option = OptionMenu(frame, self.currSourceType, *self.sourceTypes)
        button = Button(frame, **self.buttonOpts, text="Choose", command=self._chooseSource)
        label.grid(row=1, column=0, sticky=W, pady=10)
        option.grid(row=1, column=1)
        button.grid(row=1, column=2)

    def _setVideoPath(self, path):
        self.currFilePath = path

    def _getVideoPath(self):
        return self.currFilePath
    
    def _openVideo(self):
        path = filedialog.askopenfilename(initialdir = "/",title = "Select video",filetypes=(("Video file", "*.mp4"), ("all files","*.*")))
        self._setVideoPath(path)
        self._update()
        print(path)

    def _initOpenFile(self, frame):
        label = Label(frame, text=self._getVideoPath().split('/')[-1] if self._getVideoPath() else "Choosen file")
        open = Button(frame, **self.buttonOpts, text="Open video", command=self._openVideo)
        label.grid(row=2, column=0, columnspan=2, sticky=W, pady=10)
        open.grid(row=2, column=2)

    def _getCamera(self):
        return self.currCamera.get()

    def _chooseCamera(self):
        print(self._getCamera())

    def _initChooseCamera(self, frame):
        cameras = Detector.getAllCams()
        if not cameras:
            label = Label(frame, **self.labelOpts, text="Not found cameras")
            label.grid(row=2, column=0, sticky=W, pady=10)
        else:
            label = Label(frame, **self.labelOpts, text="Choose camera")
            option = OptionMenu(frame, self.currCamera, *cameras)
            button = Button(frame, **self.buttonOpts, text="Choose", command=self._chooseCamera)
            label.grid(row=2, column=0, sticky=W, pady=10)
            option.grid(row=2, column=1)
            button.grid(row=2, column=2)

    
    def _setWeightsPath(self, path):
        self.currWeightsPath = path

    def _getWeightsPath(self):
        return self.currWeightsPath
    
    def _openWeights(self):
        path = filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select weights file", filetypes=(("Weights file", "*.weights"), ("all files","*.*")))
        self._setWeightsPath(path)
        self._update()
        print(path)

    def _initOpenWeights(self, frame):
        label = Label(frame, text=self._getWeightsPath().split('/')[-1] if self._getWeightsPath() else "Choosen file")
        open = Button(frame, **self.buttonOpts, text="Open weights", command=self._openWeights)
        label.grid(row=4, column=0, columnspan=2, sticky=W, pady=10)
        open.grid(row=4, column=2)

    def _setConfigPath(self, path):
        self.currConfigPath = path

    def _getConfigPath(self):
        return self.currConfigPath
    
    def _openConfig(self):
        path = filedialog.askopenfilename(initialdir = os.getcwd(),title = "Select config file", filetypes=(("Config file", "*.cfg"), ("all files","*.*")))
        self._setConfigPath(path)
        self._update()
        print(path)

    def _initOpenConfig(self, frame):
        label = Label(frame,text=self._getConfigPath().split('/')[-1] if self._getConfigPath() else "Choosen file")
        open = Button(frame, **self.buttonOpts, text="Open config", command=self._openConfig)
        label.grid(row=5, column=0, columnspan=2, sticky=W, pady=10)
        open.grid(row=5, column=2)
        
    def _showError(self, error):
        messagebox.showerror("Error", error)

    def _showWarning(self, error):
        messagebox.showwarning("Warning", error)

    def _checkParams(self):
        if (self._getWeightsPath() is None):
            self._showWarning("Weights file not choosed")
            return False
        if (self._getConfigPath() is None):
            self._showWarning("Config file not choosed")
            return False
        if (self._getSource() is None):
            self._showWarning("Source not choosed")
            return False
        if (self._getSource() == "camera" and (self._getCamera() == 'No camera' or self._getCamera() == None)):
            self._showWarning("Source choosed like camera but not choose camera")
            return False
        if (self._getSource() == "video" and self._getVideoPath() == None):
            self._showWarning("Source choosed like video but not choose video path")
            return False
        return True

    def _createDetector(self):
        self.detector = Detector()
        if self._getSource() == "camera":
            self.detector.setSourceType(self._getSource())
            self.detector.setCamera(self._getCamera())
        if self._getSource() == 'video':
            self.detector.setSourceType(self._getSource())
            self.detector.setVideoPath(self._getVideoPath())
        self.detector.setNetWeights(self._getWeightsPath())
        self.detector.setNetConfig(self._getConfigPath())

    def _createInstance(self):
        status = self._checkParams()
        if status is True:
            self._createDetector()
            self._setIsCreated(True)

    def _initCreateBtn(self, frame):
        open = Button(frame, **self.buttonOpts, text="Create", command=self._createInstance)
        open.grid(row=6, column=0, columnspan=3)
    
    def _getStatus(self):
        if self.isCreated == True:
            return "created"
        else: return "not created"

    def _initRightFrame(self):
        rightFrame = Frame(self.root)
        rightFrame.grid(row=0, column=1, sticky=N, padx=10, pady=10)
        labelDetectorSettings = Label(rightFrame, text="Detector: Status "+self._getStatus()).grid(row=0, column=0, columnspan=3, pady=10)
        if self.isCreated == True:
            labelDetectorSettings = Label(rightFrame, text="Treshholds Settings").grid(row=1, column=0, columnspan=3, pady=10)
            self._initStartBtn(rightFrame)
            self._initTreshholdsSettings(rightFrame)
    
    def _startDetection(self):
        if self.detector.isRun() != True:
            self.isRunning = True
            self.detector.start()
            self._update()

    def _stopDetection(self):
        if self.detector.isRun() == True:
            self.isRunning = False
            self.detector.stop()
            self._update()

    def _initStartBtn(self, frame):
        open = None
        if self.isRunning != True:
            open = Button(frame, **self.buttonOpts, text="Start", command=self._startDetection)
        else:
            open = Button(frame, **self.buttonOpts, text="Stop", command=self._stopDetection)
        open.grid(row=7, column=2, columnspan=2)

    def _validateEntry(self, value):
        try: 
            int(value)
            return True
        except ValueError:
            self._showError("Field must be a number")
            return False
    
    def _changeThresholds(self):
        minDu = int(self.minDuEntry.get())
        maxDu = int(self.maxDuEntry.get())
        minDis = int(self.minDisEntry.get())
        maxDis = int(self.maxDisEntry.get())
        self.detector.setTreshholdsSettings(minDu, maxDu, minDis, maxDis)

    def _initTreshholdsSettings(self, frame):
        opts = {"anchor": W, "width": 30, "padx":5,"pady": 5 }
        vcmd = (frame.register(self._validateEntry), '%S')
        threshholds = self.detector.getThresholds()
        entryopts = { "validate": "key", "vcmd": vcmd}
        minDulabel = Label(frame, **opts, text="Min speed change threshhold").grid(row=2, column=0, columnspan=2)
        self.minDuEntry = Entry(frame, **entryopts )
        self.minDuEntry.insert(0, threshholds[0])
        self.minDuEntry.grid(row=2, column=2)
        maxDulabel = Label(frame, **opts, text="Max speed times threshhold").grid(row=3, column=0, columnspan=2)
        self.maxDuEntry = Entry(frame, **entryopts)
        self.maxDuEntry.insert(0, threshholds[1])
        self.maxDuEntry.grid(row=3, column=2)
        minDislabel = Label(frame, **opts, text="Min dispercy change threshhold").grid(row=4, column=0, columnspan=2)
        self.minDisEntry = Entry(frame, **entryopts)
        self.minDisEntry.insert(0, threshholds[2])
        self.minDisEntry.grid(row=4, column=2)
        maxDislabel = Label(frame, **opts, text="Max dispercy times threshhold").grid(row=5, column=0, columnspan=2)
        self.maxDisEntry = Entry(frame, **entryopts)
        self.maxDisEntry.insert(0, threshholds[3])
        self.maxDisEntry.grid(row=5, column=2)
        apply = Button(frame, **self.buttonOpts, text="Apply", command=self._changeThresholds)
        apply.grid(row=7, column=0, columnspan=2)
    
gui = GUI()
gui.start()




