# main
#
# application to provide gui for control of attiny2313 development board.
#
# author: Peter Backlund
# email: backlunp (at) gmail.com
# date: 11/7/2014

import Tkinter

class control_tk(Tkinter.Tk):
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self, textvariable=self.entryVariable)
        self.entry.grid(column=0, row=0, sticky='EW')
        self.entry.bind("<Return>", self.onPressEnter)
        self.entryVariable.set(u"Enter text here.")

        button = Tkinter.Button(self, text=u"Click me !",
                                command=self.onButtonClick)
        button.grid(column=1, row=0)

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self, textvariable=self.labelVariable,
                              anchor="w", fg="white", bg="grey")
        label.grid(column=0, row=1, columnspan=2, sticky="EW")
        self.labelVariable.set(u"hello")

        self.grid_columnconfigure(0, weight=1)
        self.resizable(True, False)
        self.update()
        self.geometry(self.geometry())
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def onButtonClick(self):
        self.labelVariable.set( self.entryVariable.get() + "Button clicked")
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def onPressEnter(self, event):
        self.labelVariable.set( self.entryVariable.get() + "Enter")
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

if __name__ == "__main__":
    app = control_tk(None)
    app.title('ATTiny Dev Board Controller')
    app.mainloop()