import tkinter as tk
import os
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


'''
Input for more suffisticated GUI

class DemoWindow(QMainWindow):
    """
    User Interface to access our prototype's capabilities
    To open the Qt Designer, activate your environment and type "designer" at the prompt and press enters
    """
    def __init__(self):
        super(DemoWindow, self).__init__()

        # Determines, whether buttons are enabled or disabled
        self.buttons_enabled = True

        # setup the UI components
        self.setupUi()


        # Register listeners
        self.register_config_listeners_and_changers()
        self.register_tool_listeners()


    def setupUi(self):
        #Stuff
        

    def enable_or_disable_all_buttons(self):
        """
        Disables all buttons
        :return:
        """
        if self.buttons_enabled:
            self.buttons_enabled = False
        else:
            self.buttons_enabled = True

        # Enable or disable the buttons-> Bsp:
        # self.current_config_btn_select_other_cfg.setEnabled(self.buttons_enabled)
        
    def register_config_listeners_and_changers(self):
        """
        Registers the listener functions that adjust our self.cfg values as soon as user input changes
        :return:
        """
        # Bsp:
        # For current configuration
        # self.current_config_btn_select_other_cfg.clicked.connect(self.current_config_btn_select_other_cfg_clicked)
    
    def register_tool_listeners(self):
        """
        Registers the functions that call our tool functions (i.e. preprocess, train, test, demo)
        :return:
        """

        # For demo -> Bsp
        #self.demo_btn_start_demo.clicked.connect(self.demo_btn_start_demo_clicked)
    
    
######### Start the demo gui
def start_demo_gui():
    """
    Starts the GUI
    :param cfg:
    :return:
    """
    app = QApplication(sys.argv)
    win = DemoWindow()
    win.show()
    app.exec_()



if __name__ == "__main__":
    start_demo_gui()
'''

# Different Cluster Numbers
OPTIONS = ['No options available']
# Amount of Clusters, selected by user from explorative approach
NUM_CLUSTER = 0
# Label returned by user
LABEL = dict()
# Counter for Label
counter = 1


def popupmsg(msg, title):
    root = tk.Tk()
    root.title(title)
    label = tk.Label(root, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = tk.Button(root, text="Okay", command=root.destroy)
    B1.pack()
    root.mainloop()


def inputboxList():

    def ok():
        input = display.get()
        global NUM_CLUSTER
        NUM_CLUSTER = input

    root = tk.Tk()
    display = tk.StringVar(root)
    display.set(OPTIONS[0])
    dropdown = tk.OptionMenu(root, display, *OPTIONS)
    dropdown.pack()
    button = tk.Button(root, text="OK", command=ok )
    button.pack()
    b2 = tk.Button(root, text="Exit", command=root.destroy)
    b2.pack()
    root.mainloop()


def setOptions(list):
    global OPTIONS
    OPTIONS = list


def inputboxLine():

    def ok():
        input = textBox.get("1.0","end-1c")
        global LABEL
        global counter
        LABEL[counter] = input
        counter += 1

    root = tk.Tk()
    textBox = tk.Text(root, height=2, width=10)
    textBox.pack()
    buttonCommit = tk.Button(root, height=1, width=10, text="Commit",
                             command=lambda: ok())
    # command=lambda: ok() >>> just means do this when i press the button
    buttonCommit.pack()
    b2 = tk.Button(root, text="Exit", command=root.destroy)
    b2.pack()

    tk.mainloop()


if __name__ == '__main__':
    list = ["Hallo","Tschüss"]
    setOptions(list)
    app = inputboxLine()
    print(LABEL)
