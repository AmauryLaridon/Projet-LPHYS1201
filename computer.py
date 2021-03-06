import math
import scipy.integrate as sc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import csv
import os

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from fusee import *
from environnement import *
from graphics import *


# -----------------------------CLASSE QUI PERMET D EFFECTUER TOUS LES CALCULS ET DE LES AFFICHER--------------------------#
class Computer:
    def __init__(self, rocket=None):
        if rocket is None:
            self.rocket = Rocket()
            self.rocket.create_soyuz_mod()
        else:
            self.rocket = rocket
        self.environment = Environment()
        self.solution = []
        self.data_tg = [[], []]
        self.t_stop = 0
        self.theta_0 = []
        self.data_t = []
        self.data_y = [[], [], [], [], [], [], []]
        self.orb_dir = []
        self.separation_time = [0]

        self.orbit_h_wanted = 400000

        self.v_rad_reached = 0
        self.space_reached = False
        self.crashed = False

    def orbital_direction(self, X, V):
        """Défini le vecteur normal au plan de l'orbite"""
        XxV = np.cross(X, V)
        orbital_direction = XxV / np.linalg.norm(XxV)
        return orbital_direction

    def normal_acceleration(self, orbital_direction, r_hat):
        """Fonction à implémenter dans RK45 pour avoir une circularisation de l'orbite après la première phase du vol"""
        thrust_direction = np.cross(orbital_direction, r_hat)
        return thrust_direction

    def coord_to_rad(self, position):
        """Converti les coordonnées angulaires données en degré en radian"""
        new_pos = [position[0] * math.pi / 180, position[1] * math.pi / 180]

        return new_pos

    def convert_init(self, position):
        """Converti les coordonnées spheriques en coordonnées cartésiennes a l'initialisation"""
        x = self.environment.r_earth * math.cos(position[0]) * math.cos(position[1])
        y = self.environment.r_earth * math.cos(position[0]) * math.sin(position[1])
        z = self.environment.r_earth * math.sin(position[0])

        return [x, y, z]

    def convert_SC(self, position):
        """Converti les coordonnées sphériques en coordonnées cartésiennes [r, theta, phi]"""
        x = position[0] * math.cos(position[1]) * math.cos(position[2])
        y = position[0] * math.cos(position[1]) * math.sin(position[2])
        z = position[0] * math.sin(position[1])

        return [x, y, z]

    def convert_CS(self, position):
        """Converti les coordonnées cartésiennes en coordonnées sphériques"""
        r = math.sqrt(sum([x_i ** 2 for x_i in position]))

        if position[0] == 0 and position[1] >= 0:
            phi = math.pi / 2
        elif position[0] == 0:
            phi = 3 * math.pi / 2
        else:
            phi = math.atan2(position[1], position[0])
        if position[0] ** 2 + position[1] ** 2 == 0:
            theta = math.pi / 2 * math.copysign(1, position[2])
        else:
            theta = math.atan2(position[2], math.sqrt(position[0] ** 2 + position[1] ** 2))

        return [r, theta, phi]

    def radial_velocity(self, r_hat, v):
        """input la vitesse en coordonnées cartésienne [v_x, v_y, v_z] et les angles theta/phi [theta, phi] et return la vitesse radial v_rad"""
        V = np.array(v)
        v_rad = np.dot(V, r_hat)

        return v_rad

    def earth_rotation_velocity(self, position):
        """Converti la position données en coordonnées sphériques pour le transformer en vitesse initiale due à la rotation de
           la Terre en coordonnées cartésiennes"""
        r = self.environment.r_earth * math.cos(position[0])
        omega = 2 * math.pi * self.environment.freq_rot * r
        v_x = -omega * math.sin(position[1])
        v_y = omega * math.cos(position[1])

        return [v_x, v_y, 0]

    def wind_velocity(self, position):
        """Converti la position données en coordonnées sphériques pour retourner la vitesse du vent en coordonnées cartésiennes"""
        r = position[0] * math.cos(position[1])
        omega = 2 * math.pi * self.environment.freq_rot * r
        v_x = -omega * math.sin(position[2])
        v_y = omega * math.cos(position[2])

        return np.array([v_x, v_y, 0])

    def gravity_turn_test(self, h, r_hat):
        dir = math.cos(h / 200000) * r_hat + math.sin(h / 200000) * np.cross(self.orb_dir, r_hat)  # 22000 c sympa
        return dir

    def gravity_turn_test2(self, h, r_hat):
        dir = math.cos(h / 200000) * r_hat + math.sin(h / 200000) * np.cross(self.orb_dir, r_hat)  # 22000 c sympa
        return dir

    # ------------------------ Fonctions implémentées pour l'équation différentielle ---------------------- #

    def test_launch(self, t, X):
        """fonction a implementer dans RK-45 pour un lancement purement radiale, ou plus mtn enfait"""
        # Variables de positions et de vitesse.
        x, y, z, v_x, v_y, v_z, M = X

        # coordonnées sphériques
        r, theta, phi = self.convert_CS([x, y, z])

        # vecteur position normé
        r_hat = np.array([x, y, z]) / r
        V = np.array([v_x, v_y, v_z])

        # calcul de la vitesse radiale
        v_rad = self.radial_velocity(r_hat, V)
        v_pot = math.sqrt(2 * self.environment.G * self.environment.M_earth * abs(1 / (self.environment.r_earth + self.orbit_h_wanted) - 1 / r))
        # Vitesse nécessaire pour avoir l'energie potentielle définie par la hauteur de l'orbite voulue
        if v_rad >= v_pot:
            self.v_rad_reached = True
        # Défini le vent
        V_wind = self.wind_velocity([r, theta, phi])
        # Défini les vitesses relatives dues au "vent"
        V_rel = V - V_wind
        v_rel = np.linalg.norm(V_rel)

        # Défini la densité de l'air
        if not self.environment.cool_athm:
            rho = self.environment.US_standart(r)
        else:
            rho = self.environment.air_density(r)

        # calul l'apoapsis Ap et le périapsis Pe
        delta = (self.environment.G ** 2) * (self.environment.M_earth ** 2) + r ** 2 * (np.linalg.norm(np.cross(V, r_hat)) ** 2) * (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)

        if delta > 0:
            self.Pe = (-self.environment.G * self.environment.M_earth + math.sqrt(delta)) / (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)
            self.Ap = (-self.environment.G * self.environment.M_earth - math.sqrt(delta)) / (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)
        else:
            self.Pe = 0
            self.Ap = 0
            print("FUCK")

        if r < self.environment.r_earth - 100 and not self.crashed:  # les 100 c'est juste par sécurité
            self.crashed = True
        if r >= self.environment.r_earth + self.environment.h_athm and not self.space_reached:
            self.space_reached = True

        # Variation de masse
        dM = -self.rocket.C - self.rocket.C_boost

        # calcul de l'accélération
        a_grav = - (self.environment.G * self.environment.M_earth) / (r ** 2)
        a_eng = self.rocket.P / M
        if r < self.environment.r_earth + 5000:
            eng_dir = r_hat
        elif r < self.environment.r_earth + 5500:
            eng_dir = math.cos(0.2) * r_hat + math.sin(0.2) * self.normal_acceleration(self.orb_dir, r_hat)
            eng_dir = eng_dir / np.linalg.norm(eng_dir)
        elif not self.v_rad_reached:
            # eng_dir = math.sin(self.theta_0) * V / np.linalg.norm(V) + math.cos(self.theta_0) * r_hat
            eng_dir = self.gravity_turn_test(r - self.environment.r_earth, r_hat)
            eng_dir = eng_dir / np.linalg.norm(eng_dir)
        else:
            eng_dir = self.normal_acceleration(self.orb_dir, r_hat)

        # vérifie si on est en orbite
        if delta > 0:
            if self.Pe >= self.environment.r_earth + self.orbit_h_wanted - 500:
                a_eng = 0
                dM = 0
                if self.t_stop == 0:
                    self.t_stop = t

        C_A = self.rocket.C_A

        a_x, a_y, a_z = a_grav * r_hat - rho * v_rel * C_A * V_rel / (2 * M) + a_eng * eng_dir

        a_g = np.array([a_x, a_y, a_z]) - a_grav * r_hat
        g = np.linalg.norm(a_g) / 9.81
        self.data_tg[0].append(t)
        self.data_tg[1].append(g)

        return np.array([v_x, v_y, v_z, a_x, a_y, a_z, dM])

    def free_fall(self, t, X):
        """fonction a implementer dans RK-45 pour un lancement purement radiale, ou plus mtn enfait"""
        # Variables de positions et de vitesse.
        x, y, z, v_x, v_y, v_z, M = X

        # coordonnées sphériques
        r, theta, phi = self.convert_CS([x, y, z])

        # vecteur position normé
        r_hat = np.array([x, y, z]) / r
        V = np.array([v_x, v_y, v_z])

        # calcul de la vitesse radiale
        v_rad = self.radial_velocity(r_hat, V)
        v_pot = math.sqrt(2 * self.environment.G * self.environment.M_earth * abs(1 / (self.environment.r_earth + self.orbit_h_wanted) - 1 / r))
        # Vitesse nécessaire pour avoir l'energie potentielle définie par la hauteur de l'orbite voulue
        if v_rad >= v_pot:
            self.v_rad_reached = True
        # Défini le vent
        V_wind = self.wind_velocity([r, theta, phi])
        # Défini les vitesses relatives dues au "vent"
        V_rel = V - V_wind
        v_rel = np.linalg.norm(V_rel)

        # Défini la densité de l'air
        if not self.environment.cool_athm:
            rho = self.environment.US_standart(r)
        else:
            rho = self.environment.air_density(r)

        # calul l'apoapsis Ap et le périapsis Pe
        delta = (self.environment.G ** 2) * (self.environment.M_earth ** 2) + r ** 2 * (np.linalg.norm(np.cross(V, r_hat)) ** 2) * (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)

        if delta > 0:
            self.Pe = (-self.environment.G * self.environment.M_earth + math.sqrt(delta)) / (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)
            self.Ap = (-self.environment.G * self.environment.M_earth - math.sqrt(delta)) / (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)
        else:
            self.Pe = 0
            self.Ap = 0
            print("FUCK")

        if r < self.environment.r_earth - 100 and not self.crashed:  # les 100 c'est juste par sécurité
            self.crashed = True
        if r >= self.environment.r_earth + self.environment.h_athm and not self.space_reached:
            self.space_reached = True

        # Variation de masse
        dM = 0

        # calcul de l'accélération
        a_grav = - (self.environment.G * self.environment.M_earth) / (r ** 2)

        C_A = self.rocket.C_A

        a_x, a_y, a_z = a_grav * r_hat - rho * v_rel * C_A * V_rel / (2 * M)

        a_g = np.array([a_x, a_y, a_z]) - a_grav * r_hat
        g = np.linalg.norm(a_g) / 9.81
        self.data_tg[0].append(t)
        self.data_tg[1].append(g)

        return np.array([v_x, v_y, v_z, a_x, a_y, a_z, dM])

    def circularisation(self, t, X):
        """fonction a implementer dans RK-45 pour un lancement purement radiale, ou plus mtn enfait"""
        # Variables de positions et de vitesse.
        x, y, z, v_x, v_y, v_z, M = X

        # coordonnées sphériques
        r, theta, phi = self.convert_CS([x, y, z])

        # vecteur position normé
        r_hat = np.array([x, y, z]) / r
        V = np.array([v_x, v_y, v_z])

        # calcul de la vitesse radiale
        v_rad = self.radial_velocity(r_hat, V)
        v_pot = math.sqrt(2 * self.environment.G * self.environment.M_earth * abs(1 / (self.environment.r_earth + self.orbit_h_wanted) - 1 / r))
        # Vitesse nécessaire pour avoir l'energie potentielle définie par la hauteur de l'orbite voulue
        if v_rad >= v_pot:
            self.v_rad_reached = True
        # Défini le vent
        V_wind = self.wind_velocity([r, theta, phi])
        # Défini les vitesses relatives dues au "vent"
        V_rel = V - V_wind
        v_rel = np.linalg.norm(V_rel)

        # Défini la densité de l'air
        if not self.environment.cool_athm:
            rho = self.environment.US_standart(r)
        else:
            rho = self.environment.air_density(r)

        # calul l'apoapsis Ap et le périapsis Pe
        delta = (self.environment.G ** 2) * (self.environment.M_earth ** 2) + r ** 2 * (np.linalg.norm(np.cross(V, r_hat)) ** 2) * (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)

        if delta > 0:
            self.Pe = (-self.environment.G * self.environment.M_earth + math.sqrt(delta)) / (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)
            self.Ap = (-self.environment.G * self.environment.M_earth - math.sqrt(delta)) / (np.linalg.norm(V) ** 2 - 2 * self.environment.G * self.environment.M_earth / r)
        else:
            self.Pe = 0
            self.Ap = 0
            print("FUCK")

        if r < self.environment.r_earth - 100 and not self.crashed:  # les 100 c'est juste par sécurité
            self.crashed = True
        if r >= self.environment.r_earth + self.environment.h_athm and not self.space_reached:
            self.space_reached = True

        # calcul de l'accélération
        a_grav = - (self.environment.G * self.environment.M_earth) / (r ** 2)

        # vérifie si on est en orbite
        if delta > 0:
            if self.Ap - self.Pe < 500:
                a_eng = 0
                dM = 0
                eng_dir = - V / np.linalg.norm(V)
            else:
                a_eng = self.rocket.P / M
                dM = -self.rocket.C - self.rocket.C_boost
                eng_dir = - V / np.linalg.norm(V)

        C_A = self.rocket.C_A

        a_x, a_y, a_z = a_grav * r_hat - rho * v_rel * C_A * V_rel / (2 * M) + a_eng * eng_dir

        a_g = np.array([a_x, a_y, a_z]) - a_grav * r_hat
        g = np.linalg.norm(a_g) / 9.81
        self.data_tg[0].append(t)
        self.data_tg[1].append(g)

        return np.array([v_x, v_y, v_z, a_x, a_y, a_z, dM])

    # ---------------------- Fonction à utiliser pour tout le lancement ------------------- #

    def launch(self, position):
        """Fonction qui prend en charge tout les calculs lors du lancement de la fusée
        :param position: liste de dimension 2 [a, b] dont les composantes sont respectivement la latitude et la longitude
        :return: que dalle mais les données du vol sont stockées dans self.data_t et self.data_y
        """
        print(txt_to_print + "\n/!\ DECOLAGE\n" + txt_to_print + "\n")
        # Conditions initiales
        angles = self.coord_to_rad(position)
        X = self.convert_init(angles)
        V = self.earth_rotation_velocity(angles)
        Y = X + V
        Y = Y + [0]
        T = 0
        t_0 = 0
        self.theta_0 = angles[0]
        self.orb_dir = self.orbital_direction(X, V)

        # Calcul radial launch
        for i in range(len(self.rocket.stage) - 1):
            # Initialistion masse et temps
            Y[6] = self.rocket.M
            t_0 += T
            T = self.rocket.stage_time()
            # Calcul et résolution de l'équation différentielle
            self.solution.append(sc.solve_ivp(self.test_launch, (t_0, T + t_0), Y, vectorized=False, max_step=T / 500))
            # vérifie si il faut découpler ou pas (et découple si il faut)
            if self.t_stop == 0:
                # Découplage une fois le temps de l'étage courant atteint
                print("Découplage du " + self.rocket.stage[-1].name + " après :" + str(T + t_0) + "s")
                self.rocket.decouple()
                for j in range(7):
                    Y[j] = self.solution[i].y[j][-1]
                self.separation_time.append(t_0 + T)
            else:
                print("Arret du moteur après " + str(self.t_stop) + "s")
                self.rocket.remove_fuel(self.t_stop - t_0)
                while self.solution[-1].t[-2] >= self.t_stop and len(self.solution[-1].t) > 2:
                    self.solution[-1].t = np.delete(self.solution[-1].t, -1)
                    self.solution[-1].y = np.delete(self.solution[-1].y, -1, axis=1)
                for j in range(7):
                    Y[j] = self.solution[i].y[j][-1]
                a = abs(self.Pe + self.Ap) / 2
                t_0 = self.solution[-1].t[-1]
                T = 1.1 * 2 * math.pi * math.sqrt((a ** 3) / (self.environment.G * self.environment.M_earth))
                self.solution.append(sc.solve_ivp(self.free_fall, (t_0, T + t_0), Y, vectorized=False, max_step=T / 1000))
                dist = self.Pe
                for j in range(len(self.solution[-1].t)):
                    if abs(math.sqrt(sum([self.solution[-1].y[0][j]**2 + self.solution[-1].y[1][j]**2 + self.solution[-1].y[2][j]**2])) - self.Pe) <= dist:
                        r = math.sqrt(sum([self.solution[-1].y[0][j] ** 2 + self.solution[-1].y[1][j] ** 2 + self.solution[-1].y[2][j] ** 2]))
                        dist = abs(r - self.Pe)
                        t_Pe = self.solution[-1].t[j]
                        v_Pe = math.sqrt(sum([self.solution[-1].y[3][j]**2 + self.solution[-1].y[4][j]**2 + self.solution[-1].y[5][j]**2]))
                v_Pe_circular = math.sqrt(self.environment.G * self.environment.M_earth/r)
                delta_v = abs(v_Pe_circular - v_Pe)
                delta_t = (1 - math.e ** (-delta_v * self.rocket.C / self.rocket.stage[-1].P)) * self.solution[-1].y[6][-1] / self.rocket.C
                t_0 = t_Pe - delta_t / 2
                T = delta_t
                while self.solution[-1].t[-2] >= t_0 and len(self.solution[-1].t) > 2:
                    self.solution[-1].t = np.delete(self.solution[-1].t, -1)
                    self.solution[-1].y = np.delete(self.solution[-1].y, -1, axis=1)
                for j in range(7):
                    Y[j] = self.solution[-1].y[j][-1]
                self.solution.append(sc.solve_ivp(self.circularisation, (t_0, t_0 + T), Y, vectorized=False, max_step=T / 100))
                print("Phase de circularisation!")
                print("Découplage du " + self.rocket.stage[-1].name + " après :" + str(T + t_0) + "s")
                self.rocket.decouple()
                for j in range(7):
                    Y[j] = self.solution[-1].y[j][-1]
                self.separation_time.append(t_0 + T)

        # Calcul du restant de l'orbite une fois qu'il reste uniquement la payload
        # Initialisation masse et temps
        Y[6] = self.rocket.M
        t_0 += T
        # T = 6000
        T = 8500
        # Calcul et résolution de l'équation différentielle
        self.solution.append(sc.solve_ivp(self.free_fall, (t_0, T + t_0), Y, vectorized=False, max_step=T / 1000))
        for j in range(7):
            Y[j] = self.solution[-1].y[j][-1]
        self.separation_time.append(t_0 + T)

        # Enregistrement des solutions
        for i in range(len(self.solution)):
            for j in range(len(self.solution[i].t)):
                self.data_t.append(self.solution[i].t[j])
                for k in range(7):
                    self.data_y[k].append(self.solution[i].y[k][j])

        # Ecriture des donnée dans un fichier
        with open("flight_data.csv", 'a') as file:
            if os.stat("flight_data.csv").st_size == 0:
                # On pose une référence à self.solution parce qu'aussi non la longueur de notre ligne de code
                # est trop grande pour être prise en compte.
                a = self.solution
                writer = csv.writer(file)
                writer.writerow(["t", "x", "y", "z", "v_x", "v_y", "v_z", "M"])
                for i in range(len(self.solution)):
                    for j in range(len(self.solution[i].t)):
                        writer.writerow([a[i].t[j], a[i].y[0][j], a[i].y[1][j], a[i].y[2][j], a[i].y[3][j], a[i].y[4][j], a[i].y[5][j], a[i].y[6][j]])

        if self.space_reached:
            if self.crashed:
                print("Félicitation, nous avons atteind l'espace!! Cepandant, pour des raisons inconnues il semblerait que nous nous soyons tout de même écrasé... too bad...")
            else:
                print("Bienvenue dans l'espace!!!")
        else:
            if self.crashed:
                print("CRASH!!!")
