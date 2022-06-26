import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from collections import OrderedDict
import webbrowser

from SuperClass import SuperClass

class Molecule_Inspector(SuperClass):
    def __init__(self,parent,title,data):
        self.data = data
        self.molecule_list = []

        self.submit = False

        super().__init__(parent, title, width = 970, height = 800, take_focus=True, extendable=False)


    def body(self, frame):
        self.split_frame = ttk.Frame(frame,padding=5)
        self.split_frame.pack()

        self.protein_info_frame = tk.Frame(self.split_frame)
        self.protein_info_frame.pack(side=tk.LEFT)

        self.protein_info_scrollbar = ttk.Scrollbar(self.protein_info_frame)
        self.protein_info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.protein_tree_frame = tk.Frame(self.protein_info_frame)
        self.protein_tree_frame.pack(side=tk.LEFT)

        self.protein_tree = ttk.Treeview(self.protein_tree_frame, yscrollcommand=self.protein_info_scrollbar.set, height=36)
        self.protein_tree['columns'] = ('Name', 'Full Name', 'Abundance', 'P-Value')
        self.protein_tree.pack()

        self.protein_tree.column('#0',width=0,stretch='NO')
        self.protein_tree.column('Name',width=80)
        self.protein_tree.column('Full Name',width=500)
        self.protein_tree.column('Abundance',width=80)
        self.protein_tree.column('P-Value',width=90)

        self.protein_tree.heading('#0', text='')
        self.protein_tree.heading('Name', text='Name')
        self.protein_tree.heading('Full Name', text='Full Name')
        self.protein_tree.heading('Abundance', text='Abundance')
        self.protein_tree.heading('P-Value', text='P-Value')

        self.protein_info_scrollbar.config(command = self.protein_tree.yview)

        self.query_frame = tk.Frame(self.split_frame)
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



    def update_selected(self):
        try:
            self.protein_tree.delete(*self.protein_tree.get_children())
            selected = self.molecule_tree.item(self.molecule_tree.focus())['values'][0]
            counter = 0
            for i in self.data:
                if selected in self.data[i].consumes:
                    self.protein_tree.insert(parent='', index=counter, values=(self.data[i].name, self.data[i].recomended_name, self.data[i].abundance, self.data[i].p_value), tags="consumes")
                    counter +=1
                elif selected in self.data[i].produces:
                    self.protein_tree.insert(parent='', index=counter, values=(self.data[i].name, self.data[i].recomended_name, self.data[i].abundance, self.data[i].p_value), tags="produces")
                    counter +=1

            self.protein_tree.tag_configure('consumes', foreground="red")
            self.protein_tree.tag_configure('produces', foreground="green")
        except:
            pass






    def buttonbox(self):
        self.btn_cancel = ttk.Button(self, text='Cancel', width=10, command=self.cancel)
        self.btn_cancel.pack(side="right", padx=(5,10), pady=(5,10))
        self.btn_back = ttk.Button(self, text='Protein Info', width=15, command=self.protein_info)
        self.btn_back.pack(side="right", padx=(5,10), pady=(5,10))


    def protein_info(self):
        selected = self.protein_tree.item(self.protein_tree.focus())['values'][0]
        webbrowser.open(self.data[selected].web)

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