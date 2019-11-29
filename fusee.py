import math
import scipy

#CLASSE DECRIVANT LES DONNEES D UN ETAGE
class Stage:
    def __init__(self, M_vide, M_fuel, P, C_A, C, name):
        self.M_vide   = M_vide
        self.M_fuel   = M_fuel
        self.P        = P
        self.C_A      = C_A
        self.C        = C
        self.name     = name
#CLASSE DECRIVANT LA FUSEE UTILISEE
class Fusee :
    def __init__(self):
        self.M        = 0
        self.P        = 0
        self.C_A      = 0
        self.C        = 0
        self.C_boost  = 0
        self.stage    =[]

    def ajouter_module(self, M_vide, M_fuel, P, C_A, C, stage_name):
        new_stage = Stage( M_vide, M_fuel, P, C_A, C, stage_name)
        self.stage.append(new_stage)
        self.M += new_stage.M_vide + new.stage.M_fuel

    def update(self):
        if self.stage[-1].name == 'booster' :
            self.P       = self.stage[-1].P + self.stage[-2].P
            self.C_A     = self.stage[-1].C_A + self.stage[-2].C_A
            self.C       = self.stage[-2].C
            self.C_boost = self.stage[-1].C

        elif self.stage[-1].name != 'payload' :
            self.P       = self.stage[-1].P
            self.C_A     = self.stage[-1].C_A
            self.C       = self.stage[-1].C

    def launch(self, position, environnement):
        X = convert_init(position, environnement)
        V = initial_velocity(position, environnement)
        Z = [X,Y]
        self.update()

    def decoupling(self):
        self.M -= self.stage[-1].M_vide
        self.stage.pop()
        self.update()

    def stage_time(self):
        t_stage = self.stage[-1].M_fuel/self.stage[-1].C
        return t_stage

    def convert_init(self, position, environnement):
        #Convertis les coordonnées sphériques en coordonnées cartésiennes à l'initialisation
        x = environnement.r_earth*math.cos(position[0])*math.cos(position[1])
        y = environnement.r_earth*math.cos(position[0])*math.sin(position[1])
        z = environnement.r_earth*math.sin(position[0])

        return np.array([x,y,z])

    def convert(self, position):
        #Convertis les coordonnées sphériques en coordonnées cartésiennes en général pour les calculs
        r = math.sqrt(sum([x_i**2 for x_i in position]))
        x = r*math.cos(position[0])*math.cos(position[1])
        y = r*math.cos(position[0])*math.sin(position[1])
        z = r*math.sin(position[0])

        return np.array([x,y,z])

    def initial_velocity(self, position, environnement):
        #Convertire la position données en coordonnées sphériques pour le transformer en
        #vitesse initiale du à la rotation de la Terre
        r = environnement.r_earth*math.cos(position[0])
        v = 2*math.pi*environnement.freq_rot*r
        v_x = -v*math.sin(position[1])
        v_y =  v*math.cos(position[1])

        return np.array([v_x, v_y, 0])

    def affichage(self):
        pass
