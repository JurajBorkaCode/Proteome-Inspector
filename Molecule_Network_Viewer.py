import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from collections import OrderedDict
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import networkx as nx
import copy
from pyvis.network import Network

from SuperClass import SuperClass

class Molecule_Network_Viewer(SuperClass):
    def __init__(self,parent,title,data):
        self.data = data
        self.molecule_list = []
        self.G = nx.Graph()

        self.submit = False


        super().__init__(parent, title, width = 1400, height = 800, take_focus=True, extendable=False)


    def body(self, frame):
        self.split_frame = ttk.Frame(frame,padding=5)
        self.split_frame.pack()

        self.plot_frame = ttk.Frame(self.split_frame)
        self.plot_frame.pack(side=tk.LEFT)

        self.figure = plt.Figure(figsize=(12,12))
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.toolbar_frame = tk.Frame(self.plot_frame)
        self.toolbar_frame.pack(side="top",fill ='x', expand=True)
        NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.canvas.get_tk_widget().pack(side="top", fill ='both', expand=True)
        self.canvas.draw()





        self.query_frame = ttk.Frame(self.split_frame,padding=5)
        self.query_frame.pack(side=tk.LEFT)

        self.search = tk.StringVar()
        self.search.trace_add("write", self.search_molecule_tree)

        self.search_query = ttk.Entry(self.query_frame, font=("Calibri 12"), textvariable = self.search, width=100)
        self.search_query.pack(side=tk.TOP)

        self.query_tree_split_frame = tk.Frame(self.query_frame)
        self.query_tree_split_frame.pack(side=tk.TOP)

        self.query_scrollbar = ttk.Scrollbar(self.query_tree_split_frame)
        self.query_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.query_tree_frame = tk.Frame(self.query_tree_split_frame)
        self.query_tree_frame.pack(side=tk.LEFT)

        self.molecule_tree = ttk.Treeview(self.query_tree_frame, yscrollcommand=self.query_scrollbar.set, height=34)
        self.molecule_tree['columns'] = ('Name')
        self.molecule_tree.pack()

        self.molecule_tree.column('#0',width=0,stretch='NO')
        self.molecule_tree.column('Name',width=180)

        self.molecule_tree.heading('#0', text='')
        self.molecule_tree.heading('Name', text='Name')

        self.molecule_tree.bind('<<TreeviewSelect>>',lambda event: self.update_selected())

        self.query_scrollbar.config(command = self.molecule_tree.yview)

        self.init_molecule_tree()
        self.create_net()



    def create_net(self):
        for i in self.molecule_list:
            self.G.add_node(i)

        for i in self.data:
            for j in self.data[i].consumes:
                for x in self.data[i].produces:
                    self.G.add_edge(j,x,title=self.data[i].name)



    def update_selected(self):
        selected = self.molecule_tree.item(self.molecule_tree.focus())["values"][0]

        net = copy.deepcopy(self.G)

        for i in self.molecule_list:
            if nx.has_path(net,selected,i) == 0:
                    net.remove_node(i)

        nx.draw_networkx(net,ax=self.axis)
        xlim=self.axis.get_xlim()
        ylim=self.axis.get_ylim()

        focus = {selected: {"color":"red"}}
        nx.set_node_attributes(net,focus)

        vis_net = Network(notebook=True,height=1000,width=1000)
        vis_net.barnes_hut()
        vis_net.show_buttons(filter_=['physics'])
        vis_net.from_nx(net)
        vis_net.show(selected+".html")





    def buttonbox(self):
        self.btn_cancel = ttk.Button(self, text='Cancel', width=10, command=self.cancel)
        self.btn_cancel.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_back = ttk.Button(self, text='Protein Info', width=15, command=self.protein_info)
        self.btn_back.pack(side="right", padx=(5,10), pady=(5,10))


    def protein_info(self):
        pass

    def init_molecule_tree(self):
        for i in self.data:
            self.molecule_list.extend(self.data[i].consumes)
            self.molecule_list.extend(self.data[i].produces)

        self.molecule_list = list(OrderedDict.fromkeys(self.molecule_list))

        counter = 0
        for i in self.molecule_list:
            text_to_add = i.replace(' ', '\ ')
            self.molecule_tree.insert(parent='', index=counter, values=(text_to_add))
            counter += 1


    def search_molecule_tree(self,var,index,mode):
        self.molecule_tree.delete(*self.molecule_tree.get_children())
        search = self.search.get().upper()

        counter = 0
        for i in self.molecule_list:
            if search in i.upper():
                text_to_add = i.replace(' ', '\ ')
                self.molecule_tree.insert(parent='', index=counter, values=(text_to_add))
                counter += 1












        #
