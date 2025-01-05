from PyQt5 import QtCore, QtGui, QtWidgets
import rclpy
from std_msgs.msg import UInt8
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QLabel, QHBoxLayout, QMainWindow, QAction, QTextEdit, QPushButton
from PyQt5.Qt import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer,QThread, pyqtSignal
import sys
from PyQt5 import uic
import cv2
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
import serial
import time

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("GUI.ui", self)
        self.show()
        # self.bluetooth_connection = None

        # log frame 
        self.frameLogs_Main = self.findChild(QTextEdit, "textEdit_LogsMain")  
        

        # Initialize Bluetooth connection
        self.bluetooth_port = "/dev/rfcomm0" 
        self.bluetooth_baudrate = 9600  
        try:
            self.bluetooth_connection = serial.Serial(self.bluetooth_port, self.bluetooth_baudrate)
            self.appendLog("Bluetooth connected successfully!", self.frameLogs_Main)
            time.sleep(2)

        except Exception as e:
            self.appendLog(f"Failed to connect to Bluetooth: {e}", self.frameLogs_Main)
            self.bluetooth_connection = None

        # Find the QLabel objects for live video and grayscale video
        self.cameraVideo = self.findChild(QLabel, "Live_camera_videoLable")
        
        
        #Speed slider
        self.horizontalSlider_speed = self.findChild(QtWidgets.QSlider, "horizontalSlider_speed")
        self.horizontalSlider_speed.setRange(0, 255)  # Ensure range is set to 0-255
        self.horizontalSlider_speed.valueChanged.connect(self.updateSpeedLog)
        self.horizontalSlider_speed.valueChanged.connect(self.updateSpeedPercentageLog)


        #Control Buttons
        self.MovePushBt_Forward = self.findChild(QPushButton, "Forward_PushB")  
        self.MovePushBt_Forward.clicked.connect(lambda: self.MovingInfo("Forward"))
        QShortcut(QKeySequence("W"), self).activated.connect(self.MovePushBt_Forward.click)

        self.MovePushBt_Left = self.findChild(QPushButton, "Left_PushB")
        self.MovePushBt_Left.clicked.connect(lambda: self.MovingInfo("Left"))
        QShortcut(QKeySequence("A"), self).activated.connect(self.MovePushBt_Left.click)

        self.MovePushBt_Right = self.findChild(QPushButton, "Right_PushB")
        self.MovePushBt_Right.clicked.connect(lambda: self.MovingInfo("Right"))
        QShortcut(QKeySequence("D"), self).activated.connect(self.MovePushBt_Right.click)

        self.MovePushBt_Back = self.findChild(QPushButton, "Back_PushB")
        self.MovePushBt_Back.clicked.connect(lambda: self.MovingInfo("Backward"))
        QShortcut(QKeySequence("S"), self).activated.connect(self.MovePushBt_Back.click)

        self.MovePushBt_STOP = self.findChild(QPushButton, "STOP_PushB")
        self.MovePushBt_STOP.clicked.connect(lambda: self.MovingInfo("Stop"))
        QShortcut(QKeySequence("Space"), self).activated.connect(self.MovePushBt_STOP.click)


        # Mode buttons
        self.MovePushBt_Button = self.findChild(QPushButton, "Moving_Button")  
        self.MovePushBt_Button.clicked.connect(lambda: self.onButtonClick("b"))
                
        self.LinePushBt_Button = self.findChild(QPushButton, "Line_Button")  
        self.LinePushBt_Button.clicked.connect(lambda: self.onButtonClick("l"))
                
        self.ObstaclePushBt_Button = self.findChild(QPushButton, "Obstacle_Button")  
        self.ObstaclePushBt_Button.clicked.connect(lambda: self.onButtonClick("o"))
                
        self.FirePushBt_Button = self.findChild(QPushButton, "Fire_Button")  
        self.FirePushBt_Button.clicked.connect(lambda: self.onButtonClick("f"))

        self.label_display = self.findChild(QLabel, "MovingLabel")  # Make sure to add a QLabel in your UI
        self.label_display.setText("Choose a Mode")  # Set the initial text


        # Fire buttons
        self.servo_up = self.findChild(QPushButton, "ServoUP_Button")  
        self.servo_up.clicked.connect(lambda: self.send_data("v+"))

        self.servoDown = self.findChild(QPushButton, "ServoDown_Button")  
        self.servoDown.clicked.connect(lambda: self.send_data("v-"))

        self.trunON = self.findChild(QPushButton, "PumpOn_Button")  
        self.trunON.clicked.connect(lambda: self.send_data("N"))

        self.trunOFF = self.findChild(QPushButton, "PumpOff_Button")  
        self.trunOFF.clicked.connect(lambda: self.send_data("N"))

        #stops Buttons 
        self.Moveoff = self.findChild(QPushButton, "OFFManual")  
        self.Moveoff.clicked.connect(lambda: self.send_data("z"))

        self.obsoff = self.findChild(QPushButton, "OFFobs")  
        self.obsoff.clicked.connect(lambda: self.send_data("S"))

        self.lineoff = self.findChild(QPushButton, "OFFLine")  
        self.lineoff.clicked.connect(lambda: self.send_data("S"))
        
        
        self.startVideoStream()

    def send_data(self,direction):

        current_value = self.horizontalSlider_speed.value()
        if self.bluetooth_connection and self.bluetooth_connection.is_open:
            try:
                # Format: "DIRECTION,SPEED" (e.g., "Forward,128")
                data_to_send = f"{direction},{current_value}\n"
                self.bluetooth_connection.write(data_to_send.encode('utf-8'))
                print(f"Sent to HC-05: {data_to_send}")  # Print in terminal for debugging
                self.appendLog(f"Sent to UNO: {data_to_send}", self.frameLogs_Main)
            except Exception as e:
                self.appendLog(f"Failed to send data to AFAY: {e}", self.frameLogs_Main)
                print(f"Error: {e}")  # Print in terminal for debugging
                time.sleep(1)
        else:
            self.appendLog("No Bluetooth connection!", self.frameLogs_Main)
            print("No Bluetooth connection!")  # Print in terminal for debugging
    

    
    def newDirction(self, string):
        print(string)
        if string == "Forward":
            mode = "f"
        elif string == "Left":
            mode = "l"
        elif string == "Backward":
            mode = "b"
        elif string == "Right":
            mode = "r"
        elif string == "Stop":
            mode = "s"
        

        else:
            mode = "Unknown Mode"
        return mode
            
    def onButtonClick(self, string):
        print(string)
        if string == "b":
            mode = "Moving Mode"
            self.send_data("B")
        elif string == "l":
            mode = "Line Mode"
            self.send_data("L")
        elif string == "o":
            mode = "Obstacle Mode"
            self.send_data("A")
        elif string == "f":
            mode = "Fire Mode"
            self.send_data("B")
        else:
            mode = "Unknown Mode"
       
        self.label_display.setText(f"{mode}")  # Update the QLabel with the button clicked

    def updateSpeedLog(self):
        """Update log with the current slider value."""
        current_value = self.horizontalSlider_speed.value()
        log_text = f"Slider Value: {current_value}\n"
        print(log_text)
        # self.appendLog(log_text, self.frameLogs_Main)

    def updateSpeedPercentageLog(self):
        """Update log with the current slider value as a percentage."""
        current_value = self.horizontalSlider_speed.value()
        percentage = (current_value / 255) * 100  # Calculate percentage
        log_text = f"Slider Percentage: {percentage:.2f}%\n"
        self.appendLog(log_text, self.frameLogs_Main)

    def MovingInfo(self,direction):
        """Log the current button click and movement."""
        print(f"Button clicked: {direction}")
        current_value = self.horizontalSlider_speed.value()
        percentage = (current_value / 255) * 100  # Calculate percentage

        log_text = f"Moving {direction} with speed {percentage:.2f}%\n"
        
        self.appendLog(log_text, self.frameLogs_Main)
        directionnew =self.newDirction(direction)
        self.send_data(directionnew)
        
        # if self.bluetooth_connection and self.bluetooth_connection.is_open:
        #     try:
        #         # Format: "DIRECTION,SPEED" (e.g., "Forward,128")
        #         data_to_send = f"{direction},{current_value}\n"
        #         self.bluetooth_connection.write(data_to_send.encode('utf-8'))
        #         print(f"Sent to HC-05: {data_to_send}")  # Print in terminal for debugging
        #         self.appendLog(f"Sent to UNO: {data_to_send}", self.frameLogs_Main)
        #     except Exception as e:
        #         self.appendLog(f"Failed to send data to ESP32: {e}", self.frameLogs_Main)
        #         print(f"Error: {e}")  # Print in terminal for debugging
        #         time.sleep(1)
        # else:
        #     self.appendLog("No Bluetooth connection!", self.frameLogs_Main)
        #     print("No Bluetooth connection!")  # Print in terminal for debugging

        

    def startVideoStream(self):
            # ip_camera_url = "http://10.98.165.205:8080/video"
            ip_camera_url = "http://192.168.45.234:8080/video"
            self.capture = cv2.VideoCapture(ip_camera_url)

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.updateFrame)
            self.timer.start(1)

    def updateFrame(self):
        ret, frame = self.capture.read()
        if ret:
            # Send the frame to the image_processing function
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Update the original video label (self.cameraVideo)
            self.displayFrameInLabel(frame_rgb, self.cameraVideo)

        # else:
            print("Failed to capture video frame")
    def displayFrameInLabel(self, frame, label):
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        qImg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        scaled_pixmap = pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio)
        label.setPixmap(scaled_pixmap)


    
    def appendLog(self, log_text, log_frame):
        if log_frame:  # Check if the widget is found
            log_frame.append(log_text)  # Append log to QTextEdit
        else:
            print("Log frame not found")

    def closeEvent(self, event):
        self.capture.release()
        event.accept()


app = QApplication(sys.argv)
window = UI()
window.show()
app.exec_()