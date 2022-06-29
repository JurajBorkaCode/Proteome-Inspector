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

class Add_Reaction_Dialog(SuperClass):
    def __init__(self,parent,title,data):
        self.data = data
        self.molecule_list = []
        self.G = nx.Graph()

        self.submit = False


        super().__init__(parent, title, width = 590, height = 500, take_focus=True, extendable=False)


    def body(self, frame):
        self.split_frame = ttk.Frame(frame,padding=5)
        self.split_frame.pack()

        self.edit_frame = tk.Frame(self.split_frame)
        self.edit_frame.pack(side=tk.LEFT)

        self.reaction_description = tk.Text(self.edit_frame,width=45,height=7,state="disabled", wrap=tk.WORD)
        self.reaction_description.pack()

        self.holder_frame = tk.Frame(self.edit_frame)
        self.holder_frame.pack()

        self.consumes_frame = tk.Frame(self.holder_frame)
        self.consumes_frame.pack(side=tk.LEFT)

        self.consumes_tree = ttk.Treeview(self.consumes_frame, height=10)
        self.consumes_tree['columns'] = ('Consumes')
        self.consumes_tree.pack()

        self.consumes_tree.column('#0',width=0,stretch='NO')
        self.consumes_tree.column('Consumes',width=180)

        self.consumes_tree.heading('#0', text='')
        self.consumes_tree.heading('Consumes', text='Consumes')

        self.consumes_txt = tk.StringVar()
        self.consumes_entry = ttk.Entry(self.consumes_frame, font=("Calibri 12"), textvariable = self.consumes_txt, width=10)
        self.consumes_entry.pack(fill=tk.X)

        self.add_consumes_button = tk.Button(self.consumes_frame, text="Add", command=self.add_consumes)
        self.add_consumes_button.pack(fill=tk.X)

        self.remove_consumes_button = tk.Button(self.consumes_frame, text="Remove", command=self.remove_consumes)
        self.remove_consumes_button.pack(fill=tk.X)





        self.produces_frame = tk.Frame(self.holder_frame)
        self.produces_frame.pack(side=tk.RIGHT)

        self.produces_tree = ttk.Treeview(self.produces_frame, height=10)
        self.produces_tree['columns'] = ('Produces')
        self.produces_tree.pack()

        self.produces_tree.column('#0',width=0,stretch='NO')
        self.produces_tree.column('Produces',width=180)

        self.produces_tree.heading('#0', text='')
        self.produces_tree.heading('Produces', text='Produces')

        self.produces_txt = tk.StringVar()
        self.produces_entry = ttk.Entry(self.produces_frame, font=("Calibri 12"), textvariable = self.produces_txt, width=10)
        self.produces_entry.pack(fill=tk.X)

        self.add_produces_button = tk.Button(self.produces_frame, text="Add", command=self.add_produces)
        self.add_produces_button.pack(fill=tk.X)

        self.remove_produces_button = tk.Button(self.produces_frame, text="Remove", command=self.remove_produces)
        self.remove_produces_button.pack(fill=tk.X)




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

        self.molecule_tree = ttk.Treeview(self.query_tree_frame, yscrollcommand=self.query_scrollbar.set, height=19)
        self.molecule_tree['columns'] = ('Name')
        self.molecule_tree.pack()

        self.molecule_tree.column('#0',width=0,stretch='NO')
        self.molecule_tree.column('Name',width=180)

        self.molecule_tree.heading('#0', text='')
        self.molecule_tree.heading('Name', text='Name')

        self.molecule_tree.bind('<<TreeviewSelect>>',lambda event: self.update_selected())

        self.query_scrollbar.config(command = self.molecule_tree.yview)

        self.init_molecule_tree()



    def add_consumes(self):
        selected_protein = self.molecule_tree.item(self.molecule_tree.focus())["values"][0]
        self.data[selected_protein].consumes.append(self.consumes_txt.get())
        self.update_selected()

    def remove_consumes(self):
        selected_consumes = self.consumes_tree.item(self.consumes_tree.focus())["values"][0]
        selected_protein = self.molecule_tree.item(self.molecule_tree.focus())["values"][0]
        self.data[selected_protein].consumes.remove(selected_consumes)
        self.update_selected()

    def add_produces(self):
        selected_protein = self.molecule_tree.item(self.molecule_tree.focus())["values"][0]
        self.data[selected_protein].produces.append(self.produces_txt.get())
        self.update_selected()

    def remove_produces(self):
        selected_produces = self.produces_tree.item(self.produces_tree.focus())["values"][0]
        selected_protein = self.molecule_tree.item(self.molecule_tree.focus())["values"][0]
        self.data[selected_protein].produces.remove(selected_produces)
        self.update_selected()

    def update_selected(self):
        self.consumes_tree.delete(*self.consumes_tree.get_children())
        self.produces_tree.delete(*self.produces_tree.get_children())

        selected = self.molecule_tree.item(self.molecule_tree.focus())["values"][0]

        self.reaction_description.config(state="normal")
        self.reaction_description.delete("1.0","end-1c")
        self.reaction_description.insert(tk.END, self.data[selected].reaction)
        self.reaction_description.config(state="disabled")

        counter = 0
        for i in self.data[selected].consumes:
            text_to_add = i.replace(' ', '\ ')
            self.consumes_tree.insert(parent='', index=counter, values=(text_to_add))
            counter += 1

        counter = 0
        for i in self.data[selected].produces:
            text_to_add = i.replace(' ', '\ ')
            self.produces_tree.insert(parent='', index=counter, values=(text_to_add))
            counter += 1







    def buttonbox(self):
        self.btn_cancel = ttk.Button(self, text='Cancel', width=10, command=self.cancel)
        self.btn_cancel.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_back = ttk.Button(self, text='Updata data', width=15, command=self.update_data)
        self.btn_back.pack(side="right", padx=(5,10), pady=(5,10))


    def update_data(self):
        self.submit = True
        self.destroy()

    def init_molecule_tree(self):
        counter = 0
        for i in self.data:
            text_to_add = self.data[i].name.replace(' ', '\ ')
            if self.data[i].reaction == "":
                self.molecule_tree.insert(parent='', index=counter, values=(text_to_add), tags="no_reactions")
            elif (self.data[i].reaction != "") and (self.data[i].consumes == []) and (self.data[i].produces == []):
                self.molecule_tree.insert(parent='', index=counter, values=(text_to_add), tags="has_reactions_but_no_molecules")
            else:
                self.molecule_tree.insert(parent='', index=counter, values=(text_to_add), tags="has_reactions")
            counter += 1

        self.molecule_tree.tag_configure('no_reactions', foreground="black")
        self.molecule_tree.tag_configure('has_reactions_but_no_molecules', foreground="red")
        self.molecule_tree.tag_configure('has_reactions', foreground="green")



    def search_molecule_tree(self,var,index,mode):
        self.molecule_tree.delete(*self.molecule_tree.get_children())
        search = self.search.get().upper()

        counter = 0
        for i in self.data:
            if search in self.data[i].name.upper():
                text_to_add = i.replace(' ', '\ ')
                if self.data[i].reaction == "":
                    self.molecule_tree.insert(parent='', index=counter, values=(text_to_add), tags="no_reactions")
                elif (self.data[i].reaction != "") and (self.data[i].consumes == []) and (self.data[i].produces == []):
                    self.molecule_tree.insert(parent='', index=counter, values=(text_to_add), tags="has_reactions_but_no_molecules")
                else:
                    self.molecule_tree.insert(parent='', index=counter, values=(text_to_add), tags="has_reactions")
                counter += 1

        self.molecule_tree.tag_configure('no_reactions', foreground="black")
        self.molecule_tree.tag_configure('has_reactions_but_no_molecules', foreground="red")
        self.molecule_tree.tag_configure('has_reactions', foreground="green")










        #
