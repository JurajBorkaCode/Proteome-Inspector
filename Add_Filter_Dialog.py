import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from collections import OrderedDict
import webbrowser
import pandas as pd
import os

from SuperClass import SuperClass

class Add_Filter_Dialog(SuperClass):
    def __init__(self,parent,title,data):
        self.data = data

        self.Cellular_Component_list = []
        self.Molecular_Function_list = []
        self.Biological_Process_list = []
        self.load_lists()

        self.submit = False
        self.filters = {"Cellular Component":[],"Molecular Function":[],"Biological Process":[]}
        self.types = ["Cellular Component","Molecular Function","Biological Process"]

        super().__init__(parent, title, width = 350, height = 600, take_focus=True, extendable=False)


    def body(self, frame):
        self.clicked = tk.StringVar()
        self.clicked.trace_add("write", self.update_data)
        self.type = tk.OptionMenu(frame,self.clicked,*self.types)
        self.type.pack(side=tk.TOP)

        self.search = tk.StringVar()
        self.search.trace_add("write", self.search_tree)
        self.search_en = ttk.Entry(frame, font=("Calibri 12"), textvariable = self.search)
        self.search_en.pack(side=tk.TOP)

        self.filter_selection = ttk.Frame(frame)
        self.filter_selection.pack(side=tk.TOP)

        self.filter_selection_frame = tk.Frame(self.filter_selection)
        self.filter_selection_frame.pack(side=tk.LEFT)

        self.filter_selection_scrollbar = ttk.Scrollbar(self.filter_selection)
        self.filter_selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        self.filter_selection_tree = ttk.Treeview(self.filter_selection, yscrollcommand=self.filter_selection_scrollbar.set, height=24)
        self.filter_selection_tree['columns'] = ('Option')
        self.filter_selection_tree.pack()

        self.filter_selection_tree.column('#0',width=0,stretch='NO')
        self.filter_selection_tree.column('Option',width=300)

        self.filter_selection_tree.heading('#0', text='')
        self.filter_selection_tree.heading('Option', text='Option')

        self.filter_selection_scrollbar.config(command = self.filter_selection_tree.yview)



    def search_tree(self,var,index,mode):
        search = self.search.get().upper()

        if self.clicked.get() == 'Cellular Component':
            counter = 0
            for i in self.Cellular_Component_list:
                if search in i.upper():
                    text_to_add = i.replace(' ', '\ ')
                    self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif self.clicked.get() == 'Molecular Function':
            counter = 0
            for i in self.Molecular_Function_list:
                if search in i.upper():
                    text_to_add = i.replace(' ', '\ ')
                    self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif self.clicked.get() == 'Biological Process':
            counter = 0
            for i in self.Biological_Process_list:
                if search in i.upper():
                    text_to_add = i.replace(' ', '\ ')
                    self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))


    def load_lists(self):
        self.Cellular_Component_list = []
        self.Molecular_Function_list = []
        self.Biological_Process_list = []

        counter = 1
        for i in self.data:
            self.Cellular_Component_list.extend(self.data[i].cellular_component)
            self.Molecular_Function_list.extend(self.data[i].molecular_function)
            self.Biological_Process_list.extend(self.data[i].biological_process)
            counter += 1
        self.Cellular_Component_list = list(OrderedDict.fromkeys(self.Cellular_Component_list))
        self.Molecular_Function_list = list(OrderedDict.fromkeys(self.Molecular_Function_list))
        self.Biological_Process_list = list(OrderedDict.fromkeys(self.Biological_Process_list))

    def update_data(self,var,index,mode):
        self.filter_selection_tree.delete(*self.filter_selection_tree.get_children())
        if self.clicked.get() == 'Cellular Component':
            counter = 0
            for i in self.Cellular_Component_list:
                text_to_add = i.replace(' ', '\ ')
                self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif self.clicked.get() == 'Molecular Function':
            counter = 0
            for i in self.Molecular_Function_list:
                text_to_add = i.replace(' ', '\ ')
                self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif self.clicked.get() == 'Biological Process':
            counter = 0
            for i in self.Biological_Process_list:
                text_to_add = i.replace(' ', '\ ')
                self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))



    def back(self, event=None):
        try:
            selected = self.filter_selection_tree.item(self.filter_selection_tree.focus())["values"][0]
            print(selected)
        except:
            selected = self.search.get()

        self.filters[self.clicked.get()].append(selected)
        self.submit = True


        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()












#
