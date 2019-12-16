import math

# --------------------CLASSE MODELISANT TOUT L ENVIRONNEMENT DE VOL---------------- #
class Environment:
    def __init__(self, G=6.6743e-11, M_earth=5.972e24, r_earth=6371000, gk=0.03417429, L_B=0.0065, T_0=288.15, rho_0=1.225, T_rot=86164):
        """Initialise l'environnement dans lequel la fusée va évoluer, par défaut les paramètres sont fixés sur ceux de la Terre"""
        self.G = G
        self.M_earth = M_earth
        self.r_earth = r_earth
        self.gk = gk
        self.L_B = L_B
        self.T_0 = T_0
        self.rho_0 = rho_0
        self.T_rot = T_rot
        self.freq_rot = 1 / T_rot

    def air_density(self, r):
        h = r - self.r_earth
        if self.T_0 - self.L_B * h > 0:
            exp = 1 - self.gk / self.L_B
            rho = self.rho_0 * (self.T_0 / abs(self.T_0 - self.L_B * h)) ** exp
        else:
            rho = 0

        return rho

    def US_standart(self, r): # http://www.braeunig.us/space/atmmodel.htm#table4
        # en vrai ca change presque rien dutout...
        R = 287.053
        h = (r - self.r_earth)/1000
        if h <= 11:
            T = 288.15 - 6.5 * h
            exp = -34.1632/6.5
            P = 101325 * (288.15/(288.15 - 6.5 * h))**exp
        elif h <= 20:
            T = 216.65
            exp = -34.1632 * (h - 11) / 216.65
            P = 22632.06 * math.e ** exp
        elif h <= 32:
            T = 196.65 + h
            exp = 34.1632
            P = 5474.889 * (216.65/(216.65 + (h - 20))) ** exp
        elif h <= 47:
            T = 139.05 + 2.8 * h
            exp = 34.1632/2.8
            P = 868.0187 * (228.65 / (228.65 + 2.8 * (h - 32))) ** exp
        elif h <= 51:
            T = 270.65
            exp = -34.1632 * (h-47)/270.65
            P = 110.9063 * math.e ** exp
        elif h <= 71:
            T = 413.45 - 2.8 * h
            exp = -34.1632 / 2.8
            P = 66.93887 * (270.65 / (270.65 - 2.8 * (h - 51))) ** exp
        elif h <= 84.852:
            T = 356.65 - 2.0 * h
            exp = -34.1632 / 2
            P = 3.956420 * (214.65 / (214.65 - 2 * (h - 71))) ** exp
        else :
            T = 1
            exp = 1
            P = 0
        rho = P / (R * T)
        return rho

    def Earth(self):
        self.G = 6.6743e-11
        self.M_earth = 5.972e24
        self.r_earth = 6371000
        self.gk = 0.03417429
        self.L_B = 0.0065
        self.T_0 = 288.15
        self.rho_0 = 1.22
        self.T_rot = 86164
        self.freq_rot = 1 / self.T_rot

        print("Earth is now the environment")

    def Kerbin(self):
        self.G = 6.6743e-11
        self.M_earth = 5.2915e22
        self.r_earth = 600000
        self.gk = 0.03417429
        self.L_B = 0.0065
        self.T_0 = 288.15
        self.rho_0 = 1.22
        self.T_rot = 21549
        self.freq_rot = 1 / self.T_rot

        print("Kerbin is now the environment")
