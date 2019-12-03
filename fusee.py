import math
import scipy
import numpy as np

from environnement import *

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
#-----------------------------CLASSE DECRIVANT LA FUSEE UTILISEE---------------------------#
class Rocket:
    def __init__(self):
        self.M        = 0
        self.P        = 0
        self.C_A      = 0
        self.C        = 0
        self.C_boost  = 0
        self.stage    =[]
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
            self.M += new_stage.M_empty + new_stage.M_fuel

    def remove_stage(self):
        """supprime le dernier étage de la fusée. Fonction destinée à l'utilisateur
           si celui-ci se trompe dans son montage """
        if len(self.stage) == 0:
            print("Pour supprimer un étage il faudrait déja qu'il y en ai un.")
        else:
            self.M -= self.stage[-1].M_empty + self.stage[-1].M_fuel
            self.stage.pop()

    def create_soyuz(self):
        """Permet de créer directement une fusée de type Soyuz"""
        self.reset()
        self.add_stage('payload', 'Module Soyuz', 7000, 0, 0, 2.86, 0)
        self.add_stage('stage', 'Troisième étage', 2250, 25200, 300000, 2.78, 105)
        self.add_stage('stage', 'Deuxième étage', 6500, 105000, 1000000, 3.42, 350)
        self.add_stage('booster', 'Booster', 4*3500, 4*40000, 4*1000000, 4*2.82, 4*333.33)
        print("La fusée est maintenant une fusée Soyuz.")

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
        if self.stage[-1].type == 'booster':
            self.P       = self.stage[-1].P + self.stage[-2].P
            self.C_A     = self.stage[-1].C_A + self.stage[-2].C_A
            self.C       = self.stage[-2].C
            self.C_boost = self.stage[-1].C

        elif self.stage[-1].type != 'payload':
            self.P       = self.stage[-1].P
            self.C_A     = self.stage[-1].C_A
            self.C       = self.stage[-1].C
    def update_txt(self):
        self.update()
        print("Données actuelles de la fusée :")

    def decoupling(self):
        """détache le dernier étage. Utilisé lors des calculs"""
        self.M -= self.stage[-1].M_empty
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
