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

#-----------------------------CLASSE POUR L'AFFICHAGE--------------------------#
class Graphics:
    def __init__(self, computer):
        self.x = []
        self.y = []
        self.z = []
        self.data_t = []
        self.data_y = []
        self.environment = computer.environment
        self.rocket = computer.rocket

    def animation(self,_):
        t_max = self.data_t[-1]
        while self.t_anim <= t_max - 1 and self.data_t[self.i] <= self.t_anim:
            self.x.append(self.data_y[0][self.i])
            self.y.append(self.data_y[1][self.i])
            self.z.append(self.data_y[2][self.i])
<<<<<<< HEAD
            self.i += 3

        self.t_anim += 30
=======
            self.i += 1

        self.t_anim += 10
>>>>>>> abeb66741760c6beffac0c3cf6a78324f45a2847

        self.ax.clear()

        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]     #technique allègrement volée ici https://stackoverflow.com/questions/11140163/plotting-a-3d-cube-a-sphere-and-a-vector-in-matplotlib
        x_earth = self.environment.r_earth*np.cos(u + self.environment.freq_rot*2*math.pi*self.t_anim)*np.sin(v)
        y_earth = self.environment.r_earth*np.sin(u + self.environment.freq_rot*2*math.pi*self.t_anim)*np.sin(v)
        z_earth = self.environment.r_earth*np.cos(v)
        #self.ax.plot_surface(x_earth, y_earth, z_earth, rstride=1, cstride=1, cmap='magma', alpha = 0.5)
<<<<<<< HEAD
        self.ax.plot_wireframe(x_earth, y_earth, z_earth, color='b', alpha = 0.5)
=======
        self.ax.plot_surface(x_earth, y_earth, z_earth, color='b', alpha = 0.5)
>>>>>>> abeb66741760c6beffac0c3cf6a78324f45a2847

        self.ax.set_xlim(-self.r_max*1.1, self.r_max*1.1)
        self.ax.set_ylim(-self.r_max*1.1, self.r_max*1.1)
        self.ax.set_zlim(-self.r_max*1.1, self.r_max*1.1)

<<<<<<< HEAD
        self.ax.plot(self.x, self.y, self.z, color = 'r')
=======
        self.ax.plot(self.x, self.y, self.z)
>>>>>>> abeb66741760c6beffac0c3cf6a78324f45a2847

    def display_animation(self, data_t, data_y):
        self.data_t = data_t
        self.data_y = data_y
        self.lenght = len(self.data_t)
        r_2 = [data_y[0][i]**2 + data_y[1][i]**2 + data_y[2][i]**2 for i in range(self.lenght)]
        self.r_max = math.sqrt(max(r_2))

<<<<<<< HEAD
        fig = plt.figure()
=======
        fig = plt.figure(figsize=plt.figaspect(0.8)*2)
>>>>>>> abeb66741760c6beffac0c3cf6a78324f45a2847
        self.ax = fig.add_subplot(111, projection='3d')

        self.t_anim = 0
        self.i = 0

        ani = anim.FuncAnimation(fig, self.animation, interval = 100)
        #Writer = anim.writers['ffmpeg']
        #writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        #ani.save('gif animation_1.mp4', writer=writer)
<<<<<<< HEAD
        plt.axis('scaled')
        plt.show()

    def display_plane(self): #la fonction doit etre lancée après display_animation pour l'instant
        r_0 = [self.data_y[0][0], self.data_y[1][0], self.data_y[2][0]]
        v_0 = [self.data_y[3][0], self.data_y[4][0], self.data_y[5][0]]
        e_r = r_0/np.linalg.norm(r_0)
        e_v = v_0/np.linalg.norm(v_0)
        plane = [[], []]

        for i in range(len(self.data_t)):
            r = [self.data_y[0][i], self.data_y[1][i], self.data_y[2][i]]
            a, b = np.dot(r, e_r), np.dot(r, e_v)
            plane[0].append(a)
            plane[1].append(b)

        rocket, = plt.plot(plane[0], plane [1], color = 'r', label = 'rocket trajectory')
        ax = plt.gca()
        earth = plt.Circle((0,0), self.environment.r_earth)
        ax.add_artist(earth)
        ax.axis('scaled')
        #ax.set_aspect('equal', 'box')
        #ax.set_xlim(-self.r_max*1.1, self.r_max*1.1)
        #ax.set_ylim(-self.r_max*1.1, self.r_max*1.1)
        plt.legend(loc='upper right')
=======
>>>>>>> abeb66741760c6beffac0c3cf6a78324f45a2847
        plt.show()
