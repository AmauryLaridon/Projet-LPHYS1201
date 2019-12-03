#--------------------CLASSE MODELISANT TOUT L'ENVIRONNEMENT DE VOL----------------#
class Environment :
    def __init__(self, G = 6.6743e-11, M_earth = 5.972e24, r_earth = 6371000, gk = 0.03417429, L_B = 0.0065, T_0 = 288.15, rho_0 = 1.225, T_rot = 86164):
        self.G       = G
        self.M_earth = M_earth
        self.r_earth = r_earth
        self.gk      = gk
        self.L_B     = L_B
        self.T_0     = T_0
        self.rho_0   = rho_0
        self.T_rot   = T_rot
        self.freq_rot  = 1/T_rot

    def air_density(self, rayon):
        h = rayon - self.r_earth
        exp = 1-self.gk/self.L_B
        rho = self.rho_0*(self.T_0/abs(self.T_0-self.L_B*h))**exp


        return rho
