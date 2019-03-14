from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from imutils.video import VideoStream
from imutils.video import FPS
import textDetectionGUI
import textDetection
import textDetectionVideo
import cv2
import sys
import time

class MyQtApp(textDetectionGUI.Ui_MainWindow, QtWidgets.QMainWindow): 
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.showMaximized(cd) #页面最大化
        self.setWindowTitle("Text Detection GUI Tool")
        self.toolButton.clicked.connect(self.select_image)
        self.detection_PB.clicked.connect(self.detect_text)
        self.recognition_PB.clicked.connect(lambda: self.detect_text(True))
        self.dyDetect_PB.clicked.connect(self.change_page)
        self.turnOn_PB.clicked.connect(self.button_tool)
        
        self.th = Thread(self)
        self.th.changePixmap.connect(self.label_7.setPixmap)
        self.cameraState = False

    def button_tool(self):
        if self.cameraState == False:
            self.th = Thread(self)
            self.th.changePixmap.connect(self.label_7.setPixmap)
            self.th.start()
            self.cameraState = True
            self.turnOn_PB.setText("Stop")
        else:
            self.th.stop()
            self.cameraState = False
            self.turnOn_PB.setText("Turn on camera")


    def change_page(self):
        if self.stackedWidget.currentIndex() == 0:
            self.stackedWidget.setCurrentIndex(1)         
            # myDetection = textDetectionVideo.myTextDetectionVideo()
            # myDetection.detectText()
        else:
            self.stackedWidget.setCurrentIndex(0)


    def detect_video_text(self):
        myDetection = textDetectionVideo.myTextDetectionVideo()
		# load the pre-trained EAST text detector
        print("[INFO] loading EAST text detector...")
        # if a video path was not supplied, grab the reference to the web cam
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        time.sleep(1.0)
        # start the FPS throughput estimator
        fps = FPS().start()
        # loop over frames from the video stream
        while True:
            # grab the current frame, then handle if we are using a
            # VideoStream or VideoCapture object
            frame = vs.read()
            frame = frame

            # check to see if we have reached the end of the stream
            if frame is None:
                break
            image = myDetection.detectImage(frame)
            # update the FPS counter
            fps.update()

            # # show the output frame
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # rows, cols, channels = image.shape
            # bytesPerLine = channels * cols
            # QImg = QImage(image.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
            # self.label_7.setPixmap(QPixmap.fromImage(QImg).scaled(
            #         self.label_7.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


            cv2.imshow("Text Detection", image)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
                # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        vs.stop()
        # close all windows
        cv2.destroyAllWindows()

    def detect_text(self, rcg = False):
        imagePath = self.imagePath_LE.text()
        if not imagePath:
            QtWidgets.QMessageBox.about(self, "Image Required", "Please select the image.")
            return
        print("imagePath: "+imagePath)

        width = int(self.width_SB.text())
        height = int(self.height_SB.text())
        if (width % 32 != 0 or height % 32 != 0):
            QtWidgets.QMessageBox.about(self, "Input Invalid", "Width or height must be multiple of 32.")
            return

        min_confidence = float(self.mincfd_DSB.text())
        if (min_confidence < 0 or min_confidence > 1):
            QtWidgets.QMessageBox.about(self, "Input Invalid", "Min-confidence must be 0 ~ 1")
            return
        padding = float(self.padding_DSB.text())

        self.captured = cv2.imread(str(imagePath))
        # # OpenCV图像以BGR通道存储，显示时需要从BGR转到RGB
        self.captured = cv2.cvtColor(self.captured, cv2.COLOR_BGR2RGB)
        rows, cols, channels = self.captured.shape
        bytesPerLine = channels * cols
        QImg = QImage(self.captured.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
        self.ori_image_L.setPixmap(QPixmap.fromImage(QImg).scaled(
                self.ori_image_L.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # detect the text from image
        myDetection = textDetection.myTextDetection(imagePath, width, height, min_confidence, padding, rcg)
        (outPutImage, calTime) = myDetection.detectText()
        outPutImage = cv2.cvtColor(outPutImage, cv2.COLOR_BGR2RGB)
        rows, cols, channels = outPutImage.shape
        bytesPerLine = channels * cols
        QImg_output = QImage(outPutImage.data, cols, rows, bytesPerLine, QImage.Format_RGB888)
        self.detected_image_L.setPixmap(QPixmap.fromImage(QImg_output).scaled(
                self.detected_image_L.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # mystr = "[INFO] text detection took %.6f seconds" %float(calTime)
        # print(mystr)
        self.detectText_L.setText("[INFO] Text detection took %.6f seconds" %float(calTime))

    def select_image(self):
        image_path, image_type= QtWidgets.QFileDialog.getOpenFileName(self, 
            "select image", '.', "Images (*.jpg *.png *jpeg *.xpm)")

        if image_path:
            self.imagePath_LE.setText(image_path)


class Thread(QThread):
    changePixmap = pyqtSignal(QPixmap)
        
    def __init__(self, parent=None):
        QThread.__init__(self, parent=parent)
        self.isRunning = True

    def __del__(self):
        self.wait()

    def run(self):
        myDetection = textDetectionVideo.myTextDetectionVideo()
		# load the pre-trained EAST text detector
        print("[INFO] loading EAST text detector...")
        # if a video path was not supplied, grab the reference to the web cam
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        # time.sleep(1.0)
        # start the FPS throughput estimator
        fps = FPS().start()

        while self.isRunning:
            # grab the current frame, then handle if we are using a
            # VideoStream or VideoCapture object
            frame = vs.read()
            frame = frame

            # check to see if we have reached the end of the stream
            if frame is None:
                break
            image = myDetection.detectImage(frame)
            # update the FPS counter
            fps.update()

            rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            convertToQtFormat = QPixmap.fromImage(convertToQtFormat)
            p = convertToQtFormat.scaled(800, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.changePixmap.emit(p)

        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        vs.stop()
        # close all windows
        cv2.destroyAllWindows()
        self.changePixmap.emit(QPixmap(""))
    def stop(self):
        self.isRunning = False
        self.quit()
 

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    qt_app = MyQtApp()
    qt_app.show()
    # MainWindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    sys.exit(app.exec_())
