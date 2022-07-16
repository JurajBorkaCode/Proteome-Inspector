import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
from collections import OrderedDict

import urllib.parse
import urllib.request
import time
import os
import sys
import threading
import pandas as pd
import pickle
import networkx as nx
import webbrowser
import copy

from pathlib import Path

from Data import Data
from compound import Compound
from SuperClass import SuperClass

class Add_From_List(SuperClass):
    def __init__(self,parent,title,data,file):
        self.web = tk.StringVar()
        self.web.set("Webpage")
        self.submit = False
        self.compound = None
        self.name = tk.StringVar()
        self.name.set("Name")
        self.out_name = ""
        self.P_value = tk.StringVar()
        self.P_value.set("P-Value")
        self.abundance = tk.StringVar()
        self.abundance.set("Abundance")
        self.missing_data = []
        self.data = data
        self.file = file
        with open(file.replace("pickle","txt").replace("csv","txt")) as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() not in self.data.keys():
                    self.missing_data.append(line.strip())



        super().__init__(parent, title, width = 200, height = 170, take_focus=True, extendable=False)

    def update_data(self,var,index,mode):
        try:
            #FORMAT CSV
            data = pd.read_csv(self.file.replace("pickle","csv"))
            data = data.rename(columns={"﻿Molecule Name":"﻿Molecule Name","∆LFQ":"∆LFQ","Std. Dev.":"Std. Dev.","P-Value":"P-Value","Molecule Type":"Molecule_Type"})
            data = data.drop(data[data.Molecule_Type == "METABOLITE"].index)
            data = data.drop(data[data.Molecule_Type == "LIPID"].index)

            gene_name = self.clicked.get()
            for index, row in data.iterrows():
                name = row['Molecule Name'].split(' ')[0]
                if name == gene_name:
                    self.name.set(name)
                    self.abundance.set(row['∆LFQ'])
                    self.P_value.set(row['P-Value'])
                else:
                    self.name.set(self.clicked.get())
        except:
            pass

    def body(self, frame):

        self.clicked = tk.StringVar()
        self.clicked.trace_add("write", self.update_data)
        self.selection = tk.OptionMenu(frame,self.clicked,*self.missing_data)
        self.selection.pack(side=tk.TOP)

        self.name_e = ttk.Entry(frame, font=("Calibri 12"), textvariable = self.name, width=100)
        self.name_e.pack(side=tk.TOP)
        self.p_val = ttk.Entry(frame, font=("Calibri 12"), textvariable = self.P_value, width=100)
        self.p_val.pack(side=tk.TOP)
        self.abund = ttk.Entry(frame, font=("Calibri 12"), textvariable = self.abundance, width=100)
        self.abund.pack(side=tk.TOP)
        self.webpage = ttk.Entry(frame, font=("Calibri 12"), textvariable = self.web, width=100)
        self.webpage.pack(side=tk.TOP)

    def buttonbox(self):
        self.btn_cancel = ttk.Button(self, text='Cancel', width=10, command=self.cancel)
        self.btn_cancel.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_back = ttk.Button(self, text='Add', width=10, command=self.add_pro)
        self.btn_back.pack(side="right", padx=(5,10), pady=(5,10))

    def add_pro(self):
        protein_data = self.get_protein_data()
        self.compound = Compound(self.name.get(),protein_data[0],self.P_value.get(),protein_data[1],protein_data[2],protein_data[3],self.abundance.get(),self.web.get().replace(".txt",""),protein_data[4],protein_data[5],protein_data[6])
        self.submit = True
        self.out_name = self.name.get()
        self.destroy()

    def get_protein_data(self):
        name = ""
        locations = []
        MF = []
        BP = []
        C = []
        P = []

        url = self.web.get()
        if "/entry" in url:
            file = urllib.request.urlopen(url.replace("/entry",".txt"))
        else:
            file = urllib.request.urlopen(url)

        checkNext = 0
        full_reaction_got = 0
        full_reaction = ""
        reaction = ""

        for line in file:

            decoded_line = line.decode("utf-8")
            if "DR   GO" in decoded_line:
                if "C:" in decoded_line:
                    line_info = decoded_line.split('; ')
                    locations.append(line_info[2].replace('C:',''))
                elif "F:" in decoded_line:
                    line_info = decoded_line.split('; ')
                    MF.append(line_info[2].replace('F:',''))
                elif "P:" in decoded_line:
                    line_info = decoded_line.split('; ')
                    BP.append(line_info[2].replace('P:',''))
            elif "DE   RecName" in decoded_line:
                line_name = decoded_line.split('=')
                name = (line_name[1].strip()).replace(';','')
            elif "Reaction=" in decoded_line:
                full_reaction = decoded_line.strip()
                if ";" in decoded_line:
                    full_reaction_got = 1
                    checkNext = 0
                else:
                    checkNext = 1
            elif checkNext == 1:
                if "CC         " in decoded_line:
                    full_reaction += decoded_line.strip().replace("CC         "," ")
                    if ";" in decoded_line:
                        full_reaction_got = 1
                        checkNext = 0
                    else:
                        checkNext = 1
                else:
                    full_reaction_got = 1
                    checkNext = 0

            elif full_reaction_got == 1:
                line_process = full_reaction.replace('CC       Reaction=','').strip()
                split_semicolon = line_process.split(';')
                reaction = split_semicolon[0]
                if " to " in reaction:
                    split_eq = split_semicolon[0].split(' to ')
                    C = split_eq[0].split(' + ')
                    holder = split_eq[1].split('-')
                    P = holder[1].replace(".","").strip()
                    full_reaction_got = 0
                elif "=" in reaction:

                    split_eq = reaction.split(' = ')
                    C = split_eq[0].split(' + ')
                    P = split_eq[1].split(' + ')
                    full_reaction_got = 0
                else:

                    full_reaction_got = 0

        if type(P) == str:
            P = [P]

        if type(C) == str:
            C = [C]

        return [name,locations,MF,BP,C,P,reaction]
















#
