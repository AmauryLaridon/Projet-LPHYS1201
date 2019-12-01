import math
import scipy.integrate as ode
import numpy as np
import matplotlib.pyplot as plt

from fusee import *
from environnement import *


class Computer:
    def __init__(self):
        self.rocket = Rocket()
        self.rocket.create_soyuz()

        self.environment = Environment()

    def convert_init(self, position):
        """Converti les coordonnees spheriques en coordonnees cartesiennes a l'initialisation"""
        x = self.environment.r_earth*math.cos(position[0])*math.cos(position[1])
        y = self.environment.r_earth*math.cos(position[0])*math.sin(position[1])
        z = self.environment.r_earth*math.sin(position[0])

        return [x,y,z]

    def convert_SC(self, position):
        """Converti les coordonnees sph�riques en coordonnees cartesiennes [r, theta, phi]"""
        x = position[0]*math.cos(position[1])*math.cos(position[2])
        y = position[0]*math.cos(position[1])*math.sin(position[2])
        z = position[0]*math.sin(position[1])

        return [x,y,z]

    def convert_CS(self, position):
        """Converti les coordonnees cartesiennes en coordonn�es spheriques"""
        r = math.sqrt(sum([x_i**2 for x_i in position]))
        if position[0] == 0:
            phi = math.pi/2 * math.copysign(1, position[1])
        else:
            phi = math.atan(position[1]/position[0])
        if position[0]**2 + position[1]**2 == 0:
            theta = math.pi/2 * math.copysign(1, position[2])
        else:
            theta = math.atan(position[2]/math.sqrt(position[0]**2 + position[1]**2))

        return [r,theta,phi]

    def earth_rotation_velocity(self, position):
        """Converti la position donnees en coordonn�es sph�riques pour le transformer en vitesse initiale due a la rotation de la Terre en coordonnees cartesiennes"""
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
        x   = X[0]
        y   = X[1]
        z   = X[2]
        v_x = X[3]
        v_y = X[4]
        v_z = X[5]

        S     = self.convert_CS([x,y,z])
        r     = S[0]
        theta = S[1]
        phi   = S[2]

        V = self.wind_velocity(S)

        v_xrel = v_x - V[0]
        v_yrel = v_y - V[1]
        v_zrel = v_z - V[2] #ici V[2] = 0 mais utile si un jour ca change

        v_rel = math.sqrt(v_xrel**2 + v_yrel**2 + v_zrel**2)

        rho = self.environment.air_density(r)

        a1 = self.rocket.P - (self.environment.G * self.environment.M_earth * self.rocket.M)/(r**2)

        a_x = a1*math.cos(theta)*math.cos(phi) - rho*v_rel*self.rocket.C_A*v_xrel/(2*self.rocket.M)
        a_y = a1*math.cos(theta)*math.sin(phi) - rho*v_rel*self.rocket.C_A*v_yrel/(2*self.rocket.M)
        a_z = a1*math.sin(phi) - rho*v_rel*self.rocket.C_A*v_zrel/(2*self.rocket.M)

        return np.array([v_x, v_y, v_z, a_x, a_y, a_z])

    def launch(self, position):
        X = self.convert_init(position)
        V = self.earth_rotation_velocity(position)
        Z = X + V
        self.rocket.update()
        for i in range(len(self.rocket.stage)-1):
            T = self.rocket.stage_time()
            solution = ode.RK45(self.radial_launch, 0, Z, T, vectorized = True)
            print(solution)


a = Computer()
a.launch([0,0])