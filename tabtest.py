# main
#
# application to provide gui for control of attiny2313 development board.
#
# author: Peter Backlund
# email: backlunp (at) gmail.com
# date: 11/7/2014

import Tkinter as tk
import ttk

import sys
import serial
import glob
import time

def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(10)]

    elif sys.platform.startswith('linux'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except serial.SerialException:
            pass
    return result

class ControlTK(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

        # set up serial stuff
        # get list of available com channels
        self.comName = tk.StringVar()
        self.comName.set("COM6")
        availableComs = serial_ports() #serial.tools.list_ports
        #for com in availableComs:
        #    print com
        comMenu = tk.OptionMenu(self, self.comName, *availableComs, command=self.updateCom)
        comMenu.grid(row=0, column=0, sticky="W")
        try:
            self.ser = serial.Serial(self.comName.get(), 9600)
        except serial.SerialException:
            print "fuck"

        self.createGui()

    def updateCom(self, val):
        self.ser.close()
        self.comName.set(val)
        print self.comName.get()
        try:
            self.ser = serial.Serial(self.comName.get(), 9600)
            self.createGui()
        except serial.SerialException:
            print "fuck"

    def createGui(self):

        backPlate = ttk.Notebook(self.parent)
        self.page1 = ttk.Frame(backPlate)
        self.page2 = ttk.Frame(backPlate)
        backPlate.add(self.page1, text="Pins")
        backPlate.add(self.page2, text="AT")
        backPlate.grid(row=1, column=0)

        self.pinControlTab()
        self.ATControlTab()

    def ATControlTab(self):

        infoFrame = tk.LabelFrame(self.page2, text="Module INFO")
        infoFrame.grid(row=0, column=0)

        # First set up the name row
        nameLabel = tk.Label(infoFrame, text="Name:",
                             anchor="w", fg="white", bg="grey")
        nameLabel.grid(row=0, column=0)

        self.moduleName = tk.StringVar()
        nameEntry = tk.Entry(infoFrame, textvariable=self.moduleName)
        nameEntry.grid(row=0, column=1)

        nameSend = tk.Button(infoFrame, text=u"Send", command=self.setATName)
        nameSend.grid(row=0, column=2)

        # Now comes the access pin row
        pinLabel = tk.Label(infoFrame, text="PIN:",
                             anchor="w", fg="white", bg="grey")
        pinLabel.grid(row=1, column=0)

        self.modulePin= tk.StringVar()
        pinEntry = tk.Entry(infoFrame, textvariable=self.modulePin)
        pinEntry.grid(row=1, column=1)

        pinSend = tk.Button(infoFrame, text=u"Send", command=self.setATPin)
        pinSend.grid(row=1, column=2)

        addrLabel = tk.Label(infoFrame, text="BT Addr:",
                             anchor="w", fg="white", bg="grey")
        addrLabel.grid(row=2, column=0)

        self.moduleAddr = tk.StringVar()
        self.moduleAddr.set("14:12:C4:FU")
        addrOut = tk.Label(infoFrame, textvariable=self.moduleAddr)
        addrOut.grid(row=2, column=1)

        # add a frame for the reset button
        resetFrame = tk.LabelFrame(self.page2, text="Reset")
        resetFrame.grid(row=1, column=0, sticky="EW")

        resetWarning = tk.Label(resetFrame, text="This will set the module to the default state.")
        resetWarning.grid(row=0, column=0)

        resetButton = tk.Button(resetFrame, text=u"Restore",
                                command=self.onReset)
        resetButton.grid(row=0, column=1, sticky="E")

    #class ATControls
    def onReset(self):
        print "lol, reset"

    def setATName(self):
        self.ser.write("AT+NAME=" + self.moduleName.get())

    def getATName(self):
        print "AT+NAME?"

    def setATPin(self):
        print "AT+PSWD=" + self.modulePin.get()

    def getATPin(self):
        print "AT+PSWD?"

    def getATAddr(self):
        print "AT+ADDR?"

    def pinControlTab(self):

        portNames = ["PORTB", "PORTD"]
        portFrames = []
        pwmPins = ["PB2", "PB3", "PD4", "PD5"]

        pinArr = [] # array to hold pinObj objects

        # Set up a frame for each port
        for i, port in enumerate(portNames):
            portFrames.append(
                tk.LabelFrame(self.page1, text=port, width=250, height=250)
            )

        # Grid each frame
        for i, portFrame in enumerate(portFrames):
            portFrame.grid(row=2, column=i)

        for i, port in enumerate(["PB", "PD"]):
            for pin in range(0, 8):

                if port+str(pin) in pwmPins:

                    pinObj = self.PinOps(portNames[i], self.ser, portFrames[i], port+str(pin),
                                 pin, True, "off")

                    pinObj.pinDirection = tk.OptionMenu(pinObj.portFrame, pinObj.currentDir,
                                                      'in', 'out', 'pwm', command=pinObj.updateDir)
                    pinObj.pinDirection.grid(row=pin, column=2)

                    pinPWM = tk.Entry(pinObj.portFrame, textvariable=pinObj.PWMDC, width=3)
                    pinPWM.grid(row=pin, column=3)
                    pinPWM.bind("<Return>", pinObj.onPressEnter)

                    pwmLabel = tk.Label(pinObj.portFrame, text='%')
                    pwmLabel.grid(row=pin, column=4)
                else:
                    pinObj = self.PinOps(portNames[i], self.ser, portFrames[i], port+str(pin),
                                 pin, False, "off")

                    pinObj.pinDirection = tk.OptionMenu(pinObj.portFrame, pinObj.currentDir,
                                                      'in', 'out', command=pinObj.updateDir)
                    pinObj.pinDirection.grid(row=pin, column=2)

                pinArr.append(pinObj)

                # Declare label
                pinLabel = tk.Label(pinObj.portFrame, text=pinObj.pinName)
                pinLabel.grid(row=pin, column=0)

                # Declare button and store in pinops object
                pinObj.pinButton = tk.Button(pinObj.portFrame, text=pinObj.currentState,
                                           command=pinObj.onButtonClick)
                pinObj.pinButton.grid(row=pin, column=1)


    class PinOps:
        def __init__(self, port, ser, portframe, name, number, pwm, state):
            self.ser = ser
            self.portName = port # PORTB, PORTD
            self.portFrame = portframe # portFrames[0]
            self.pinName = name # PB0, PD1...
            self.pinNumber = number # 1, 2...
            self.PWM = pwm # TRUE, FALSE
            self.PWMDC = tk.StringVar() # 0-100
            self.currentState = state # on, off
            self.currentDir = tk.StringVar() # in, out, pwm if dir is in board will declare pin state
            self.currentDir.set("out")

        def onButtonClick(self):
            # the on/off button has been clicked check dir is out
            if self.currentDir.get() != "in": #"out" or "pwm":
                if self.currentState == "off":
                    self.currentState = "on"
                else:
                    self.currentState = "off"

                self.pinButton["text"] = self.currentState

            print self.currentState
            #writeToBoard(self.currentState)
            self.ser.write(self.currentState)
            #print self.ser


        def onPressEnter(self, event):
            # a new pwm value was entered make sure it's between 0 and 100
            pwmValue = int(self.PWMDC.get())
            if pwmValue in range(0, 100, 1):
                print self.PWMDC.get()
            elif pwmValue >= 100:
                self.PWMDC.set(100)
            else:
                self.PWMDC.set(0)

        def updateDir(self, val):
            #self.currentDir =
            print self.currentDir.get()

        def getPortName(self):
            return self.portName

        def getPinName(self):
            return self.pinName

        def getPinNumber(self):
            return self.pinNumber

        def hasPWM(self):
            return self.PWM

        def setCurrentState(self, state):
            self.currentState = state

        def getCurrentState(self):
            return self.currentState




if __name__ == "__main__":
    app = ControlTK(None)
    app.title('ATTiny Dev Board Controller')
    app.mainloop()