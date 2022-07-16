import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from collections import OrderedDict
import webbrowser
import pandas as pd
import os

from SuperClass import SuperClass

class Remove_Filter_Dialog(SuperClass):
    def __init__(self,parent,title,filters):
        self.submit = False
        self.filters = filters

        super().__init__(parent, title, width = 970, height = 800, take_focus=True, extendable=False)
