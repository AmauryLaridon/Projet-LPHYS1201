import math
import scipy

#CLASSE DECRIVANT LES DONNEES D UN ETAGE
class Stage:
    def __init__(self, M_vide, M_fuel, P, C_A, C, name):
        self.M_vide   = M_vide
        self.M_fuel   = M_fuel
        self.P        = P
        self.C_A      = C_A
        self.C        = C
        self.name     = name
#CLASSE DECRIVANT LA FUSEE UTILISEE
class Fusee :
    def __init__(self):
        self.M        = 0
        self.P        = 0
        self.C_A      = 0
        self.C        = 0
        self.stage    =[]

    def ajouter_module(self, M_vide, M_fuel, P, C_A, C, stage_name):
        new_stage = Stage( M_vide, M_fuel, P, C_A, C, stage_name)
        self.stage.append(new_stage)
        self.M += new_stage.M_vide + new.stage.M_fuel

    def Update(self):
        pass

    def launch(self, position, environnement):

    def convert(self):
        pass
    def affichage(self):
        pass
