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

from pathlib import Path

from Data import Data
from compound import Compound
from Network_Viewer import Network_Viewer
from Molecule_Inspector import Molecule_Inspector
from Molecule_Network_Viewer import Molecule_Network_Viewer



class MainView():
    def __init__(self):
        self.data = Data()
        self.excluded = []

        self.Cellular_Component_list = []
        self.Molecular_Function_list = []
        self.Biological_Process_list = []

        self.set_width = 1130
        self.set_height = 850

        self.root = tk.Tk()

        self.root.title('Data Viewer')

        if sys.platform.startswith('win'):
            pass
        else:
            pass


        self.root.resizable(None,None)

        self.first_resize_occurred = False

        self.root.geometry(f"{self.set_width}x{self.set_height}")


        self.menu_bar = tk.Menu(self.root,tearoff=False)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar,tearoff=False)
        self.network_menu = tk.Menu(self.menu_bar,tearoff=False)
        self.molecule_menu = tk.Menu(self.menu_bar,tearoff=False)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Network", menu=self.network_menu)
        self.menu_bar.add_cascade(label="Molecules", menu=self.molecule_menu)

        self.network_menu.add_command(label="Cellular Component", command=lambda: self.view_network("Cellular Component"))
        self.network_menu.add_command(label="Molecular Function", command=lambda: self.view_network("Molecular Function"))
        self.network_menu.add_command(label="Biological Process", command=lambda: self.view_network("Biological Process"))

        self.file_menu.add_command(label="Load from CSV file", command=self.load_data_from_csv)
        self.file_menu.add_command(label="Load from Pickle file", command=self.load_data_from_pickle)

        self.molecule_menu.add_command(label="Molecule Inspector", command=self.open_molecule_inspector)
        self.molecule_menu.add_command(label="Molecule Network Viewer", command=self.open_molecule_network_viewer)

        self.root_frame = ttk.Frame(self.root)
        self.root_frame.pack(fill=tk.BOTH, expand=tk.TRUE)


        self.proteins = ttk.Frame(self.root_frame, padding=5)
        self.proteins.grid(row=0,column=0)


        self.proteins_frame = tk.Frame(self.proteins)
        self.proteins_frame.pack(side=tk.LEFT)

        self.proteins_scrollbar = ttk.Scrollbar(self.proteins)
        self.proteins_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.proteins_tree = ttk.Treeview(self.proteins_frame, yscrollcommand=self.proteins_scrollbar.set, height=40)
        self.proteins_tree['columns'] = ('Name', 'Full Name', 'Abundance', 'P-Value')
        self.proteins_tree.pack()

        self.proteins_tree.column('#0',width=0,stretch='NO')
        self.proteins_tree.column('Name',width=80)
        self.proteins_tree.column('Full Name',width=500)
        self.proteins_tree.column('Abundance',width=80)
        self.proteins_tree.column('P-Value',width=90)

        self.proteins_tree.heading('#0', text='')
        self.proteins_tree.heading('Name', text='Name')
        self.proteins_tree.heading('Full Name', text='Full Name')
        self.proteins_tree.heading('Abundance', text='Abundance')
        self.proteins_tree.heading('P-Value', text='P-Value')


        self.proteins_scrollbar.config(command = self.proteins_tree.yview)




        self.filters = ttk.Frame(self.root_frame)
        self.filters.grid(row=0,column=1)

        self.filter_options = ttk.Frame(self.filters)
        self.filter_options.pack(side=tk.TOP)

        self.filter_options_tree = ttk.Treeview(self.filter_options, height=4)
        self.filter_options_tree['columns'] = ('Option')
        self.filter_options_tree.pack()

        self.filter_options_tree.column('#0',width=0,stretch='NO')
        self.filter_options_tree.column('Option',width=320)

        self.filter_options_tree.heading('#0', text='')
        self.filter_options_tree.heading('Option', text='Option')

        self.filter_options_tree.insert(parent='', index=0, values=('None'))
        self.filter_options_tree.insert(parent='', index=1, values=('Cellular\ Component'))
        self.filter_options_tree.insert(parent='', index=2, values=('Molecular\ Function'))
        self.filter_options_tree.insert(parent='', index=3, values=('Biological\ Process'))

        self.filter_options_tree.bind('<<TreeviewSelect>>',lambda event: self.update_options())


        self.spacer = tk.Label(self.filters, text="")
        self.spacer.pack(side=tk.TOP)

        self.search = tk.StringVar()
        self.search.trace_add("write", self.search_tree)

        self.search_en = ttk.Entry(self.filters, font=("Calibri 12"), textvariable = self.search)
        self.search_en.pack(side=tk.TOP)

        self.filter_selection = ttk.Frame(self.filters)
        self.filter_selection.pack(side=tk.TOP)

        self.filter_selection_frame = tk.Frame(self.filter_selection)
        self.filter_selection_frame.pack(side=tk.LEFT)

        self.filter_selection_scrollbar = ttk.Scrollbar(self.filter_selection)
        self.filter_selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        self.filter_selection_tree = ttk.Treeview(self.filter_selection, yscrollcommand=self.filter_selection_scrollbar.set, height=25)
        self.filter_selection_tree['columns'] = ('Option')
        self.filter_selection_tree.pack()

        self.filter_selection_tree.column('#0',width=0,stretch='NO')
        self.filter_selection_tree.column('Option',width=300)

        self.filter_selection_tree.heading('#0', text='')
        self.filter_selection_tree.heading('Option', text='Option')

        self.filter_selection_tree.bind('<<TreeviewSelect>>',lambda event: self.update_selected())

        self.filter_selection_scrollbar.config(command = self.filter_selection_tree.yview)

        self.clear_btn = ttk.Button(self.filters, text='Clear', command=self.clear_op)
        self.clear_btn.pack(side=tk.TOP)

        self.info_btn = ttk.Button(self.filters, text='Protein Info', command=self.more_info)
        self.info_btn.pack(side=tk.TOP)






        self.root.mainloop()



    def open_molecule_inspector(self):
        a = Molecule_Inspector(self.root,"Molecule Inspector",self.data.full_data)

    def open_molecule_network_viewer(self):
        a = Molecule_Network_Viewer(self.root,"Molecule Network Viewer",self.data.full_data)

    def view_network(self,cond):
        #create graph
        G = nx.Graph()

        #create nodes
        counter = 1
        for i in self.data.full_data:
            G.add_node(self.data.full_data[i].name,label = self.data.full_data[i].name, abundance=self.data.full_data[i].abundance)
            counter += 1

        #create edges
        if cond == "Cellular Component":
            for i in self.data.full_data:
                for j in self.data.full_data[i].cellular_component:
                    for x in self.data.full_data:
                        for y in self.data.full_data[x].cellular_component:
                            if j == y:
                                if G.has_edge(self.data.full_data[x].name,self.data.full_data[i].name):
                                    pass
                                elif self.data.full_data[x].name == self.data.full_data[i].name:
                                    pass
                                else:
                                    G.add_edge(self.data.full_data[i].name,self.data.full_data[x].name,label=y)
        elif cond == "Molecular Function":
            for i in self.data.full_data:
                for j in self.data.full_data[i].molecular_function:
                    for x in self.data.full_data:
                        for y in self.data.full_data[x].molecular_function:
                            if j == y:
                                if G.has_edge(self.data.full_data[x].name,self.data.full_data[i].name):
                                    pass
                                elif self.data.full_data[x].name == self.data.full_data[i].name:
                                    pass
                                else:
                                    G.add_edge(self.data.full_data[i].name,self.data.full_data[x].name,label=y)
        elif cond == "Biological Process":
            for i in self.data.full_data:
                for j in self.data.full_data[i].biological_process:
                    for x in self.data.full_data:
                        for y in self.data.full_data[x].biological_process:
                            if j == y:
                                if G.has_edge(self.data.full_data[x].name,self.data.full_data[i].name):
                                    pass
                                elif self.data.full_data[x].name == self.data.full_data[i].name:
                                    pass
                                else:
                                    G.add_edge(self.data.full_data[i].name,self.data.full_data[x].name,label=y)


        #plot and display network

        a = Network_Viewer(self.root,cond,G,self.data.full_data)




    def network_dialog(self,network):
        network_window = tk.Toplevel(self.root)

        network_window.title(cond + " Network")

        network_window.geometry("500x600")




    def more_info(self):
        selected = self.proteins_tree.item(self.proteins_tree.focus())

        webbrowser.open(self.data.full_data[selected["values"][0]].web)







    def clear_op(self):
        self.update_options()
        self.search.set("")

    def load_data_from_csv(self):
        try:
            filepath = fd.askopenfilename()
            if filepath:
                #FORMAT CSV
                data = pd.read_csv(filepath)
                data = data.rename(columns={"﻿Molecule Name":"﻿Molecule Name","∆LFQ":"∆LFQ","Std. Dev.":"Std. Dev.","P-Value":"P-Value","Molecule Type":"Molecule_Type"})
                data = data.drop(data[data.Molecule_Type == "METABOLITE"].index)


                for index, row in data.iterrows():
                    name = (row['Molecule Name'].split(' '))[0]
                    try:
                        protein_data = self.get_protein_data(name)
                        self.data.full_data[name] = Compound(name,protein_data[0],row['P-Value'],protein_data[1],protein_data[2],protein_data[3],row['∆LFQ'],"https://beta.uniprot.org/uniprotkb/" + self.Get_protein_ID_from_genename(name).strip() + "/entry",protein_data[4],protein_data[5])
                        print("| " + name + " added")
                    except:
                        self.excluded.append(name)
                        print(name + " not found")

                with open(filepath.replace('.csv','') + '.pickle', 'wb') as handle:
                    pickle.dump(self.data.full_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

                with open(filepath.replace('.csv','') + '.txt', 'w') as f:
                    for i in self.excluded:
                        f.write(i+'\n')

        except:
            pass
        self.load_proteins_tree()
        self.load_lists()



    def Get_protein_ID_from_genename(self,gene_name):
        url = 'https://www.uniprot.org/uploadlists/'

        params = {
        'from': 'GENENAME',
        'to': 'ACC',
        'format': 'tab',
        'query': gene_name,
        'taxon': '559292'
        }


        data = urllib.parse.urlencode(params)
        data = data.encode('utf-8')
        req = urllib.request.Request(url, data)
        with urllib.request.urlopen(req) as f:
           response = f.read()

        decoded = response.decode('utf-8')
        data = decoded[9:len(decoded)]
        a = data.split('	')
        return a[1]

    def get_protein_data(self,gene_name):
        protein_ID = self.Get_protein_ID_from_genename(gene_name)
        name = ""
        locations = []
        MF = []
        BP = []
        C = []
        P = []

        url = "https://rest.uniprot.org/uniprotkb/" + protein_ID.strip() + ".txt"
        file = urllib.request.urlopen(url)


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
                line_process = decoded_line.replace('CC       Reaction=','').strip()
                split_semicolon = line_process.split(';')
                split_eq = split_semicolon[0].split(' = ')
                C = split_eq[0].split(' + ')
                P = split_eq[1].split(' + ')

        return [name,locations,MF,BP,C,P]


    #Reaction=GTP + H2O = GDP + H(+) + phosphate; Xref=Rhea:RHEA:19669

    def load_data_from_pickle(self):
        try:
            filepath = fd.askopenfilename()
            if filepath:
                with open(filepath, 'rb') as handle:
                    self.data.full_data = pickle.load(handle)
                self.load_proteins_tree()
                self.load_lists()
        except:
            pass


    def search_tree(self,var,index,mode):
        self.filter_selection_tree.delete(*self.filter_selection_tree.get_children())
        selected = self.filter_options_tree.item(self.filter_options_tree.focus())
        search = self.search.get().upper()

        if selected["values"][0] == 'Cellular Component':
            counter = 0
            for i in self.Cellular_Component_list:
                if search in i.upper():
                    text_to_add = i.replace(' ', '\ ')
                    self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif selected["values"][0] == 'Molecular Function':
            counter = 0
            for i in self.Molecular_Function_list:
                if search in i.upper():
                    text_to_add = i.replace(' ', '\ ')
                    self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif selected["values"][0] == 'Biological Process':
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
        for i in self.data.full_data:
            self.Cellular_Component_list.extend(self.data.full_data[i].cellular_component)
            self.Molecular_Function_list.extend(self.data.full_data[i].molecular_function)
            self.Biological_Process_list.extend(self.data.full_data[i].biological_process)
            counter += 1
        self.Cellular_Component_list = list(OrderedDict.fromkeys(self.Cellular_Component_list))
        self.Molecular_Function_list = list(OrderedDict.fromkeys(self.Molecular_Function_list))
        self.Biological_Process_list = list(OrderedDict.fromkeys(self.Biological_Process_list))




    def load_proteins_tree(self):
        self.proteins_tree.delete(*self.proteins_tree.get_children())
        counter = 0
        for i in self.data.full_data:
            self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
            counter += 1





    def update_options(self):
        selected = self.filter_options_tree.item(self.filter_options_tree.focus())
        self.filter_selection_tree.delete(*self.filter_selection_tree.get_children())
        if selected["values"][0] == 'Cellular Component':
            counter = 0
            for i in self.Cellular_Component_list:
                text_to_add = i.replace(' ', '\ ')
                self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif selected["values"][0] == 'Molecular Function':
            counter = 0
            for i in self.Molecular_Function_list:
                text_to_add = i.replace(' ', '\ ')
                self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))
        elif selected["values"][0] == 'Biological Process':
            counter = 0
            for i in self.Biological_Process_list:
                text_to_add = i.replace(' ', '\ ')
                self.filter_selection_tree.insert(parent='', index=counter, values=(text_to_add))



    def update_selected(self):
        try:
            self.proteins_tree.delete(*self.proteins_tree.get_children())
            selected = self.filter_options_tree.item(self.filter_options_tree.focus())
            selected2 = self.filter_selection_tree.item(self.filter_selection_tree.focus())
            if selected["values"][0] == 'Cellular Component':
                counter = 0
                for i in self.data.full_data:
                    if selected2["values"][0] in self.data.full_data[i].cellular_component:
                        self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
                        counter += 1
            elif selected["values"][0] == 'Molecular Function':
                counter = 0
                for i in self.data.full_data:
                    if selected2["values"][0] in self.data.full_data[i].molecular_function:
                        self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
                        counter += 1
            elif selected["values"][0] == 'Biological Process':
                counter = 0
                for i in self.data.full_data:
                    if selected2["values"][0] in self.data.full_data[i].biological_process:
                        self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
                        counter += 1
        except:
            self.load_proteins_tree()








#
