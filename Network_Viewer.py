import tkinter as tk
import tkinter.ttk as ttk
import networkx as nx
import webbrowser
import pandas as pd
import os
import networkx as nx
import copy
from pyvis.network import Network
import webbrowser

from SuperClass import SuperClass

class Network_Viewer(SuperClass):
    def __init__(self,parent,title,network,data):
        self.network = network
        self.data = data
        self.type = title
        self.layers = {}

        self.submit = False
        self.proteins = []

        super().__init__(parent, title, width = 1500, height = 800, take_focus=True, extendable=False)


    def body(self, frame):
        self.info_frame = ttk.LabelFrame(self, text="Network Info")
        self.info_frame.pack()

        self.network_nodes = tk.Label(self.info_frame, text="Nodes: " + str(self.network.number_of_nodes()))
        self.network_nodes.grid(row=0, column=0)

        self.network_edges = tk.Label(self.info_frame, text="Edges: " + str(self.network.number_of_edges()))
        self.network_edges.grid(row=0, column=1)

        self.entry_frame = ttk.LabelFrame(self, text="Input")
        self.entry_frame.pack()

        self.start_pro = tk.StringVar()
        self.end_pro = tk.StringVar()
        self.max_length = tk.StringVar()

        self.start_lbl = tk.Label(self.entry_frame, text="Start Protein")
        self.start_lbl.grid(row=0, column=0)

        self.start_entry = tk.Entry(self.entry_frame, textvariable=self.start_pro)
        self.start_entry.grid(row=0, column=1)

        self.end_lbl = tk.Label(self.entry_frame, text="End Protein")
        self.end_lbl.grid(row=0, column=2)

        self.end_entry = tk.Entry(self.entry_frame, textvariable=self.end_pro)
        self.end_entry.grid(row=0, column=3)

        self.max_length_lbl = tk.Label(self.entry_frame, text="Max Length")
        self.max_length_lbl.grid(row=0, column=4)

        self.max_length_entry = tk.Entry(self.entry_frame, textvariable=self.max_length)
        self.max_length_entry.grid(row=0, column=5)

        self.include_edge = tk.IntVar()
        self.include_edge_check = tk.Checkbutton(self.entry_frame, text="Include Edge Labels", variable = self.include_edge, onvalue = 1, offvalue = 0)
        self.include_edge_check.grid(row=0, column=6)

        self.include_abundance = tk.IntVar()
        self.include_abundance_check = tk.Checkbutton(self.entry_frame, text="Include Abundance", variable = self.include_abundance, onvalue = 1, offvalue = 0)
        self.include_abundance_check.grid(row=0, column=7)

        self.search_btn = tk.Button(self.entry_frame, command=self.search_net, text="Search")
        self.search_btn.grid(row=0, column=8)

        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack()

        self.network_scrollbar = ttk.Scrollbar(self.tree_frame)
        self.network_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.path_tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.network_scrollbar.set, height=32)
        self.path_tree['columns'] = ('Path')
        self.path_tree.pack()

        self.path_tree.column('#0',width=0,stretch='NO')
        self.path_tree.column('Path',width=1450)

        self.path_tree.heading('#0', text='')
        self.path_tree.heading('Path', text='Path')

        self.network_scrollbar.config(command = self.path_tree.yview)


    def buttonbox(self):
        self.btn_cancel = ttk.Button(self, text='Cancel', width=10, command=self.cancel)
        self.btn_cancel.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_back = ttk.Button(self, text='Path Info', width=10, command=self.path_info)
        self.btn_back.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_extract = ttk.Button(self, text='Extract Data', width=15, command=self.extract_data)
        self.btn_extract.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_network = ttk.Button(self, text='Network', width=10, command=self.paths_network)
        self.btn_network.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_short_network = ttk.Button(self, text='Shortest Paths', width=20, command=self.paths_short_network)
        self.btn_short_network.pack(side="right", padx=(5,10), pady=(5,10))

    def paths_short_network(self):
        G = nx.Graph()
        start = str(self.start_pro.get()).upper()
        end = str(self.end_pro.get()).upper()

        counter = 1

        for i in self.layers:
            for x in self.layers[i]:
                shape_ = "dot"
                mass_ = 1
                physics_ = True
                size_ = 1
                level_ = 0
                print(x)
                print(start)
                print(end)
                if x == start or x == end:
                    shape_ = "diamond"
                    mass = 4
                    physics_ = False
                    size_ = 20
                else:
                    shape_ = "dot"
                    mass_ = 1
                    physics_ = True
                    size_ = 10

                try:
                    float(self.data[x].abundance)
                except:
                    self.data[x].abundance = 0

                if float(self.data[x].abundance) < 0:
                    if float(self.data[x].p_value) < 0.05:
                        G.add_node(self.data[x].name,label = self.data[x].name, color="#c91010",shape=shape_, mass=mass_, physics=physics_, size=size_, level=(int(i)+1))
                    else:
                        G.add_node(self.data[x].name,label = self.data[x].name, color="#f2a7a7",shape=shape_, mass=mass_, physics=physics_, size=size_, level=(int(i)+1))

                elif float(self.data[x].abundance) > 0:
                    if float(self.data[x].p_value) < 0.05:
                        G.add_node(self.data[x].name,label = self.data[x].name, color="#0f8c31",shape=shape_, mass=mass_, physics=physics_, size=size_, level=(int(i)+1))
                    else:
                        G.add_node(self.data[x].name,label = self.data[x].name, color="#bbf2c2",shape=shape_, mass=mass_, physics=physics_, size=size_, level=(int(i)+1))
                else:
                    G.add_node(self.data[x].name,label = self.data[x].name, color="#a0a0a0",shape=shape_, mass=mass_, physics=physics_, size=size_, level=(int(i)+1))
                counter += 1

        data_1 = []
        data_2 = []

        try:
            for i in self.layers:
                data_1 = self.layers[i]
                data_2 = self.layers[i+1]

                if self.type == "Cellular Component":
                    for i in data_1:
                        for j in self.data[i].cellular_component:
                            for x in data_2:
                                for y in self.data[x].cellular_component:
                                    if j == y:
                                        if G.has_edge(self.data[x].name,self.data[i].name):
                                            pass
                                        elif self.data[x].name == self.data[i].name:
                                            pass
                                        else:
                                            G.add_edge(self.data[i].name,self.data[x].name,title=y)
                elif self.type == "Molecular Function":
                    for i in data_1:
                        for j in self.data[i].molecular_function:
                            for x in data_2:
                                for y in self.data[x].molecular_function:
                                    if j == y:
                                        if G.has_edge(self.data[x].name,self.data[i].name):
                                            pass
                                        elif self.data[x].name == self.data[i].name:
                                            pass
                                        else:
                                            G.add_edge(self.data[i].name,self.data[x].name,title=y)
                elif self.type == "Biological Process":
                    for i in data_1:
                        for j in self.data[i].biological_process:
                            for x in data_2:
                                for y in self.data[x].biological_process:
                                    if j == y:
                                        if G.has_edge(self.data[x].name,self.data[i].name):
                                            pass
                                        elif self.data[x].name == self.data[i].name:
                                            pass
                                        else:
                                            G.add_edge(self.data[i].name,self.data[x].name,title=y)
        except:
            pass


        vis_net = Network(notebook=True,height=1000,width=1000)
        vis_net.show_buttons(filter_=['physics'])
        vis_net.from_nx(G)
        vis_net.repulsion(central_gravity=2)
        vis_net.show("test"+".html")
        webbrowser.open("test"+".html")



    def paths_network(self):
        G = nx.Graph()
        start = str(self.start_pro.get()).upper()
        end = str(self.end_pro.get()).upper()
        #create nodes
        counter = 1
        for i in self.proteins:
            shape_ = "dot"
            mass_ = 1
            physics_ = True
            size_ = 1
            level_ = 0
            if i == start or i == end:
                shape_ = "diamond"
                mass = 4
                physics_ = False
                size_ = 20
            else:
                shape_ = "dot"
                mass_ = 1
                physics_ = True
                size_ = 10
            for x in self.layers:
                if i in self.layers[x]:
                    level_ = int(x)

            try:
                float(self.data[i].abundance)
            except:
                self.data[i].abundance = 0

            if float(self.data[i].abundance) < 0:
                if float(self.data[i].p_value) < 0.05:
                    G.add_node(self.data[i].name,label = self.data[i].name, color="#c91010",shape=shape_, mass=mass_, physics=physics_, size=size_, level=level_)
                else:
                    G.add_node(self.data[i].name,label = self.data[i].name, color="#f2a7a7",shape=shape_, mass=mass_, physics=physics_, size=size_, level=level_)

            elif float(self.data[i].abundance) > 0:
                if float(self.data[i].p_value) < 0.05:
                    G.add_node(self.data[i].name,label = self.data[i].name, color="#0f8c31",shape=shape_, mass=mass_, physics=physics_, size=size_, level=level_)
                else:
                    G.add_node(self.data[i].name,label = self.data[i].name, color="#bbf2c2",shape=shape_, mass=mass_, physics=physics_, size=size_, level=level_)
            else:
                G.add_node(self.data[x].name,label = self.data[x].name, color="#a0a0a0",shape=shape_, mass=mass_, physics=physics_, size=size_, level=(int(i)+1))

            counter += 1

        #create edges
        if self.type == "Cellular Component":
            for i in self.proteins:
                for j in self.data[i].cellular_component:
                    for x in self.proteins:
                        for y in self.data[x].cellular_component:
                            if j == y:
                                if G.has_edge(self.data[x].name,self.data[i].name):
                                    pass
                                elif self.data[x].name == self.data[i].name:
                                    pass
                                else:
                                    G.add_edge(self.data[i].name,self.data[x].name,title=y)
        elif self.type == "Molecular Function":
            for i in self.proteins:
                for j in self.data[i].molecular_function:
                    for x in self.proteins:
                        for y in self.data[x].molecular_function:
                            if j == y:
                                if G.has_edge(self.data[x].name,self.data[i].name):
                                    pass
                                elif self.data[x].name == self.data[i].name:
                                    pass
                                else:
                                    G.add_edge(self.data[i].name,self.data[x].name,title=y)
        elif self.type == "Biological Process":
            for i in self.proteins:
                for j in self.data[i].biological_process:
                    for x in self.proteins:
                        for y in self.data[x].biological_process:
                            if j == y:
                                if G.has_edge(self.data[x].name,self.data[i].name):
                                    pass
                                elif self.data[x].name == self.data[i].name:
                                    pass
                                else:
                                    G.add_edge(self.data[i].name,self.data[x].name,title=y)


        print(list(G.nodes))
        print(list(G.edges))

        vis_net = Network(notebook=True,height=1000,width=1000)
        vis_net.show_buttons(filter_=['physics'])
        vis_net.from_nx(G)
        vis_net.repulsion(central_gravity=2)
        vis_net.show("test"+".html")
        webbrowser.open("test"+".html")



    def extract_data(self):
        try:
            max_len = int(self.max_length.get())
            start = str(self.start_pro.get())
            end = str(self.end_pro.get())
            out_data = {}
            for i in range(max_len):
                out_data["Protein " + str(i+1)] = []
                out_data["Connection " + str(i+1)] = []
            out_data["Protein " + str(max_len+1)] = []
            out_data["Viability (0.05)"] = []
            out_data["Largest P-Value"] = []
            for path in nx.all_simple_paths(self.network,start.upper(),end.upper(),max_len):
                counter1 = 0
                viable = 1
                largest_p_value = 0
                for i in range(len(path)):
                    if float(self.data[path[counter1]].p_value) > float(0.05):
                        viable = 0
                    if float(self.data[path[counter1]].p_value) > float(largest_p_value):
                        largest_p_value = float(self.data[path[counter1]].p_value)
                    out_data["Protein " + str(i+1)].append(str(path[counter1]) + " (" + str(self.data[path[counter1]].p_value) + ")")
                    try:
                        out_data["Connection " + str(i+1)].append(self.network[path[counter1]][path[counter1+1]]["label"])
                    except:
                        pass
                    counter1 += 1
                out_data["Viability (0.05)"].append(str(viable))
                out_data["Largest P-Value"].append(str(largest_p_value))


            out_df = pd.DataFrame(data=out_data)
            out_df.to_csv("net_out.csv", index=False)
            os.system("start EXCEL.EXE net_out.csv")



        except:
            pass


    def path_info(self):
        selected = self.path_tree.item(self.path_tree.focus())
        protein_path = selected["values"][0].split()

        for protein in protein_path:
            print(protein)
            try:
                print(self.data[protein].web)
                webbrowser.open(self.data[protein].web)
            except:
                pass




    def search_net(self):
        self.path_tree.delete(*self.path_tree.get_children())
        start = str(self.start_pro.get())
        end = str(self.end_pro.get())
        max_len = int(self.max_length.get())
        edge_labels = self.include_edge.get()
        abundance_labels = self.include_abundance.get()

        counter = 0
        if self.network.has_node(start.upper()) and self.network.has_node(end.upper()):
            for path in nx.all_simple_paths(self.network,start.upper(),end.upper(),max_len):
                counter1 = 0
                out_string = ""
                try:
                    for i in range(len(path)):
                        self.proteins.append(path[counter1])
                        if i in self.layers.keys():
                            self.layers[i].append(path[counter1])
                        else:
                            self.layers[i] = [path[counter1]]

                        if abundance_labels == 1:
                            out_string += path[counter1] + "[" + str(self.network.nodes[path[counter1]]["abundance"]) + "]"
                        else:
                            out_string += path[counter1]

                        if edge_labels == 1:
                            out_string += " ---[" + self.network[path[counter1]][path[counter1+1]]["label"] + "]--- "
                        else:
                            out_string += " --- "
                        counter1 += 1
                except:
                    pass
                if out_string.endswith("--- "):
                    out_string = out_string[:-5]
                out_string = out_string.replace(' ', '\ ')
                self.path_tree.insert(parent='', index=counter, values=(out_string))
                counter += 1

        self.proteins = list(dict.fromkeys(self.proteins))
        for i in self.layers:
            self.layers[i] = list(dict.fromkeys(self.layers[i]))
        print(self.proteins)
        print(self.layers)
















        #
