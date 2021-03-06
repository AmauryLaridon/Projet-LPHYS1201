import math
import scipy
import numpy as np
from copy import copy, deepcopy

from environnement import *

txt_to_print = "----------------------------------------------------------------------------------------------------------------------------"
txt_to_print2 = "  "


# --------------------------CLASSE DECRIVANT LES DONNEES D UN ETAGE----------------------- #
class Stage:
    def __init__(self, type, name, M_empty, M_fuel, P, C_A, C):
        self.type = type
        self.M_empty = M_empty
        self.M_fuel = M_fuel
        self.P = P
        self.C_A = C_A
        self.C = C
        self.name = name
        self.M_total = M_empty + M_fuel


# -----------------------------CLASSE DECRIVANT LA FUSEE UTILISEE--------------------------- #
class Rocket:
    def __init__(self):
        self.M = 0
        self.M_fuel_rocket = 0
        self.P = 0
        self.P_tot = 0
        self.C_A = 0
        self.C = 0
        self.C_boost = 0
        self.stage = []

    # -------------------------------CONSTRUCTION DE LA FUSEE--------------------------------- #
    def add_stage(self, stage_type, stage_name, M_empty, M_fuel, P, C_A, C):
        """ajoute une étage à la fusée en partant de la charge utile (le haut)
        param:  -- stage_type: string définissant le type d'étage soit "payload", "stage", "booster"
            - le premier étage ajouté doit toujour etre de type payload
            - on ne peut pas ajouter de booster sur des booster
                -- stage_name: string, c'est juste le nom de l'étage
                -- M_empty: int or float, correspond à la masse de l'étage sans M_fuel en kilogramme
                -- M_fuel: int or float, correspond à la masse de fuel dans l'étages en kilogramme
                -- P: int or float, puissance des moteurs en newton
                -- C_A : int or float, coefficient de frottement
                -- C : int or float, débit de perte massique en kilogramme par seconde"""
        if len(self.stage) == 0:
            if stage_type != 'payload':
                print(txt_to_print + "\nBienvenue dans ce programme permettant de simuler la mise en orbite d'une fusée!\n" + txt_to_print)
                print("La construction de la fusée doit commencer par de placement de la charge utile.")
            else:
                print(txt_to_print + "\nBienvenue dans ce programme permettant de simuler la mise en orbite d'une fusée!\n" + txt_to_print)
                new_stage = Stage(stage_type, stage_name, M_empty, M_fuel, P, C_A, C)
                self.stage.append(new_stage)
                self.M += new_stage.M_empty + new_stage.M_fuel
                self.P += new_stage.P
                self.P_tot += new_stage.P

        elif self.stage[-1].type != 'payload' and stage_type == 'payload':
            print("Alors, c'est pas que ça sert à rien de rajouter un payload sous un moteur, mais on va pas se mentir il va cramer ton satellite.")

        elif self.stage[-1].type == 'booster' and stage_type == 'booster':
            print("Euuuuu Michel va falloir se calmer ça fait vraiment beaucoup de booster la...")

        else:
            new_stage = Stage(stage_type, stage_name, M_empty, M_fuel, P, C_A, C)
            self.stage.append(new_stage)
            self.M += new_stage.M_empty + new_stage.M_fuel
            self.P += new_stage.P
            self.P_tot += new_stage.P

    def remove_stage(self):
        """supprime le dernier étage de la fusée. Fonction destinée à l'utilisateur si celui-ci se trompe dans son montage """
        if len(self.stage) == 0:
            print("Pour supprimer un étage il faudrait déja qu'il y en ai un.")
        else:
            self.M_fuel_rocket -= self.stage[-1].M_fuel
            self.M -= self.stage[-1].M_empty + self.stage[-1].M_fuel
            self.P_tot -= + self.stage[-1].P
            self.stage.pop()
        print("Vous venez de supprimer un étage")

    # -----------------------------------------------TYPE DE FUSÉES---------------------------------------------------#

    def create_soyuz(self):
        """Permet de créer directement une fusée de type Soyuz"""
        self.reset()
        self.add_stage('payload', 'Module Soyuz', 7000, 0, 0, 2.86, 0)
        self.add_stage('stage', 'Troisième étage', 2250, 25200, 300000, 2.78, 105)
        self.add_stage('stage', 'Deuxième étage', 6500, 105000, 1000000, 3.42, 350)
        self.add_stage('booster', 'Boosters', 4 * 3500, 4 * 40000, 4 * 1000000, 4 * 2.82, 4 * 333.33)
        self.update()
        print("La fusée est maintenant une fusée Soyuz.")

    def create_soyuz_mod(self):
        """Permet de créer directement une fusée de type Soyuz modifié, légèrement plus puissante afin de faciliter la mise en orbite"""
        self.reset()
        self.add_stage('payload', 'Module Soyuz', 7000, 0, 0, 2.86, 0)
        self.add_stage('stage', 'Troisième étage', 2250, 25200, 425000, 2.78, 105)
        self.add_stage('stage', 'Deuxième étage', 6500, 105000, 1060000, 3.42, 350)
        self.add_stage('booster', 'Boosters', 4 * 3500, 4 * 40000, 4 * 1000000, 4 * 2.82, 4 * 333.33)
        self.update()
        print("La fusée est maintenant une fusée de type Soyuz légèrement modifée afin de pouvoir se mettre en orbite plus facilement.")

    def create_falcon_9(self):
        """Permet de créer directement une fusée de type Falcon 9"""
        self.reset()
        self.add_stage('payload', 'Satellite', 5000, 0, 0, 2.00, 0)
        self.add_stage('stage', 'Deuxième étage', 4000, 108000, 934000, 2.78, 272)
        self.add_stage('stage', 'Première étage', 23000, 388000, 6805000, 3.42, 2395)
        self.update()
        print("La fusée est maintenant une fusée de type Falcon 9")

    def create_falcon_heavy(self):
        """Permet de créer directement une fusée de type Falcon heavy"""
        self.reset()
        self.add_stage('payload', 'Satellite', 5000, 0, 0, 2.00, 0)
        self.add_stage('stage', 'Deuxième étage', 4000, 108000, 934000, 2.78, 272)
        self.add_stage('stage', 'Première étage', 23000, 388000, 6805000, 3.42, 2395)
        self.add_stage('booster', 'Boosters', 2 * 23000, 2 * 388000, 2 * 6805000, 2 * 3.42, 2 * 2395)
        self.update()
        print("La fusée est maintenant une fusée de type Falcon heavy")

    def create_saturnV(self):
        """Permet de créer directement une fusée de type Saturn V"""
        self.reset()
        self.add_stage('payload', "LEM + Module de service", 47000, 0, 0, 2.00, 0)
        self.add_stage('stage', 'Troisième étage', 11300, 95700, 1000000, 2.78, 203.18)
        self.add_stage('stage', 'Deuxième étage', 36500, 445000, 5000000, 3.42, 1234)
        self.add_stage('stage', 'Premier étage', 130400 ,2148600, 33400000, 4, 14324)
        self.update()
        print("La fusée est maintenant une fusée de type SaturnV")

    # -------------------------------------FONCTIONS LIEES A LA FUSEE-------------------------------------------------- #


    def reset(self):
        """supprime l'intégralité des étages de la fusée."""
        self.M = 0
        self.M_fuel_rocket = 0
        self.P = 0
        self.P_tot = 0
        self.C_A = 0
        self.C = 0
        self.C_boost = 0
        self.stage = []

    def update(self):
        """Permet de mettre à jours les valeurs courantes de la fusée"""
        self.M_fuel_rocket = 0
        self.P_tot = 0
        for i in range(len(self.stage)):
            self.M_fuel_rocket += self.stage[i].M_fuel
            self.P_tot += self.stage[i].P

        if self.stage[-1].type == 'booster':
            self.P = self.stage[-1].P + self.stage[-2].P
            self.C_A = self.stage[-1].C_A + self.stage[-2].C_A
            self.C = self.stage[-2].C
            self.C_boost = self.stage[-1].C

        elif self.stage[-1].type != 'payload':
            self.P = self.stage[-1].P
            self.C_A = self.stage[-1].C_A
            self.C = self.stage[-1].C
            self.C_boost = 0

        else:
            self.P = 0
            self.C_A = 0
            self.C = 0
            self.C_boost = 0

        # Mise à jour console
        self.update_console()

    def update_console(self):
        """Affiche l'état actuel de la fusée en console"""
        print("Etat actuel de la fusée:\nEtages restants: \n")
        for i in range(len(self.stage)):
            print("{nom}\t\t|Carburant restant: {fuel:>8}|Masse à vide: {masse:>8}|Poussée disponible: {pousee:>8}".format(nom=self.stage[i].name, fuel=str(self.stage[i].M_fuel) + "kg",
                                                                                                                           masse=str(self.stage[i].M_empty) + "kg", pousee=str(self.stage[i].P) + "N"))
        print("\n")
        print("Paramètres généraux: \n")
        print("Carburant restant: {}kg".format(self.M_fuel_rocket))
        print("Masse totale: {}kg".format(self.M))
        if self.stage[-1].type == "booster":
            print("Poussée de l'étage courant:{}N\n".format(self.stage[-1].P + self.stage[-2].P))
        else:
            print("Poussée de l'étage courant:  {}N\n".format(self.stage[-1].P))

    def stage_time(self):
        """Calcul la durée dépuisement du fuel de l'étage actuel"""
        t_stage = self.stage[-1].M_fuel / self.stage[-1].C
        return t_stage

    def decouple(self):
        """Détache le dernier étage"""
        print(txt_to_print + "\n/!\ SEPARATION\n" + txt_to_print)
        self.M -= self.stage[-1].M_empty + self.stage[-1].M_fuel
        if self.stage[-1].type == 'booster':
            T = self.stage_time()
            self.stage[-2].M_fuel -= self.stage[-2].C * T
            self.M -= self.stage[-2].C * T
        self.stage.pop()
        self.update()

    def remove_fuel(self, dt):
        """Permet de calculer le fuel consommé durant un certain lapse de temps."""
        if self.stage[-1].type == 'booster':
            self.stage[-2].M_fuel -= self.stage[-2].C * dt
            self.M -= self.stage[-2].C * dt
        self.stage[-1].M_fuel -= self.stage[-1].C * dt
        self.M -= self.stage[-1].C * dt
        self.update()
