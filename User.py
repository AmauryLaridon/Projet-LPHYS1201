from fusee import *
from environnement import *
from graphics import *
from computer import *

# exemple d'utilisation
rocket = Rocket()
rocket.create_soyuz_mod()

pc = Computer(rocket)
#Mettre les coordonnées géographique de la zone de lancement souhaitée.
pc.launch([5, -52])

GUI = Graphics(pc)
GUI.display_3D_animation(GUI.animation)
GUI.display_2D_animation(GUI.animation_2D)
GUI.display_multiple_at_once([["plane", "h"], ["g", "m"]], True, False, False)
