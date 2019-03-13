from PyQt5 import QtWidgets, QtCore
from PyQt5 import uic
import sys
import serial
import threading
import uartSerial
import time

class MainWindow(QtWidgets.QMainWindow):
    appendResultTextSignal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi("main.ui", self)
        self.ui.show()
        self.setValues()
        uartSerial.openSerial('COM3', 115200)
        self.ser = uartSerial.getSerialConnection()
        thread = threading.Thread(target=self.logThread)
        thread.start()
        thread2 = threading.Thread(target=self.test)
        thread2.start()

    def test(self):
        try:
            #ser = serial.Serial('COM3',115200)
            time.sleep(1)
            self.ser.write("\n".encode())
            self.ser.write("debug\n".encode())
            while not self.shell_state:
                self.checkCurrentState()
                time.sleep(1)
            print("done!")
            self.setPmlogCtl(self.ctl_list)
            self.ser.write("tail -f /var/log/messages &\n".encode())
        except Exception as e:
            print(" Caught exception2 %s : %s" % (e.__class__,e))

    def setValues(self):
        self.status = ["NoDebug","Disable","NoShell","Shell"]
        # self.currentStatus = 0
        self.shell_state = False
        self.lines = []
        self.ctl_list = ["playerfactory.default", "playerfactory.feed", "media.drmcontroller", "playready", "cdmi", "cdmi.playready"]
        self.appendResultTextSignal.connect(self.putResultToWindow)

    def putResultToWindow(self, str):
        self.logWin.append(str)

    def closeEvent(self, event):
        try:
            print("CloseEvent")
            uartSerial.closeSerialConnection()
            QtWidgets.QMainWindow.closeEvent(self, event)
        except Exception as e:
            print(" Caught exception3 %s : %s" % (e.__class__,e))


    def logThread(self):
        try:
            #ser = serial.Serial('COM3',115200)
            # self.ser = uartSerial.getSerialConnection()
            line = []
            while True:
                for c in self.ser.read(): # 1글자씩 받아옴
                    line.append(chr(c))
                    # print('chr(c)= ',chr(c))
                    if c == 10: # 10 == \n 줄바꿈.
                        msg = ''.join(line)
                        if msg.strip() != '':
                            self.lines.append(msg)
                            self.appendResultTextSignal.emit(msg)
                            del line[:]
        except Exception as e:
            print(" Caught exception1 %s : %s" % (e.__class__,e))


    def checkCurrentState(self):
        # self.ser.write("\n".encode())
        current_logs = ''.join(self.lines)
        if "ORG MAIN" in current_logs:
            self.ser.write("sh\n".encode())
            del self.lines[:]
        elif "/ #" in current_logs:
            self.shell_state = True
            del self.lines[:]
        elif "debug message disable" in current_logs:
            print("??????????")
            self.ser.write(120) # F9
            del self.lines[:]
        elif current_logs.strip() == '':
            self.ser.write("debug\n".encode())


    def setPmlogCtl(self, ctl_list):
        def_cmd = "PmLogCtl def {}\n"
        set_cmd = "PmLogCtl set {} debug\n"
        for ctl in ctl_list:
            def_ctl = def_cmd.format(ctl)
            set_ctl = set_cmd.format(ctl)
            self.ser.write(def_ctl.encode())
            print(def_ctl)
            self.ser.write(set_ctl.encode())
            print(set_ctl)


    def sendBtnClicked(self):
        try:
            ser = uartSerial.getSerialConnection()
            inputText = self.lunaTextEdit.text()
            #self.logWin.append(inputText)
            #ser.write(inputText.encode("utf-8"))
            ser.write("d\n".encode())
            ser.write("\n".encode())
            ser.write("luna-send -n 1 luna://com.webos.service.tv.broadcast/getPipelineTemporary '{}'\n".encode())
            ser.write("exit\n".encode())
        except Exception as e:
            print(" Caught exception2 %s : %s" % (e.__class__,e))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    toolWindow = MainWindow(None)
    app.exec_()
