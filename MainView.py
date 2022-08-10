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
import requests
import mygene

from pathlib import Path
from bs4 import BeautifulSoup

from Data import Data
from compound import Compound
from Network_Viewer import Network_Viewer
from Molecule_Inspector import Molecule_Inspector
from Molecule_Network_Viewer import Molecule_Network_Viewer
from Add_Protein_Dialog import Add_Protein_Dialog
from Add_Reaction_Dialog import Add_Reaction_Dialog
from Add_From_List import Add_From_List



class MainView():
    def __init__(self):
        self.data = Data()
        self.excluded = []
        self.file_name = ""

        self.Cellular_Component_list = []
        self.Molecular_Function_list = []
        self.Biological_Process_list = []

        self.set_width = 1250
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
        self.sort_menu = tk.Menu(self.menu_bar,tearoff=False)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Network", menu=self.network_menu)
        self.menu_bar.add_cascade(label="Molecules", menu=self.molecule_menu)
        self.menu_bar.add_cascade(label="Sort", menu=self.sort_menu)

        self.network_menu.add_command(label="Cellular Component", command=lambda: self.view_network("Cellular Component"))
        self.network_menu.add_command(label="Molecular Function", command=lambda: self.view_network("Molecular Function"))
        self.network_menu.add_command(label="Biological Process", command=lambda: self.view_network("Biological Process"))

        self.file_menu.add_command(label="Load from CSV file [Gene (Protein)]", command=self.load_data_from_csv)
        self.file_menu.add_command(label="Load from CSV file [Protein_Strain]", command=self.load_data_from_csv2)
        self.file_menu.add_command(label="Load from Pickle file", command=self.load_data_from_pickle)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save to Pickle file", command=self.save)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Manually add Protein", command=self.add_protein)
        self.file_menu.add_command(label="Batch add Protein", command=self.batch_add_protein)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Reload Data", command=self.reload_data)
        self.file_menu.add_command(label="Fix {} in IDs", command=self.fix_bracket_in_ids)

        self.molecule_menu.add_command(label="Molecule Inspector", command=self.open_molecule_inspector)
        self.molecule_menu.add_command(label="Molecule Network Viewer", command=self.open_molecule_network_viewer)
        self.molecule_menu.add_separator()
        self.molecule_menu.add_command(label="Fix Molecules", command=self.fix_molecules)
        self.molecule_menu.add_command(label="Edit Reaction", command=self.edit_reactions)

        self.sort_menu.add_command(label="P-Value Ascending", command=self.sort_p_value_asc)
        self.sort_menu.add_command(label="P-Value Descending", command=self.sort_p_value_dec)
        self.sort_menu.add_command(label="Abundance Ascending", command=self.sort_abundance_asc)
        self.sort_menu.add_command(label="Abundance Descending", command=self.sort_abundance_dec)


        self.root_frame = ttk.Frame(self.root)
        self.root_frame.pack(fill=tk.BOTH, expand=tk.TRUE)


        self.proteins = ttk.Frame(self.root_frame, padding=5)
        self.proteins.grid(row=0,column=0)


        self.proteins_frame = tk.Frame(self.proteins)
        self.proteins_frame.pack(side=tk.LEFT)

        self.proteins_scrollbar = ttk.Scrollbar(self.proteins)
        self.proteins_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.proteins_tree = ttk.Treeview(self.proteins_frame, yscrollcommand=self.proteins_scrollbar.set, height=40)
        self.proteins_tree['columns'] = ('Unique', 'Name', 'Gene', 'Full Name', 'Abundance', 'P-Value')
        self.proteins_tree.pack()

        self.proteins_tree.column('#0',width=0,stretch='NO')
        self.proteins_tree.column('Unique',width=50)
        self.proteins_tree.column('Name',width=80)
        self.proteins_tree.column('Gene',width=80)
        self.proteins_tree.column('Full Name',width=500)
        self.proteins_tree.column('Abundance',width=80)
        self.proteins_tree.column('P-Value',width=90)

        self.proteins_tree.heading('#0', text='')
        self.proteins_tree.heading('Unique', text='Unique')
        self.proteins_tree.heading('Name', text='Name')
        self.proteins_tree.heading('Gene', text='Gene')
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


    def fix_bracket_in_ids(self):
        new_dict = {}
        for i in self.data.full_data:
            if " " in i:
                new_name = i.split(" ")[0]
                new_dict[new_name] = self.data.full_data[i]
                new_dict[new_name].name = new_name
            else:
                new_dict[i] = self.data.full_data[i]
        self.data.full_data = new_dict
        self.load_proteins_tree()
        self.load_lists()

    def sort_p_value_asc(self):
        self.data.full_data = dict(sorted(self.data.full_data.items(), key=lambda item: -float(item[1].p_value)))
        self.load_proteins_tree()
        self.load_lists()

    def sort_p_value_dec(self):
        self.data.full_data = dict(sorted(self.data.full_data.items(), key=lambda item: float(item[1].p_value)))
        self.load_proteins_tree()
        self.load_lists()

    def sort_abundance_asc(self):
        self.data.full_data = dict(sorted(self.data.full_data.items(), key=lambda item: -float(item[1].abundance)))
        self.load_proteins_tree()
        self.load_lists()

    def sort_abundance_dec(self):
        self.data.full_data = dict(sorted(self.data.full_data.items(), key=lambda item: float(item[1].abundance)))
        self.load_proteins_tree()
        self.load_lists()

    def save(self):
        if ".pickle" in self.file_name:
            with open(self.file_name, 'wb') as handle:
                pickle.dump(self.data.full_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(self.file_name.replace(".csv",".pickle"), 'wb') as handle:
                pickle.dump(self.data.full_data, handle, protocol=pickle.HIGHEST_PROTOCOL)



    def edit_reactions(self):
        a = Add_Reaction_Dialog(self.root,"Reaction Editor",self.data.full_data)
        if a.submit:
            self.data.full_data = a.data

    def add_protein(self):
        a = Add_Protein_Dialog(self.root,"Molecule Inspector")
        if a.submit:
            self.data.full_data[a.name.get()] = a.compound
        self.load_proteins_tree()
        self.load_lists()

    def batch_add_protein(self):
        a = Add_From_List(self.root,"Batch Add",self.data.full_data,self.file_name)
        if a.submit:
            self.data.full_data[a.name.get()] = a.compound
        self.load_proteins_tree()
        self.load_lists()

    def open_molecule_inspector(self):
        a = Molecule_Inspector(self.root,"Molecule Inspector",self.data.full_data)

    def open_molecule_network_viewer(self):
        a = Molecule_Network_Viewer(self.root,"Molecule Network Viewer",self.data.full_data,self.proteins_tree.item(self.proteins_tree.focus())["values"][0])

    def fix_molecules(self):
        new_data = copy.deepcopy(self.data.full_data)
        for i in self.data.full_data:
            for j in self.data.full_data[i].produces:
                if j[:1].isdigit() and j[1] == " ":
                    new_data[i].produces.remove(j)
                    j = j[2:]
                    new_data[i].produces.append(j)

                new_data[i].produces.remove(j)
                j = j.replace("(out)","")
                j = j.replace("(in)","")
                j = j.replace("a ","")
                j = j.replace("an ","")
                new_data[i].produces.append(j)


            for j in self.data.full_data[i].consumes:
                if j[:1].isdigit() and j[1] == " ":
                    new_data[i].consumes.remove(j)
                    j = j[2:]
                    new_data[i].consumes.append(j)

                new_data[i].consumes.remove(j)
                j = j.replace("(out)","")
                j = j.replace("(in)","")
                j = j.replace("a ","")
                j = j.replace("an ","")
                new_data[i].consumes.append(j)



        self.data.full_data = new_data

        with open('fixed_molecules.pickle', 'wb') as handle:
            pickle.dump(self.data.full_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


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

    def load_data_from_csv2(self):
        self.data.full_data = {}
        try:
            filepath = fd.askopenfilename()
            self.file_name = filepath
            if filepath:
                #FORMAT CSV
                data = pd.read_csv(filepath)
                data = data.rename(columns={"﻿Molecule Name":"﻿Molecule Name","∆LFQ":"∆LFQ","Std. Dev.":"Std. Dev.","P-Value":"P-Value","Molecule Type":"Molecule_Type"})
                data = data.drop(data[data.Molecule_Type == "METABOLITE"].index)
                data = data.drop(data[data.Molecule_Type == "LIPID"].index)

                counter = 1
                for index, row in data.iterrows():
                    proteins = (row['Molecule Name'].split(';'))
                    genes = []
                    for i in proteins:
                        genes.append(i.split("_")[0])

                    print(genes)

                    unique = "Yes"

                    if len(proteins) > 1:
                        unique = "No"

                    for g in range(len(genes)):
                        try:
                            if genes[g][0] == "Y":
                                protein_data = self.get_protein_data(genes[g])
                                self.data.full_data[protein_data[7]] = Compound(protein_data[7],protein_data[0],row['P-Value'],protein_data[1],protein_data[2],protein_data[3],row['∆LFQ'],"https://beta.uniprot.org/uniprotkb/" + self.Get_protein_ID_from_genename(genes[g]).strip() + "/entry",protein_data[4],protein_data[5],protein_data[6],genes[g],unique)
                            else:
                                if "UNDEF" not in genes[g]:
                                    self.excluded.append(genes[g])
                            print(str(counter) + "/" + str(len(data)))
                            counter += 1
                        except:
                            self.excluded.append(protein_data[7])
                            print(str(counter) + "/" + str(len(data)))
                            counter += 1

                with open(filepath.replace('.csv','') + '.pickle', 'wb') as handle:
                    pickle.dump(self.data.full_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

                with open(filepath.replace('.csv','') + '.txt', 'w') as f:
                    for i in self.excluded:
                        f.write(i+'\n')

        except:
            pass
        self.load_proteins_tree()
        self.load_lists()


    def load_data_from_csv(self):
        self.data.full_data = {}
        try:
            filepath = fd.askopenfilename()
            self.file_name = filepath
            if filepath:
                #FORMAT CSV
                data = pd.read_csv(filepath)
                data = data.rename(columns={"﻿Molecule Name":"﻿Molecule Name","∆LFQ":"∆LFQ","Std. Dev.":"Std. Dev.","P-Value":"P-Value","Molecule Type":"Molecule_Type"})
                data = data.drop(data[data.Molecule_Type == "METABOLITE"].index)
                data = data.drop(data[data.Molecule_Type == "LIPID"].index)

                counter = 1
                for index, row in data.iterrows():
                    name = (row['Molecule Name'].split('_'))[0]
                    gene_name = (row['Molecule Name'].split(' '))[1].replace("(","").replace(")","")
                    if ";" in gene_name:
                        genes = gene_name.split(";")
                        gene_names = name.split(";")
                        for g in range(len(genes)):
                            try:
                                protein_data = self.get_protein_data(genes[g])
                                self.data.full_data[gene_names[g]] = Compound(gene_names[g],protein_data[0],row['P-Value'],protein_data[1],protein_data[2],protein_data[3],row['∆LFQ'],"https://beta.uniprot.org/uniprotkb/" + self.Get_protein_ID_from_genename(genes[g]).strip() + "/entry",protein_data[4],protein_data[5],protein_data[6],genes[g],"No")
                                print(str(counter) + "/" + str(len(data)))
                                counter += 1
                            except:
                                self.excluded.append(gene_names[g])
                                print(str(counter) + "/" + str(len(data)))
                                counter += 1



                    else:
                        try:
                            print(str(gene_name) + "55")
                            protein_data = self.get_protein_data(gene_name)
                            self.data.full_data[name] = Compound(name,protein_data[0],row['P-Value'],protein_data[1],protein_data[2],protein_data[3],row['∆LFQ'],"https://beta.uniprot.org/uniprotkb/" + self.Get_protein_ID_from_genename(gene_name).strip() + "/entry",protein_data[4],protein_data[5],protein_data[6],gene_name,"Yes")
                            print(str(counter) + "/" + str(len(data)))
                            counter += 1
                        except:
                            self.excluded.append(name)
                            print(str(counter) + "/" + str(len(data)))
                            counter += 1

                with open(filepath.replace('.csv','') + '.pickle', 'wb') as handle:
                    pickle.dump(self.data.full_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

                with open(filepath.replace('.csv','') + '.txt', 'w') as f:
                    for i in self.excluded:
                        f.write(i+'\n')

        except:
            pass
        self.load_proteins_tree()
        self.load_lists()


    def reload_data(self):
        new_data = {}
        counter = 0
        size = str(len(self.data.full_data))
        for i in self.data.full_data:
            try:
                protein_data = self.get_protein_data_from_url(self.data.full_data[i].web.replace("/entry",".txt"))
                new_data[self.data.full_data[i].name] = Compound(self.data.full_data[i].name,protein_data[0],self.data.full_data[i].p_value,protein_data[1],protein_data[2],protein_data[3],self.data.full_data[i].abundance,self.data.full_data[i].web,protein_data[4],protein_data[5],protein_data[6])
                print(str(counter) + "/" + size)
                counter += 1
            except:
                pass

        self.data.full_data = new_data
        print(len(self.data.full_data))

        self.load_proteins_tree()
        self.load_lists()


    def get_protein_data_from_url(self,url):
        url = url.replace("www","beta")
        name = ""
        locations = []
        MF = []
        BP = []
        C = []
        P = []

        file = urllib.request.urlopen(url)

        checkNext = 0
        full_reaction_got = 0
        full_reaction = ""
        reaction = []
        gene_name = ""

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
            elif "GN   Name" in decoded_line:
                g_n = decoded_line.split(";")[0]
                gene_name = g_n.split("=")[1]
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
                reaction.append(split_semicolon[0])
                full_reaction = ""
                if " to " in split_semicolon[0]:
                    full_reaction_got = 0
                elif " = " in split_semicolon[0]:
                    split_eq = split_semicolon[0].split(' = ')
                    C = split_eq[0].split(' + ')
                    P = split_eq[1].split(' + ')
                    full_reaction_got = 0
                else:
                    full_reaction_got = 0

        if type(P) == str:
            P = [P]

        if type(C) == str:
            C = [C]


        C = list(dict.fromkeys(C))
        P = list(dict.fromkeys(P))


        return [name,locations,MF,BP,C,P,reaction,gene_name]




    def Get_protein_ID_from_genename(self,gene_name):
        mg = mygene.MyGeneInfo()
        return mg.getgene(gene_name)['uniprot']['Swiss-Prot']

    def get_protein_data(self,gene_name):
        print(gene_name)
        protein_ID = self.Get_protein_ID_from_genename(gene_name)
        print(protein_ID)


        name = ""
        locations = []
        MF = []
        BP = []
        C = []
        P = []

        url = "https://rest.uniprot.org/uniprotkb/" + protein_ID.strip() + ".txt"
        file = urllib.request.urlopen(url)

        checkNext = 0
        full_reaction_got = 0
        full_reaction = ""
        reaction = []
        gene_name = ""

        #for line in file:
            #print(line.decode("utf-8"))

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
            elif "GN   Name" in decoded_line:
                g_n = decoded_line.split(";")[0]
                gene_name = g_n.split("=")[1]
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
                reaction.append(split_semicolon[0])
                full_reaction = ""
                if " to " in split_semicolon[0]:
                    full_reaction_got = 0
                elif " = " in split_semicolon[0]:

                    split_eq = split_semicolon[0].split(' = ')
                    C = split_eq[0].split(' + ')
                    P = split_eq[1].split(' + ')
                    full_reaction_got = 0
                else:

                    full_reaction_got = 0

        if type(P) == str:
            P = [P]

        if type(C) == str:
            C = [C]

        C = list(dict.fromkeys(C))
        P = list(dict.fromkeys(P))

        return [name,locations,MF,BP,C,P,reaction,gene_name]




    def load_data_from_pickle(self):
        try:
            filepath = fd.askopenfilename()
            self.file_name = filepath
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
            self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].unique, self.data.full_data[i].protein_name, self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
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
                        self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].unique, self.data.full_data[i].protein_name, self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
                        counter += 1
            elif selected["values"][0] == 'Molecular Function':
                counter = 0
                for i in self.data.full_data:
                    if selected2["values"][0] in self.data.full_data[i].molecular_function:
                        self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].unique, self.data.full_data[i].protein_name, self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
                        counter += 1
            elif selected["values"][0] == 'Biological Process':
                counter = 0
                for i in self.data.full_data:
                    if selected2["values"][0] in self.data.full_data[i].biological_process:
                        self.proteins_tree.insert(parent='', index=counter, values=(self.data.full_data[i].unique, self.data.full_data[i].protein_name, self.data.full_data[i].name, self.data.full_data[i].recomended_name, self.data.full_data[i].abundance, self.data.full_data[i].p_value))
                        counter += 1
        except:
            self.load_proteins_tree()








#
