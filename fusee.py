import math
import scipy
import numpy as np
from copy import copy, deepcopy

from environnement import *

txt_to_print = "------------------------------------------------------------------------------------"
txt_to_print2 = "  "
#--------------------------CLASSE DECRIVANT LES DONNEES D UN ETAGE-----------------------#
class Stage:
    def __init__(self, type, name, M_empty, M_fuel, P, C_A, C):
        self.type     = type
        self.M_empty  = M_empty
        self.M_fuel   = M_fuel
        self.P        = P
        self.C_A      = C_A
        self.C        = C
        self.name     = name
        self.M_total  = M_empty + M_fuel


#-----------------------------CLASSE DECRIVANT LA FUSEE UTILISEE---------------------------#
class Rocket:
    def __init__(self):
        self.M               = 0
        self.M_fuel_rocket   = 0
        self.P               = 0
        self.C_A             = 0
        self.C               = 0
        self.C_boost         = 0
        self.stage           =[]
#-------------------------------FONCTIONS LIEES A LA FUSEE---------------------------------#
    def add_stage(self, stage_type, stage_name, M_empty, M_fuel, P, C_A, C):
        """ajoute une étage à la fusée en partant de la charge utile (le haut)"""
        #test des erreurs possibles
        if len(self.stage) == 0:
            if stage_type != 'payload':
                print("La construction de la fusée doit commencer par de placement de la charge utile.")
            else:
                new_stage = Stage(stage_type, stage_name, M_empty, M_fuel, P, C_A, C)
                self.stage.append(new_stage)
                self.M += new_stage.M_empty + new_stage.M_fuel

        elif self.stage[-1].type != 'payload' and stage_type == 'payload':
            print("Alors, c'est pas que ça sert à rien de rajouter un payload sous un moteur, mais on va pas se mentir il va cramer ton satellite.")

        elif self.stage[-1].type == 'booster' and stage_type == 'booster':
            print("Euuuuu Michel va falloir se calmer ça fait vraiment beaucoup de booster la...")

        else:
            #code de la fonction
            new_stage = Stage(stage_type, stage_name, M_empty, M_fuel, P, C_A, C)
            self.stage.append(new_stage)
            self.M             += new_stage.M_empty + new_stage.M_fuel
            self.M_fuel_rocket += new_stage.M_fuel
            self.P             += new_stage.P

    def remove_stage(self):
        """supprime le dernier étage de la fusée. Fonction destinée à l'utilisateur
           si celui-ci se trompe dans son montage """
        if len(self.stage) == 0:
            print("Pour supprimer un étage il faudrait déja qu'il y en ai un.")
        else:
            self.M_fuel_rocket -= self.stage[-1].M_fuel
            self.M -= self.stage[-1].M_empty + self.stage[-1].M_fuel
            self.stage.pop()
        print("Vous venez de supprimer un étage")

    def create_soyuz(self):
        """Permet de créer directement une fusée de type Soyuz"""
        print(txt_to_print+"\nBienvenue dans ce programme permettant de simuler la mise en orbite d'une fusée\n"+txt_to_print)
        self.reset()
        self.add_stage('payload', 'Module Soyuz', 7000, 0, 0, 2.86, 0)
        self.add_stage('stage', 'Troisième étage', 2250, 25200, 300000, 2.78, 105)
        self.add_stage('stage', 'Deuxième étage', 6500, 105000, 1000000, 3.42, 350)
        self.add_stage('booster', 'Boosters', 4*3500, 4*40000, 4*1000000, 4*2.82, 4*333.33)
        print("La fusée est maintenant une fusée Soyuz.")
        self.update_console()

    def reset(self):
        """supprime l'intégralité des étages de la fusée."""
        self.M        = 0
        self.P        = 0
        self.C_A      = 0
        self.C        = 0
        self.C_boost  = 0
        self.stage    =[]

    def update(self):
        """Permet de mettre à jours les valeurs courantes de la fusée"""
        #Mise à jour
        if self.stage[-1].type == 'booster':
            self.P       = self.stage[-1].P + self.stage[-2].P
            self.C_A     = self.stage[-1].C_A + self.stage[-2].C_A
            self.C       = self.stage[-2].C
            self.C_boost = self.stage[-1].C

        elif self.stage[-1].type != 'payload':
            self.P       = self.stage[-1].P
            self.C_A     = self.stage[-1].C_A
            self.C       = self.stage[-1].C
        #Mise à jour console
        self.update_console()

    """def M_actuelle(self):
        M_act = sum(self.stage[:].M_total))
        return M_act""" #j'arrive pas à le coder

    """def fuel_remaining(self):
        M_fuel_stage =deepcopy(self.stage[:].M_fuel)
        for i in range(len(M_fuel_stage)):
            M_fuel_remaining = sum(M_fuel_stage)
        return M_fuel_remaining"""

    def update_console(self):
        """Affiche l'état actuel de la fusée"""
        print("Etat actuel de la fusée:")
        print("Etages restants: \n")
        for i in range(len(self.stage)):
            print("{nom}\t\t|Carburant restant: {fuel:>8}|Masse à vide: {masse:>8}|Poussée disponible: {pousee:>8}".format(nom = self.stage[i].name, fuel = str(self.stage[i].M_fuel)+"kg", masse = str(self.stage[i].M_empty)+"kg", pousee = str(self.stage[i].P)+"N"))
        print("\n")
        print("Paramètres généraux: \n")
        #print("Carburant restant{}\n".format(self.M_fuel_remaining))
        print("Carburant restant: {}kg".format(self.M_fuel_rocket))
        print("Masse totale: {}kg".format(self.M))
        print("Poussée restante: {}N\n".format(self.P))


    def decoupling(self):
        """détache le dernier étage. Utilisé lors des calculs"""
        #if self.stage[-1].M_fuel == 0:
        print(txt_to_print+"\n/!\ SEPARATION\n"+txt_to_print)
        self.M -= self.stage[-1].M_empty
        self.M_fuel_rocket -= self.stage[-1].M_fuel
        self.stage.pop()
        self.update()
    def stage_time(self):
        """Calcul la durée dépuisement du fuel de l'étage actuel"""
        t_stage = self.stage[-1].M_fuel/self.stage[-1].C
        return t_stage

    def initial_velocity(self, position, environnement):
        """Converti la position données en coordonnées sphériques pour le transformer
           en vitesse initiale en coordonnées cartésiennes due à la rotation de la Terre"""
        r   = environnement.r_earth
        v   = 2*math.pi*environnement.freq_rot*r
        v_x = -v*math.cos(position[1])
        v_y =  v*math.sin(position[1])

        return np.array([v_x, v_y, 0])

    def launch(self, position, environnement):
        """Définis la séquence de lancement et calcule l'EM"""
        X = convert_init(position, environnement)
        V = initial_velocity(position, environnement)
        Z = [X,Y]
        self.update()
