import math
import scipy.integrate as ode
import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from fusee import *
from environnement import *

#-----------------------------CLASSE QUI PERMET D EFFECTUER TOUS LES CALCULS ET DE LES AFFICHER--------------------------#
class Computer:
    def __init__(self):
        self.rocket = Rocket()
        self.rocket.create_soyuz()

        self.environment = Environment()

        self.t_solved = []
        self.x_solved = []

    def convert_init(self, position):
        """Converti les coordonnées spheriques en coordonnées cartésiennes a l'initialisation"""
        x = self.environment.r_earth*math.cos(position[0])*math.cos(position[1])
        y = self.environment.r_earth*math.cos(position[0])*math.sin(position[1])
        z = self.environment.r_earth*math.sin(position[0])

        return [x,y,z]

    def convert_SC(self, position):
        """Converti les coordonnées sphériques en coordonnées cartésiennes [r, theta, phi]"""
        x = position[0]*math.cos(position[1])*math.cos(position[2])
        y = position[0]*math.cos(position[1])*math.sin(position[2])
        z = position[0]*math.sin(position[1])

        return [x,y,z]

    def convert_CS(self, position):
        """Converti les coordonnées cartésiennes en coordonnées sphériques"""
        r = math.sqrt(sum([x_i**2 for x_i in position]))

        if position[0] == 0 and position[1] >= 0:
            phi = math.pi/2
        elif position[0] == 0:
            phi = 3*math.pi/2
        else:
            phi = math.atan2(position[1], position[0])
        if position[0]**2 + position[1]**2 == 0:
            theta = math.pi/2 * math.copysign(1, position[2])
        else:
            theta = math.atan2(position[2], math.sqrt(position[0]**2 + position[1]**2))

        return [r,theta,phi]

    def earth_rotation_velocity(self, position):
        """Converti la position données en coordonnées sphériques pour le transformer en vitesse initiale due à la rotation de
           la Terre en coordonnées cartésiennes"""
        r     = self.environment.r_earth*math.cos(position[0])
        omega = 2*math.pi*self.environment.freq_rot*r
        v_x   = -omega*math.sin(position[1])
        v_y   =  omega*math.cos(position[1])

        return [v_x, v_y, 0]

    def wind_velocity(self, position):
        """Converti la position donnees en coordonnées sphériques pour retourner la vitesse du vent en coordonnees cartesiennes"""
        r     = position[0]*math.cos(position[1])
        omega = 2*math.pi*self.environment.freq_rot*r
        v_x   = -omega*math.sin(position[2])
        v_y   =  omega*math.cos(position[2])

        return [v_x, v_y, 0]

    def radial_launch(self, t, X):
        """fonction a implementer dans RK-45 pour un lancement purement radiale"""
        x   = X[0]
        y   = X[1]
        z   = X[2]
        v_x = X[3]
        v_y = X[4]
        v_z = X[5]
        M   = X[6]

        S     = self.convert_CS([x,y,z])
        r     = S[0]
        theta = S[1]
        phi   = S[2]

        #print(r-self.environment.r_earth)

        V = self.wind_velocity(S)

        v_xrel = v_x - V[0]
        v_yrel = v_y - V[1]
        v_zrel = v_z - V[2] #ici V[2] = 0 mais utile si un jour ca change

        v_rel = math.sqrt(v_xrel**2 + v_yrel**2 + v_zrel**2)

        if r < self.environment.r_earth + 45000:
            rho = self.environment.air_density(r)
        else:
            rho = 0

        dM = -self.rocket.C
        #print(M)
        #implémentation d'une partie de l'équation du mouvement ne prenant ici qu'en compte le poids de la fusée et la pousée
        a1 = self.rocket.P/M - (self.environment.G * self.environment.M_earth)/(r**2)
        #définis les accélérations selon les coordonnées cartésiennes en prenant en compte les frottements
        a_x = a1*math.cos(theta)*math.cos(phi) - rho*v_rel*self.rocket.C_A*v_xrel/(2*M)
        a_y = a1*math.cos(theta)*math.sin(phi) - rho*v_rel*self.rocket.C_A*v_yrel/(2*M)
        a_z = a1*math.sin(theta) - rho*v_rel*self.rocket.C_A*v_zrel/(2*M)

        return np.array([v_x, v_y, v_z, a_x, a_y, a_z, dM])

    def launch(self, position):
        X = self.convert_init(position)
        V = self.earth_rotation_velocity(position)
        Y = X + V
        Y = Y + [0]
        solution = []
        self.rocket.update()

        for i in range(len(self.rocket.stage)-1):
            Y[6] = self.rocket.M
            T = self.rocket.stage_time()
            solution.append(ode.solve_ivp(self.radial_launch, (0,T), Y, vectorized = False, max_step = T/1000))
            self.rocket.M -= self.rocket.stage[-1].M_fuel
            self.rocket.decoupling()
            Y[0] = solution[i].y[0][-1]
            Y[1] = solution[i].y[1][-1]
            Y[2] = solution[i].y[2][-1]
            Y[3] = solution[i].y[3][-1]
            Y[4] = solution[i].y[4][-1]
            Y[5] = solution[i].y[5][-1]

        fig = plt.figure()
        ax = fig.gca(projection='3d') # changement de coordonnées
        #ax.scatter3D(solution.y[0], solution.y[1], solution.y[2])
        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        x_earth = self.environment.r_earth*np.cos(u)*np.sin(v)
        y_earth = self.environment.r_earth*np.sin(u)*np.sin(v)
        z_earth = self.environment.r_earth*np.cos(v)
        #ax.plot_surface(x_earth, y_earth, z_earth, rstride=1, cstride=1, cmap='magma', edgecolor='none')
        ax.plot_wireframe(x_earth, y_earth, z_earth, color='b')

        """
        L = len(solution.y[0])
        n = int((L-L)
        print(n)
        x = [solution.y[0][100*i] for i in range(n)]
        y = [solution.y[1][100*i] for i in range(n)]
        z = [solution.y[2][100*i] for i in range(n)]
        print(len(x), len(y), len(z))
        ax.scatter3D(x, y, z)
        """
        for sol in solution:
            ax.scatter3D(sol.y[0], sol.y[1], sol.y[2])


        plt.show()

        #debug zone

        #plt.plot(solution.t, solution.y[3])
        #plt.show()
        #plt.plot(solution.t, solution.y[4])
        #plt.show()
        for sol in solution:
            plt.plot(sol.y[0], sol.y[3])
        plt.show()  #ici on voit bien le problème de transitions entre 1er booster (bleu) et l'étage suivant (jaune)

        delta_t = 0 #c'est juste pour vérifier la masse
        for sol in solution:
            plt.plot(sol.t + delta_t, sol.y[6])
            delta_t += sol.t[-1]
        plt.show()


        """
    def fct_RK_4(self, fonction, t, x, dt):
        k_1 = fonction(t, x)
        k_2 = fonction(t + dt/2, x + dt/2 * k_1)
        k_3 = fonction(t + dt/2, x + dt/2 * k_2)
        k_4 = fonction(t + dt, x + dt * k_3)
        return (k_1 + 2 * k_2 + 2 * k_3 + k_4)/6
    def RK_4(self, fonction, t, x, t_end, dt, first = False):
        if first:
            self.t_solved.append(t)
            self.x_solved.append(x)
        while t < t_end:
            x = x + dt * self.fct_RK_4(fonction, t, x, dt)
            t += dt
            self.t_solved.append(t)
            self.x_solved.append(x)
    def launch(self, position):
        X = self.convert_init(position)
        V = self.earth_rotation_velocity(position)
        Y = X + V
        Y = Y + [0]

        for i in range(len(self.rocket.stage)-1):
            Y[6] = self.rocket.M
            self.rocket.update()
            T = self.rocket.stage_time()
            self.RK_4(self.radial_launch, 0, Y, T, 1)
            self.decouple()
          """


self = Computer()
self.launch([1, 2])
