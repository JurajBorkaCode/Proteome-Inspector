class Compound:
    def __init__(self,Name,Recomended_Name,p_value,Cellular_Component,Molecular_Function,Biological_Process,Abundance,web,consume,produce,reaction):
        self.name = Name
        self.recomended_name = Recomended_Name
        self.p_value = p_value
        self.cellular_component = Cellular_Component
        self.molecular_function = Molecular_Function
        self.biological_process = Biological_Process
        self.abundance = Abundance
        self.consumes = consume
        self.produces = produce
        self.web = web
        self.reaction = reaction

    def info(self):
        print("| " + self.name)
        print("| " + self.recomended_name)
        print("| P-Value - " + str(self.p_value))

        for i in self.cellular_component:
            print("| Cellular Component - " + i)

        for i in self.molecular_function:
            print("| Molecular Function - " + i)

        for i in self.biological_process:
            print("| Biological Process - " + i)

        print("| Abundance - " + str(self.abundance))
        print("| " + self.web)

    def get_reactions(self):
        out = ""
        for i in self.reaction:
            out += i + "\n\n"

        return out






        #
