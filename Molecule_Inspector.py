import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from collections import OrderedDict
import webbrowser
import pandas as pd
import os

from SuperClass import SuperClass
from Add_Filter_Dialog import Add_Filter_Dialog

class Molecule_Inspector(SuperClass):
    def __init__(self,parent,title,data):
        self.data = data
        self.molecule_list = []

        self.submit = False
        self.filters = {"Cellular Component":[],"Molecular Function":[],"Biological Process":[]}

        super().__init__(parent, title, width = 970, height = 800, take_focus=True, extendable=False)


    def body(self, frame):
        self.split_frame = ttk.Frame(frame,padding=5)
        self.split_frame.pack()

        self.vertical_split_frame = tk.Frame(self.split_frame)
        self.vertical_split_frame.pack(side=tk.LEFT)

        self.protein_info_frame = tk.Frame(self.vertical_split_frame)
        self.protein_info_frame.pack()

        self.protein_info_scrollbar = ttk.Scrollbar(self.protein_info_frame)
        self.protein_info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.protein_tree_frame = tk.Frame(self.protein_info_frame)
        self.protein_tree_frame.pack(side=tk.LEFT)

        self.protein_tree = ttk.Treeview(self.protein_tree_frame, yscrollcommand=self.protein_info_scrollbar.set, height=30)
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

        self.protein_tree.bind('<<TreeviewSelect>>',lambda event: self.update_reaction())

        self.protein_info_scrollbar.config(command = self.protein_tree.yview)

        self.protein_reaction_frame = tk.Frame(self.vertical_split_frame)
        self.protein_reaction_frame.pack()

        self.reaction_scroll = ttk.Scrollbar(self.protein_reaction_frame)
        self.reaction_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.protein_reaction_text = tk.Text(self.protein_reaction_frame,width=94,height=7, wrap=tk.WORD)
        self.protein_reaction_text.pack(expand=True, side=tk.LEFT)

        self.protein_reaction_text.config(yscrollcommand=self.reaction_scroll.set, state="disabled")
        self.reaction_scroll.config(command=self.protein_reaction_text.yview)

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



    def update_reaction(self):
        selected = self.protein_tree.item(self.protein_tree.focus())["values"][0]
        self.protein_reaction_text.config(state="normal")
        self.protein_reaction_text.delete("1.0","end-1c")
        self.protein_reaction_text.insert(tk.END, self.data[selected].get_reactions())
        self.protein_reaction_text.config(state="disabled")


    def check_filters(self,protein):
        filter_out = True
        if self.filters == {'Cellular Component': [], 'Molecular Function': [], 'Biological Process': []}:
            filter_out = False

        if self.filters["Cellular Component"] != []:
            for x in self.data[protein].cellular_component:
                if self.filters["Cellular Component"][0].upper() in x.upper():
                    filter_out = False

        if self.filters["Molecular Function"] != []:
            for x in self.data[protein].molecular_function:
                if self.filters["Molecular Function"][0] in x:
                    filter_out = False


        if self.filters["Biological Process"] != []:
            for x in self.data[protein].biological_process:
                if self.filters["Biological_Process"][0] in x:
                    filter_out = False

        if filter_out:
            return 2
        else:
            return 1






    def update_selected(self):
        try:
            self.protein_tree.delete(*self.protein_tree.get_children())
            selected = self.molecule_tree.item(self.molecule_tree.focus())['values'][0]
            counter = 0
            for i in self.data:
                check = self.check_filters(self.data[i].name)
                if selected in self.data[i].consumes and check == 1:
                    self.protein_tree.insert(parent='', index=counter, values=(self.data[i].name, self.data[i].recomended_name, self.data[i].abundance, self.data[i].p_value), tags="consumes")
                    counter +=1
                elif selected in self.data[i].produces and check == 1:
                    self.protein_tree.insert(parent='', index=counter, values=(self.data[i].name, self.data[i].recomended_name, self.data[i].abundance, self.data[i].p_value), tags="produces")
                    counter +=1
                elif (selected not in self.data[i].produces) and check == 1 and (selected not in self.data[i].consumes) and (" " + selected + " " in self.data[i].reaction):
                    self.protein_tree.insert(parent='', index=counter, values=(self.data[i].name, self.data[i].recomended_name, self.data[i].abundance, self.data[i].p_value), tags="N_A")
                    counter +=1

            self.protein_tree.tag_configure('consumes', foreground="red")
            self.protein_tree.tag_configure('produces', foreground="green")
            self.protein_tree.tag_configure('N_A', foreground="black")
            self.protein_reaction_text.config(state="normal")
            self.protein_reaction_text.delete("1.0","end-1c")
            self.protein_reaction_text.config(state="disabled")
        except:
            pass






    def buttonbox(self):
        self.cancel_btn = ttk.Button(self, text='Cancel', width=10, command=self.cancel)
        self.cancel_btn.pack(side="right", padx=(5,10), pady=(5,10))
        self.back_btn = ttk.Button(self, text='Protein Info', width=15, command=self.protein_info)
        self.back_btn.pack(side="right", padx=(5,10), pady=(5,10))
        self.extract_btn = ttk.Button(self, text='Extract', width=15, command=self.extract_data_to_csv)
        self.extract_btn.pack(side="right", padx=(5,10), pady=(5,10))
        self.remove_filter_btn = ttk.Button(self, text='Remove Filter', width=20, command=self.remove_filter)
        self.remove_filter_btn.pack(side="right", padx=(5,10), pady=(5,10))
        self.add_filter_btn = ttk.Button(self, text='Add Filter', width=20, command=self.add_filter)
        self.add_filter_btn.pack(side="right", padx=(5,10), pady=(5,10))

    def extract_data_to_csv(self):
        print(1)
        out_data = {"Protein ID" : [],"Protein Name" : [],"Abundance" : [],"P-Value" : [],"status" : []}
        for line in self.protein_tree.get_children():
            out_data["Protein ID"].append(self.protein_tree.item(line)['values'][0])
            out_data["Protein Name"].append(self.protein_tree.item(line)['values'][1])
            out_data["Abundance"].append(self.protein_tree.item(line)['values'][2])
            out_data["P-Value"].append(self.protein_tree.item(line)['values'][3])
            out_data["status"].append(self.protein_tree.item(line)['tags'][0])

        out_df = pd.DataFrame(data=out_data)

        out_df.to_csv("out.csv", index=False)
        os.system("start EXCEL.EXE out.csv")



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



    def add_filter(self):
        a = Add_Filter_Dialog(self,"Add Filter",self.data)
        if a.submit == True:
            self.filters = a.filters
            print(self.filters)




    def remove_filter(self):
        pass



















        #
