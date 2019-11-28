#CLASSE MODELISANT TOUT L ENVIRONNEMENT DE VOL
class environnement :
    def __init__(self, r_earth, kappa, gk, L_B, T_0):
        self.r_earth = r_earth
        self.kappa   = kappa
        self.gk      = gk
        self.L_B     = L_B
        self.T_0     = T_0

    def air_density(self, h)
