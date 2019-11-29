#CLASSE MODELISANT TOUT L ENVIRONNEMENT DE VOL
class Environnement :
    def __init__(self, r_earth, kappa, gk, L_B, T_0, rho_0 = 1.225, T_rot = 86164):
        self.r_earth = r_earth
        self.kappa   = kappa
        self.gk      = gk
        self.L_B     = L_B
        self.T_0     = T_0
        self.rho_0   = rho_0
        self.T_rot   = T_rot
        self.freq_rot  = 1/T_rot

    def air_density(self, rayon):
        h = rayon - r_earth
        exp = 1-self.gk/self.L_B
        rho = rho_0*(self.T_0/(self.T_0-self.L_B*h))**exp

        return rho
