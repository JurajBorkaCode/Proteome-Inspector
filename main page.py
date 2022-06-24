import urllib.parse
import urllib.request

import pickle
import threading
import pandas as pd

import tkinter as tk


from compound import Compound

from window import MainView

def options(data_dict):
    print("###############################")
    print("# 1 - import data from csv    #")
    print("# 2 - import data from pickle #")
    print("# 3 - look at data            #")
    print("# 4 - sort data               #")
    print("# 5 - filter data             #")
    print("# 6 - look at protein         #")
    print("# 7 - save                    #")
    print("###############################")

    option = int(input())
    if option == 1:
        load_data_from_csv()
    elif option == 2:
        with open('processed_data.pickle', 'rb') as handle:
            data_dict = pickle.load(handle)
    elif option == 3:
        for i in data_dict:
            print("| " + i)
    elif option == 4:
        print("##################")
        print("#   Sort Types   #")
        print("##################")
        print("# 1 #    Name    #")
        print("# 2 #   P-Value  #")
        print("# 3 #  Abundance #")
        print("##################")
        sort_by = input(" sort by: ")

    elif option == 5:
        print("##########################")
        print("#      Filter Types      #")
        print("##########################")
        print("# 1 #   Above P-Value    #")
        print("# 2 #   Below P-Value    #")
        print("# 3 #  Above Abundance   #")
        print("# 4 #  Below Abundance   #")
        print("# 5 # Cellular Component #")
        print("# 6 # Molecular Function #")
        print("# 7 # Biological Process #")
        print("##########################")
        filter_type = input(" filter by: ")
        print("##########################")
        filter_con = input(" filter condition: ")
        print("##########################")
        filter_dict(filter_type,filter_con)


    elif option == 6:
        protein_lookup = input("protein ID: ")
        print("###############################")
        data_dict[protein_lookup].info()

    elif option == 7:
        with open('processed_data.pickle', 'wb') as handle:
            pickle.dump(data_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return data_dict


def sort_dict(type):
    pass

def filter_dict(type,con):
    for i in data_dict:
        if type == "1":
            if float(data_dict[i].p_value) > float(con):
                print("| " + data_dict[i].name)
        elif type == "2":
            if float(data_dict[i].p_value) < float(con):
                print("| " + data_dict[i].name)
        elif type == "3":
            if float(data_dict[i].abundance) > float(con):
                print("| " + data_dict[i].name)
        elif type == "4":
            if float(data_dict[i].abundance) < float(con):
                print("| " + data_dict[i].name)
        elif type == "5":
            if con in data_dict[i].cellular_component:
                print("| " + data_dict[i].name)
        elif type == "6":
            if con in data_dict[i].molecular_function:
                print("| " + data_dict[i].name)
        elif type == "7":
            if con in data_dict[i].biological_process:
                print("| " + data_dict[i].name)








def load_data_from_csv():
    file = input("input the CSV file location: ")
    data = pd.read_csv(file)
    data = data.rename(columns={"﻿Molecule Name":"﻿Molecule Name","∆LFQ":"∆LFQ","Std. Dev.":"Std. Dev.","P-Value":"P-Value","Molecule Type":"Molecule_Type"})
    data = data.drop(data[data.Molecule_Type == "METABOLITE"].index)

    for index, row in data.iterrows():
        name = (row['Molecule Name'].split(' '))[0]
        try:
            protein_data = get_protein_data(name)
            data_dict[name] = Compound(name,protein_data[0],row['P-Value'],protein_data[1],protein_data[2],protein_data[3],row['∆LFQ'],"https://beta.uniprot.org/uniprotkb/" + Get_protein_ID_from_genename(name).strip() + "/entry")
            print("| " + name + " added")
        except:
            print(name + " not found")

    with open('processed_data.pickle', 'wb') as handle:
        pickle.dump(data_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)





def Get_protein_ID_from_genename(gene_name):
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

def get_protein_data(gene_name):
    protein_ID = Get_protein_ID_from_genename(gene_name)
    name = ""
    locations = []
    MF = []
    BP = []


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

    return [name,locations,MF,BP]


data = None
data_dict = {}

print(1)


def main():
    MainView()

main()

print(1)























#
