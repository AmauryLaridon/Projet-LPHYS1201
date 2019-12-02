import math
import scipy as sc
import numpy as np

from environnement import *

#CLASSE DECRIVANT LES DONNEES D UN ETAGE
class Stage:
    def __init__(self, type, M_empty, M_fuel, P, C_A, C):
        self.type     = type
        self.M_empty  = M_empty
        self.M_fuel   = M_fuel
        self.P        = P
        self.C_A      = C_A
        self.C        = C

#CLASSE DECRIVANT LA FUSEE UTILISEE
class Rocket:
    def __init__(self):
        self.M        = 0
        self.P        = 0
        self.C_A      = 0
        self.C        = 0
        self.C_boost  = 0
        self.stage    =[]

    def add_stage(self, stage_type, M_empty, M_fuel, P, C_A, C):
        """ajoute une étage à la fusée en partant de la charge utile (le haut)"""

        #test des erreurs possibles
        if len(self.stage) == 0: 
            if stage_type != 'payload':
                print("La construction de la fusée doit commencer par de placement de la charge utile.")
            else:
                new_stage = Stage(stage_type, M_empty, M_fuel, P, C_A, C)
                self.stage.append(new_stage)
                self.M += new_stage.M_empty + new_stage.M_fuel

        elif self.stage[-1].type != 'payload' and stage_type == 'payload':
            print("Alors, c'est pas que ça sert à rien de rajouter un payload sous un moteur, mais on va pas se mentir il va cramer ton satellite.")

        elif self.stage[-1].type == 'booster' and stage_type == 'booster':
            print("Euuuuu Michel va falloir se calmer ça fait vraiment beaucoup de booster la...")

        else:
            #code de la fonction
            new_stage = Stage(stage_type, M_empty, M_fuel, P, C_A, C)
            self.stage.append(new_stage)
            self.M += new_stage.M_empty + new_stage.M_fuel

    def remove_stage(self):
        """supprime le dernier étage de la fusée."""
        if len(self.stage) == 0:
            print("Pour supprimer un étage il faudrait déja qu'il y en ai un.")
        else:
            self.M -= self.stage[-1].M_empty + self.stage[-1].M_fuel
            self.stage.pop()

    def reset(self):
        """supprime l'intégralité des étages de la fusée."""
        self.M        = 0
        self.P        = 0
        self.C_A      = 0
        self.C        = 0
        self.C_boost  = 0
        self.stage    =[]

    def create_soyuz(self):
        self.reset()
        self.add_stage('payload', 7000, 0, 0, 2.86, 0)
        self.add_stage('stage', 2250, 25200, 300000, 2.78, 105)
        self.add_stage('stage', 6500, 105000, 1000000, 3.42, 350)
        self.add_stage('booster', 4*3500, 4*40000, 4*1000000, 4*2.82, 4*333.33)
        print("La fusée est maintenant une fusée Soyuz.")

    def update(self):
        if self.stage[-1].type == 'booster':
            self.P       = self.stage[-1].P + self.stage[-2].P
            self.C_A     = self.stage[-1].C_A + self.stage[-2].C_A
            self.C       = self.stage[-2].C
            self.C_boost = self.stage[-1].C

        elif self.stage[-1].type != 'payload':
            self.P       = self.stage[-1].P
            self.C_A     = self.stage[-1].C_A
            self.C       = self.stage[-1].C

    def launch(self, position, environment):
        X = convert_init(position, environment)
        V = initial_velocity(position, environment)
        Y = [X,Y]
        self.update()

    def decoupling(self):
        """détache le dernier étage"""
        self.M -= self.stage[-1].M_empty
        self.stage.pop()
        self.update()

    def stage_time(self):
        """Calcul la durée dépuisement du fuel de l'étage actuel"""
        t_stage = self.stage[-1].M_fuel/self.stage[-1].C
        return t_stage

    def display(self):
        pass
