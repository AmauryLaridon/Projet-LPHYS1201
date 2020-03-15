import math
import numpy as np
import matplotlib.pyplot as plt

import scipy.integrate as sc

G = 6.67408e-11

class Planet:
    def __init__(self, m, r, x_vect, v_vect, athm=False):
        self.m = m
        self.r = r
        self.X = np.concatenate((x_vect, v_vect), axis=None)
        self.athm = athm

    def planet_motion_componant(self, f_vect, i):
        dX = np.concatenate(([self.X[i] for i in range(3, 6)], np.array(f_vect)/self.m), axis=None)
        return dX[i]

class Univers:
    def __init__(self, planets):
        self.planets = planets
        self.n = len(self.planets)

    def planetary_motion(self, t, planets_X):
        X = planets_X.reshape(self.n, 6)
        dX = np.array([[0. for k in range(6)] for i in range(self.n)])
        a_G = np.array([[0. for k in range(3)] for i in range(self.n)])
        for i, planet1 in enumerate(X):
            for j, planet2 in enumerate(X):
                if i != j:
                    r_vect = np.array([X[i][k] - X[j][k] for k in range(0, 3)])
                    r = np.linalg.norm(r_vect)
                    for k in range(3):
                        a_G[i][k] += - G * self.planets[j].m * r_vect[k] / r**3
            dX[i] = np.concatenate(([X[i][k] for k in range(3, 6)], a_G[i]), axis=None)
        return np.reshape(dX, (1, 6 * self.n))

terre = Planet(5.972e24, 6.371e6, [0, 0, 0], [0, 0, 0])
lune = Planet(7.3477e22, 1.736e6, [4e8, 0, 0], [0, 1e3, 0])
univers = Univers([terre, lune])
solution = sc.solve_ivp(univers.planetary_motion, (0, 40*3600*24), np.concatenate((terre.X, lune.X), axis=None), max_step=40*3600*24 / 1000, dense_output=True)
plt.plot(solution.y[0], solution.y[1], label="Earth")
plt.plot(solution.y[6+0], solution.y[6+1], label="Moon")
plt.xlim(-4e8*1.2, 4e8*1.2)
plt.ylim(-4e8*1.2, 4e8*1.2)
plt.legend()
plt.show()