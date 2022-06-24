import tkinter as tk
import tkinter.ttk as ttk
import networkx as nx
import webbrowser

from SuperClass import SuperClass

class Network_Viewer(SuperClass):
    def __init__(self,parent,title,network,data):
        self.network = network
        self.data = data

        self.submit = False

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


















        #
