import math
import scipy.integrate as ode
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import csv

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from fusee import *
from environnement import *


# -----------------------------CLASSE POUR L'AFFICHAGE--------------------------#
class Graphics:
    def __init__(self, computer):
        self.x = []
        self.y = []
        self.z = []
        self.data_t = computer.data_t
        self.data_y = computer.data_y
        self.computer = computer
        self.environment = computer.environment
        self.rocket = computer.rocket
        len(self.data_t)
        self.r_max = 0
        self.t_anim = 0
        self.i = 0
        self.ax = 0

        self.n = 20
        self.X = [[] for i in range(self.n)]
        self.Y = [[] for i in range(self.n)]
        self.Z = [[] for i in range(self.n)]
        self.T = [[] for i in range(self.n)]
        self.dt = 10

    def update_graphics(self):
        self.x = []
        self.y = []
        self.z = []
        self.data_t = self.computer.data_t
        self.data_y = self.computer.data_y
        self.computer = self.computer
        self.environment = self.computer.environment
        self.rocket = self.computer.rocket
        self.length = len(self.data_t)
        self.r_max = 0
        self.t_anim = 0
        self.i = 0
        self.ax = 0

        self.n = 20
        self.X = [[] for i in range(self.n)]
        self.Y = [[] for i in range(self.n)]
        self.Z = [[] for i in range(self.n)]
        self.T = [[] for i in range(self.n)]
        self.dt = 10

    def animation2(self, _):
        self.dt = max([self.data_t[i + 1] - self.data_t[i] for i in range(len(self.data_t) - 1)]) * 2  # woooooooohoooooooow ca fonctionne michel
        t_max = self.data_t[-1]

        while t_max - 1 >= self.t_anim >= self.data_t[self.i]:
            self.X[0].append(self.data_y[0][self.i])
            self.Y[0].append(self.data_y[1][self.i])
            self.Z[0].append(self.data_y[2][self.i])
            self.T[0].append(self.data_t[self.i])
            self.i += 1

        for i in range(self.n - 1):
            if len(self.T[i]) != 0:
                while self.T[i][0] < self.t_anim - self.dt * (i + 1):
                    self.X[i + 1].append(self.X[i][0])
                    self.X[i].pop(0)
                    self.Y[i + 1].append(self.Y[i][0])
                    self.Y[i].pop(0)
                    self.Z[i + 1].append(self.Z[i][0])
                    self.Z[i].pop(0)
                    self.T[i + 1].append(self.T[i][0])
                    self.T[i].pop(0)
                    if len(self.T[i]) == 0:
                        break
        if len(self.T[-1]) != 0:
            while self.T[-1][0] < self.t_anim - self.dt * (self.n + 1):
                self.X[-1].pop(0)
                self.Y[-1].pop(0)
                self.Z[-1].pop(0)
                self.T[-1].pop(0)
                if len(self.T[-1]) == 0:
                    break

        self.t_anim += 10

        self.ax.clear()

        u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]  # technique allègrement volée ici : https://stackoverflow.com/questions/11140163/plotting-a-3d-cube-a-sphere-and-a-vector-in-matplotlib
        x_earth = self.environment.r_earth * np.cos(u + self.environment.freq_rot * 2 * math.pi * self.t_anim) * np.sin(v)
        y_earth = self.environment.r_earth * np.sin(u + self.environment.freq_rot * 2 * math.pi * self.t_anim) * np.sin(v)
        z_earth = self.environment.r_earth * np.cos(v)
        # self.ax.plot_surface(x_earth, y_earth, z_earth, rstride=1, cstride=1, cmap='magma', alpha = 0.5)
        self.ax.plot_wireframe(x_earth, y_earth, z_earth, color='b', alpha=0.5)

        self.ax.set_xlim(-self.r_max * 1.1, self.r_max * 1.1)
        self.ax.set_ylim(-self.r_max * 1.1, self.r_max * 1.1)
        self.ax.set_zlim(-self.r_max * 1.1, self.r_max * 1.1)

        for i in range(self.n-1):
            if len(self.T[i]) != 0 and len(self.T[i+1]) != 0:
                self.ax.plot(self.X[i] + [self.X[i+1][-1]], self.Y[i] + [self.Y[i+1][-1]], self.Z[i] + [self.Z[i+1][-1]], color='r', alpha=1 - i / self.n)
            else:
                self.ax.plot(self.X[i], self.Y[i], self.Z[i], color='r', alpha=1-i/self.n)
        self.ax.plot(self.X[-1], self.Y[-1], self.Z[-1], color='r', alpha=1/self.n)

    def animation(self, _):
        t_max = self.data_t[-1]
        while t_max - 1 >= self.t_anim >= self.data_t[self.i]:
            self.x.append(self.data_y[0][self.i])
            self.y.append(self.data_y[1][self.i])
            self.z.append(self.data_y[2][self.i])
            self.i += 3

        self.t_anim += 30

        self.ax.clear()

        u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]  # technique allègrement volée ici https://stackoverflow.com/questions/11140163/plotting-a-3d-cube-a-sphere-and-a-vector-in-matplotlib
        x_earth = self.environment.r_earth * np.cos(u + self.environment.freq_rot * 2 * math.pi * self.t_anim) * np.sin(v)
        y_earth = self.environment.r_earth * np.sin(u + self.environment.freq_rot * 2 * math.pi * self.t_anim) * np.sin(v)
        z_earth = self.environment.r_earth * np.cos(v)
        # self.ax.plot_surface(x_earth, y_earth, z_earth, rstride=1, cstride=1, cmap='magma', alpha = 0.5)
        self.ax.plot_wireframe(x_earth, y_earth, z_earth, color='b', alpha=0.5)

        self.ax.set_xlim(-self.r_max * 1.1, self.r_max * 1.1)
        self.ax.set_ylim(-self.r_max * 1.1, self.r_max * 1.1)
        self.ax.set_zlim(-self.r_max * 1.1, self.r_max * 1.1)

        self.ax.plot(self.x, self.y, self.z, color='r')

    def animation_2D(self, _):
        self.dt = max([self.data_t[i + 1] - self.data_t[i] for i in range(len(self.data_t) - 1)]) * 2  # woooooooohoooooooow ca fonctionne michel
        t_max = self.data_t[-1]

        # initialise la base des nouvelles coordonnées
        r_0 = [self.data_y[0][0], self.data_y[1][0], self.data_y[2][0]]
        v_0 = [self.data_y[3][0], self.data_y[4][0], self.data_y[5][0]]
        e_r = r_0 / np.linalg.norm(r_0)
        e_v = v_0 / np.linalg.norm(v_0)
        plane = [[], []]

        # calcul les positions dans les nouvelles coordonnées
        for i in range(len(self.data_t)):
            r = [self.data_y[0][i], self.data_y[1][i], self.data_y[2][i]]
            a, b = np.dot(r, e_r), np.dot(r, e_v)
            plane[0].append(a)
            plane[1].append(b)

        # crée toutes les listes à plot (plusieurs avec des alphas décroissant comme ca meme que c plus zoli)
        while t_max - 1 >= self.t_anim >= self.data_t[self.i]:
            self.X[0].append(plane[0][self.i])
            self.Y[0].append(plane[1][self.i])
            self.T[0].append(self.data_t[self.i])
            self.i += 1
        for i in range(self.n - 1):
            if len(self.T[i]) != 0:
                while self.T[i][0] < self.t_anim - self.dt * (i + 1):
                    self.X[i + 1].append(self.X[i][0])
                    self.X[i].pop(0)
                    self.Y[i + 1].append(self.Y[i][0])
                    self.Y[i].pop(0)
                    self.T[i + 1].append(self.T[i][0])
                    self.T[i].pop(0)
                    if len(self.T[i]) == 0:
                        break
        if len(self.T[-1]) != 0:
            while self.T[-1][0] < self.t_anim - self.dt * (self.n+1):
                self.X[-1].pop(0)
                self.Y[-1].pop(0)
                self.T[-1].pop(0)
                if len(self.T[-1]) == 0:
                    break

        # indente le temps pour la prochaine étape
        self.t_anim += 20

        # plotting
        self.ax.clear()
        border = self.environment.r_earth / 2

        for i in range(self.n-1):
            if len(self.T[i]) != 0 and len(self.T[i+1]) != 0:
                self.ax.plot(self.X[i] + [self.X[i+1][-1]], self.Y[i] + [self.Y[i+1][-1]], color='r', alpha=1 - i / self.n)
            else:
                self.ax.plot(self.X[i], self.Y[i], color='r', alpha=1-i/self.n)
        self.ax.plot(self.X[-1], self.Y[-1], color='r', alpha=1/self.n)

        self.ax = plt.gca()
        earth = plt.Circle((0, 0), self.environment.r_earth)
        self.ax.add_artist(earth)
        self.ax.axis('scaled')
        if len(self.T[0]) != 0:
            plt.xlim(self.X[0][-1] - border, self.X[0][-1] + border)
            plt.ylim(self.Y[0][-1] - border, self.Y[0][-1] + border)

            # plt.xlim(-self.r_max * 1.1, self.r_max * 1.1)
            # plt.ylim(-self.r_max * 1.1, self.r_max * 1.1)

    def display_3D_animation(self, animation):
        self.update_graphics()
        self.length = len(self.data_t)
        r_2 = [self.data_y[0][i] ** 2 + self.data_y[1][i] ** 2 + self.data_y[2][i] ** 2 for i in range(self.length)]
        self.r_max = math.sqrt(max(r_2))

        self.X = [[] for i in range(self.n)]
        self.Y = [[] for i in range(self.n)]
        self.Z = [[] for i in range(self.n)]
        self.T = [[] for i in range(self.n)]

        fig = plt.figure()
        self.ax = fig.add_subplot(111, projection='3d')

        self.t_anim = 0
        self.i = 0

        ani = anim.FuncAnimation(fig, animation, interval=100)
        plt.axis('scaled')  # ATTENTION CETTE LIGNE NE FONCTIONNE PAS SI ON UTILISE LA VERSION 3.1.0, 3.1.1, 3.1.2 de matplotlib, on espère qu'ils vont changer ca plus tard (en att on utilise 3.0.3)
        plt.show()

    def display_2D_animation(self, animation):
        self.update_graphics()
        self.length = len(self.data_t)
        r_2 = [self.data_y[0][i] ** 2 + self.data_y[1][i] ** 2 + self.data_y[2][i] ** 2 for i in range(self.length)]
        self.r_max = math.sqrt(max(r_2))

        self.X = [[] for i in range(self.n)]
        self.Y = [[] for i in range(self.n)]
        self.Z = [[] for i in range(self.n)]
        self.T = [[] for i in range(self.n)]

        fig = plt.figure()
        self.ax = fig.add_subplot(111)

        self.t_anim = 0
        self.i = 0

        ani = anim.FuncAnimation(fig, animation, interval=100)
        plt.xlim(-self.r_max * 1.1, self.r_max * 1.1)
        plt.ylim(-self.r_max * 1.1, self.r_max * 1.1)
        plt.axis('scaled')
        plt.show()

    def display_plane(self, show=True):
        self.update_graphics()
        r_0 = [self.data_y[0][0], self.data_y[1][0], self.data_y[2][0]]
        v_0 = [self.data_y[3][0], self.data_y[4][0], self.data_y[5][0]]
        e_r = r_0 / np.linalg.norm(r_0)
        e_v = v_0 / np.linalg.norm(v_0)
        plane = [[], []]

        for i in range(len(self.data_t)):
            r = [self.data_y[0][i], self.data_y[1][i], self.data_y[2][i]]
            a, b = np.dot(r, e_r), np.dot(r, e_v)
            plane[0].append(a)
            plane[1].append(b)

        rocket, = plt.plot(plane[0], plane[1], color='r', label='rocket trajectory')
        ax = plt.gca()
        earth = plt.Circle((0, 0), self.environment.r_earth)
        ax.add_artist(earth)
        ax.axis('scaled')
        # ax.set_aspect('equal', 'box')
        # ax.set_xlim(-self.r_max*1.1, self.r_max*1.1)
        # ax.set_ylim(-self.r_max*1.1, self.r_max*1.1)
        plt.legend(loc='upper right')
        if show:
            plt.show()

    def display_g(self, separate=False, useless=True, show=True):
        self.update_graphics()
        if not separate:
            plt.plot(self.computer.data_tg[0], self.computer.data_tg[1])
        else:
            if useless:
                n = 0
            else:
                n = 1
            for i in range(len(self.computer.separation_time) - (1 + n)):
                data_t = []
                data_g = []
                for j in range(len(self.computer.data_tg[0])):
                    if self.computer.separation_time[i] < self.computer.data_tg[0][j] < self.computer.separation_time[i + 1]:
                        data_t.append(self.computer.data_tg[0][j])
                        data_g.append(self.computer.data_tg[1][j])
                plt.plot(data_t, data_g)
        plt.title("Nombre de g que subit Jebediah Kerman durant le vol.")
        plt.xlabel("Temps(s)")
        plt.ylabel("Nombre de g (m/s²)")
        plt.grid()
        if show:
            plt.show()

    def display_h(self, separate=False, show=True):
        self.update_graphics()
        if not separate:
            plt.plot(self.data_t, [math.sqrt(self.data_y[0][i] ** 2 + self.data_y[1][i] ** 2 + self.data_y[2][i] ** 2) for i in range(self.length)])
        else:
            for i in range(len(self.computer.separation_time) - 1):
                data_t = []
                data_r = []
                for j in range(len(self.data_t)):
                    if self.computer.separation_time[i] < self.data_t[j] < self.computer.separation_time[i + 1]:
                        data_t.append(self.data_t[j])
                        data_r.append(math.sqrt(self.data_y[0][j] ** 2 + self.data_y[1][j] ** 2 + self.data_y[2][j] ** 2))
                plt.plot(data_t, data_r)
        plt.title("Coordonnées radiale lors du décolage en fonction du temps")
        plt.xlabel("Temps(s)")
        plt.ylabel("Distance au centre de la Terre (m)")
        if show:
            plt.show()

    def display_m(self, separate=False, useless=True, show=True):
        self.update_graphics()
        if not separate:
            plt.plot(self.data_t, self.data_y[6])
        else:
            if useless:
                n = 0
            else:
                n = 1
            for i in range(len(self.computer.separation_time) - (1 + n)):
                data_t = []
                data_m = []
                for j in range(len(self.data_t)):
                    if self.computer.separation_time[i] < self.data_t[j] < self.computer.separation_time[i + 1]:
                        data_t.append(self.data_t[j])
                        data_m.append(self.data_y[6][j])
                plt.plot(data_t, data_m)
        plt.title("Masse totale de la fusée en fonction du temps")
        plt.xlabel("Temps(s)")
        plt.ylabel("Masse(kg)")
        if show:
            plt.show()

    def display_void(self):
        """Affiche le meilleur graphique qu'il puisse existe, un graphique vide!!!!!!!!!!!!!!!!!!!
        """
        plt.plot([-1, -1, 1, 1], [-1, 1, 1, -1])

    def display_multiple_at_once(self, u=None, separate=False, useless=True, in_line=True):
        """Affiche plusieurs graphiques en un seul graphique.

        :param u: Liste de dimension n ou n*m (voir in_line) dont les élément sont des strings de type :
            "h" pour afficher la hauteur
            "plane" pour afficher la trajectoire de la fusée dans un plan
            "g" pour afficher les g que se prennent les astronautes
            "m" pour afficher l'évolution de la masse de la fusée dans le temps
            0 pour avoir un graphique vide (Wooohoooow trop bien!!! je sais que vous en reviez, en plus petite folie 0 n'est pas un string)

        :param separate: (False) Si True sépare les étages dans l'affichage, c'est juste parce que c'est joli

        :param useless: (True) Si True affiche les données sur tout le trajet, si False affiche uniquement lors du décolage
            Uniquement utile si separate = True.

        :param in_line: (True) Si True affiche tout en une ligne, u doit alors etre une liste de dimension n
            Si False, affiche les graphiques dans l'ordre donné par u et permet d'avoir plusieurs colonnes, pour n lignes et m colonnes il faut une liste de dimension n*m
            ex : pour 3 lignes et 2 colonnes : u = [[a, b], [c, d], [e, f]]

        :return: rien enfait techniquement
        """
        if u is None:
            print("C'est bien sympa d'essayer d'utiliser toutes nos fonctions mais c'est mieu quand on y met les bons arguments.")
            return 0
        if in_line:
            fig, ax = plt.subplots(1, len(u))
            for i in range(len(u)):
                plt.subplot(1, len(u), i+1)
                if len(u) < i:
                    self.display_void()
                elif u[i] == "h":
                    self.display_h(separate, False)
                elif u[i] == "m":
                    self.display_m(separate, useless, False)
                elif u[i] == "g":
                    self.display_g(separate, useless, False)
                elif u[i] == "plane":
                    self.display_plane(False)
        else:
            fig, ax = plt.subplots(len(u), len(u[0]))
            for i in range(len(u)):
                for j in range(len(u[i])):
                    plt.subplot(len(u), len(u[0]), i*len(u[0]) + j + 1)
                    if u[i][j] == 0:
                        self.display_void()
                    elif u[i][j] == "h":
                        self.display_h(separate, False)
                    elif u[i][j] == "m":
                        self.display_m(separate, useless, False)
                    elif u[i][j] == "g":
                        self.display_g(separate, useless, False)
                    elif u[i][j] == "plane":
                        self.display_plane(False)

        plt.show()

    def display_multiple_sequence(self, u=None, separate=False, useless=True):
        """Affiche plusieurs graphiques à la suite (ce qui sert techniquement presque a rien mais c'est pour la forme)

        :param u: Liste de dimension n dont les élément sont des strings de type :
            "h" pour afficher la hauteur
            "plane" pour afficher la trajectoire de la fusée dans un plan
            "g" pour afficher les g que se prennent les astronautes
            "m" pour afficher l'évolution de la masse de la fusée dans le temps
            0 pour avoir un graphique vide (Wooohoooow trop bien!!! je sais que vous en reviez, en plus petite folie 0 n'est pas un string)

        :param separate: (False) Si True sépare les étages dans l'affichage, c'est juste parce que c'est joli

        :param useless: (True) Si True affiche les données sur tout le trajet, si False affiche uniquement lors du décolage
            Uniquement utile si separate = True.

        :return: rien enfait techniquement
        """
        if u is None:
            print("C'est bien sympa d'essayer d'utiliser toutes nos fonctions mais c'est mieu quand on y met les bons arguments.")
            return 0
        for i in range(len(u)):
            if u[i] == "h":
                self.display_h(separate)
            elif u[i] == "m":
                self.display_m(separate, useless)
            elif u[i] == "g":
                self.display_g(separate, useless)
            elif u[i] == "plane":
                self.display_plane()
