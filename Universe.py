import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from mpl_toolkits.mplot3d import Axes3D
import scipy.integrate as sc

plt.style.use('dark_background')

G = 6.67408e-11
N = 100  # number of point to draw the ellipse


def angle(cos, sin, error=0.001):
    #fonctionne pas surper bien, math.atan2 c'est beacoup mieux
    if 1 < cos <= 1 + error:
        cos = 1
    if -1 - error < cos <= -1:
        cos = -1
    if 1 < sin <= 1 + error:
        sin = 1
    if -1 - error < sin <= -1:
        sin = -1
    acos = math.acos(cos)
    asin = math.asin(sin)
    if asin - error <= acos <= asin + error:
        return acos
    elif math.pi / 2 < acos and 0 < asin:
        return 2 * math.pi - acos
    elif math.pi / 2 < acos:
        return acos
    else:
        return asin


class Planet:
    def __init__(self, m, r, x_vect, v_vect, athm=False):
        self.m = m
        self.r = r
        self.X = np.concatenate((x_vect, v_vect), axis=None)
        self.athm = athm

    def planet_motion_componant(self, f_vect, i):
        dX = np.concatenate(([self.X[i] for i in range(3, 6)], np.array(f_vect) / self.m), axis=None)
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
                        a_G[i][k] += - G * self.planets[j].m * r_vect[k] / r ** 3
            dX[i] = np.concatenate(([X[i][k] for k in range(3, 6)], a_G[i]), axis=None)
        return np.reshape(dX, (1, 6 * self.n))

    def animation(self, _):
        self.ax.clear()
        self.ax.axis('scaled')
        self.ax.set_xlim(-4e8 * 1.2, 4e8 * 1.2)
        self.ax.set_ylim(-4e8 * 1.2, 4e8 * 1.2)
        self.ax.set_zlim(-4e8 * 1.2, 4e8 * 1.2)

        mu = (sum([(planet.m) ** (-1) for planet in self.planets])) ** (-1)
        # centre de masse
        cm = np.array([self.planets[1].m * self.planets[1].X[i] + self.planets[0].m * self.planets[0].X[i] for i in range(3)]) / sum([planet.m for planet in self.planets])
        alpha = G * self.planets[0].m * self.planets[1].m

        r_vect = np.array([self.planets[1].X[i] - self.planets[0].X[i] for i in range(3)])
        r = np.linalg.norm(r_vect)
        dr_vect = np.array([self.planets[1].X[i] - self.planets[0].X[i] for i in range(3, 6)])
        e_r = r_vect / r
        L_vect = mu * np.cross(r_vect, dr_vect)
        L = np.linalg.norm(L_vect)
        e_l = L_vect / L
        e_theta = np.cross(e_l, e_r)
        dr = np.dot(dr_vect, e_r)

        p = L ** 2 / (alpha * mu)
        E = 0.5 * mu * dr ** 2 - alpha / r + L ** 2 / (2 * mu * r ** 2)
        e = math.sqrt(1 + 2 * p * E / alpha)

        theta = math.atan2(dr * mu * p / (e * L), (p / r - 1) / e)
        phi = np.linspace(-math.pi, math.pi, num=N)
        r_ellipse = [np.cos(phi) * p * e_r[i] / (1 + e * np.cos(theta + phi)) + np.sin(phi) * p * e_theta[i] / (1 + e * np.cos(theta + phi)) for i in range(3)]

        plt.plot(cm[0] + mu * r_ellipse[0] / self.planets[0].m, cm[1] + mu * r_ellipse[1] / self.planets[0].m, cm[2] + mu * r_ellipse[2] / self.planets[0].m)
        plt.plot(cm[0] + mu * r_ellipse[0] / self.planets[1].m, cm[1] + mu * r_ellipse[1] / self.planets[1].m, cm[2] + mu * r_ellipse[2] / self.planets[1].m)

        dt = 3600
        solution = sc.solve_ivp(univers.planetary_motion, (0, dt), np.concatenate((terre.X, lune.X), axis=None), max_step=dt / 40)
        for i, planet in enumerate(self.planets):
            planet.X = np.array([solution.y[j][-1] for j in range(i*6, (i+1)*6)])
        self.ax.scatter3D([planet.X[0] for planet in self.planets], [planet.X[1] for planet in self.planets], [planet.X[2] for planet in self.planets], c='r', depthshade=False)

        print(theta)

    def display(self):
        fig = plt.figure(dpi=300)
        self.ax = fig.add_subplot(111, projection='3d')

        ani = anim.FuncAnimation(fig, self.animation, interval=100)
        plt.show()

    def save(self):
        fig = plt.figure(dpi=300)
        self.ax = fig.add_subplot(111, projection='3d')

        Writer = anim.writers['ffmpeg']
        writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=1500)

        ani = anim.FuncAnimation(fig, self.animation, interval=100, frames=400)
        ani.save('ok_wtf.mp4', writer=writer)  # si jamais tu a ffmpeg
        plt.show()


terre = Planet(5.972e24, 6.371e6, [0, 0, 0], [0, 0, 0])
lune = Planet(7.3477e22, 1.736e6, [4e8, 0, 0], [0, 1e3*0.7, 0])
univers = Univers([terre, lune])
"""
solution = sc.solve_ivp(univers.planetary_motion, (0, 40 * 3600 * 24), np.concatenate((terre.X, lune.X), axis=None), max_step=40 * 3600 * 24 / 1000, dense_output=True)
print([solution.y[i][-1] for i in range(6*2)])
plt.plot(solution.y[0], solution.y[1], label="Earth")
plt.plot(solution.y[6 + 0], solution.y[6 + 1], label="Moon")
plt.xlim(-4e8 * 1.2, 4e8 * 1.2)
plt.ylim(-4e8 * 1.2, 4e8 * 1.2)
plt.legend()
plt.show()
"""
univers.display()