import math
import scipy.integrate as ode
import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from fusee import *
from environnement import *

#-----------------------------CLASSE QUI PERMET D'EFFECTUER TOUS LES CALCULS ET DE LES AFFICHER--------------------------#
class Computer:
    def __init__(self):
        self.rocket = Rocket()
        self.rocket.create_soyuz()

        self.environment = Environment()

        self.solution = []
        self.test = 0

    def coord_to_rad(self, position):
        new_pos = [position[0]*math.pi/180, position[1]*math.pi/180]

        return new_pos

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

    def radial_velocity(self, theta_phi, v):
        """input la vitesse en coordonnées cartésienne [v_x, v_y, v_z] et les angles theta/phi [theta, phi] et return la vitesse radial v_rad"""
        V   = np.array(v)
        rad = np.array([math.cos(theta_phi[0])*math.cos(theta_phi[1]), math.cos(theta_phi[0])*math.sin(theta_phi[1]), math.sin(theta_phi[0])])
        v_rad = np.dot(V, rad)

        return v_rad

    def earth_rotation_velocity(self, position):
        """Converti la position données en coordonnées sphériques pour le transformer en vitesse initiale due à la rotation de la Terre en coordonnées cartésiennes"""
        r     = self.environment.r_earth*math.cos(position[0])
        omega = 2*math.pi*self.environment.freq_rot*r
        v_x   = -omega*math.sin(position[1])
        v_y   =  omega*math.cos(position[1])

        return [v_x, v_y, 0]

    def wind_velocity(self, position):
        """Converti la position donnees en coordonn�es sph�riques pour retourner la vitesse du vent en coordonnees cartesiennes"""
        r     = position[0]*math.cos(position[1])
        omega = 2*math.pi*self.environment.freq_rot*r
        v_x   = -omega*math.sin(position[2])
        v_y   =  omega*math.cos(position[2])

        return [v_x, v_y, 0]

    def radial_launch(self, t, X):
        """fonction a implementer dans RK-45 pour un lancement purement radiale"""
        #sortie des coordoonées, vitesses et masse
        x   = X[0]
        y   = X[1]
        z   = X[2]
        v_x = X[3]
        v_y = X[4]
        v_z = X[5]
        M   = X[6]

        #calcul des coordonnées sphériques
        S     = self.convert_CS([x,y,z])
        r     = S[0]
        theta = S[1]
        phi   = S[2]

        #calcul de la vitesse radiale
        v_rad = self.radial_velocity([theta, phi], [v_x, v_y, v_z])
        #.....
        v_pot = math.sqrt(2*self.environment.G*self.environment.M_earth*abs(1/(self.environment.r_earth+400000) - 1/r))
        if v_rad >= v_pot:
            self.test = 1
        if r > self.environment.r_earth+400000-0.7 and r < self.environment.r_earth+400000+0.7:
            print("v_x =", v_x, "   v_y =", v_y, "   v_z =", v_z, "     v =", math.sqrt(v_x**2 + v_y**2 + v_z**2))
        #-------------------------------------------

        #calcul de la vitesse du vent
        V = self.wind_velocity(S)

        #calcul de la vitesse de la fusée relative au vent
        v_xrel = v_x - V[0]
        v_yrel = v_y - V[1]
        v_zrel = v_z - V[2] #ici V[2] = 0 mais utile si un jour ca change

        v_rel = math.sqrt(v_xrel**2 + v_yrel**2 + v_zrel**2)

        #calcul de la densité de l'air
        if r < self.environment.r_earth + 45000:
            rho = self.environment.air_density(r)
        else:
            rho = 0

        #calcul de la variation de masse
        dM = -self.rocket.C - self.rocket.C_boost
        """
        #calcul de l'accélération
        a1 = self.rocket.P/M - (self.environment.G * self.environment.M_earth)/(r**2)
        a_x = a1*math.cos(theta)*math.cos(phi) - rho*v_rel*self.rocket.C_A*v_xrel/(2*M)
        a_y = a1*math.cos(theta)*math.sin(phi) - rho*v_rel*self.rocket.C_A*v_yrel/(2*M)
        a_z = a1*math.sin(theta) - rho*v_rel*self.rocket.C_A*v_zrel/(2*M)
        """
        if self.test != 1:
            a1 = self.rocket.P/M - (self.environment.G * self.environment.M_earth)/(r**2)
        else:
            a1 = - (self.environment.G * self.environment.M_earth)/(r**2)
        a_x = a1*math.cos(theta)*math.cos(phi) - rho*v_rel*self.rocket.C_A*v_xrel/(2*M)
        a_y = a1*math.cos(theta)*math.sin(phi) - rho*v_rel*self.rocket.C_A*v_yrel/(2*M)
        a_z = a1*math.sin(theta) - rho*v_rel*self.rocket.C_A*v_zrel/(2*M)

        return np.array([v_x, v_y, v_z, a_x, a_y, a_z, dM])
    
    def launch(self, position):
        """gère le lancement de la fusée"""
        angles = self.coord_to_rad(position)
        X = self.convert_init(angles)
        V = self.earth_rotation_velocity(angles)
        Y = X + V
        Y = Y + [0]
        self.rocket.update()

        for i in range(len(self.rocket.stage)-1):
            Y[6] = self.rocket.M
            T = self.rocket.stage_time()
            self.solution.append(ode.solve_ivp(self.radial_launch, (0,T), Y, vectorized = False, max_step = T/1000))

            self.rocket.decouple()

            for j in range(6):
                Y[j] = self.solution[i].y[j][-1]

            #print(math.sqrt(sum([self.solution[i].y[j][-1]**2 for j in range(3)])) - self.environment.r_earth)  #calcul juste la hauteur si pour debug (+flem de l'enlever si rebesoin)
        self.display()


    def display(self):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        x_earth = self.environment.r_earth*np.cos(u)*np.sin(v)
        y_earth = self.environment.r_earth*np.sin(u)*np.sin(v)
        z_earth = self.environment.r_earth*np.cos(v)
        #ax.plot_surface(x_earth, y_earth, z_earth, rstride=1, cstride=1, cmap='magma', edgecolor='none')
        ax.plot_wireframe(x_earth, y_earth, z_earth, color='b')

        for sol in self.solution:
            ax.plot(sol.y[0], sol.y[1], sol.y[2])

        plt.show()



        #DEBUG ZONE -------------------------------------------------------------------------------------------------------------------------
        
        for sol in self.solution:
            plt.plot(sol.t, sol.y[3])
        plt.show()

        delta_t = 0
        for sol in self.solution:
            plt.plot(sol.t + delta_t, np.sqrt(sol.y[0]**2 + sol.y[1]**2+sol.y[2]**2)-self.environment.r_earth)
            delta_t += sol.t[-1]
        plt.title('h')
        plt.show()

        delta_t = 0 #c'est juste pour vérifier la masse
        for sol in self.solution:
            plt.plot(sol.t + delta_t, sol.y[6])
            delta_t += sol.t[-1]
        plt.show()
        


self = Computer()
self.launch([45, 0])


