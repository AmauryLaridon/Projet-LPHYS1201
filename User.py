from fusee import *
from environnement import *
from graphics import *
from computer import *
from parameters import *

# exemple d'utilisation
rocket = Rocket()
rocket.create_soyuz_mod()

pc = Computer(rocket)
pc.launch([0, 0])

GUI = Graphics(pc)
GUI.display_3D_animation(GUI.animation2)
GUI.display_2D_animation(GUI.animation_2D)
GUI.display_multiple_at_once([["plane", "h"], ["g", "m"]], True, False, False)
