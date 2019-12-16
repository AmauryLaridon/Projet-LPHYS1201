# Projet-LPHYS1201
Lancement d'une fusée en orbite basse
--------------------------------------------------------------------------------------------------------------------------
Bienvenue dans ce programme permettant de simuler la mise en orbite basse d'une fusée !
Ce programme se veut le plus modulable possible afin que selon les désirs de l'utilisateurs celui-ci puisse lancer la fusée
de ses rêves sur la planète de ses désirs bien que la Terre et la fusée Soyuz soient mises en place par défault.

Parce que lancer une fusée ne se fait pas en appuyant simplement sur une pédale et en tournant un volant, il est important
de lire ce texte afin de bien respecter les procédures et consignes inhérentes à notre programme.

Tout d'abord, un bref apercu sur la structure des fichers. Ils sont aux nombres de quatre :
  
  - environnement.py : Contient la classe définissant l'envirronnement de vol utilisé. Vous pouvez allègrement modifié les
                       paramètres de la planète si vous le désirez mais attention, la mise en orbite fonctionne pour les 
                       données de la Terre par défault et non pour celle d'une gravité et d'une masse digne de Saturne !
                       
  - fusee.py         : Contient la classe Stage ainsi que la classe Rocket qui attention flash news ! Implémente les données
                       de la fusée souhaitée. La fonction add_stage permet de construire votre propre fusée là ou des fonctions
                       prédéfinies donnent la possibilité de génerer une fusée Soyuz, une Falcon 9, Falcon Heavy et Saturne V.
                       
  - graphics.py      : Pas très passionnant contient les définitions des fonctions qui vous permettent de remplir votre rétine 
                       de beaux visuels représentant votre vol !
                     
  - computer.py      : Véritable cerveau algorithmique modélisant votre vol. Si vous souhaitez lancer une autre fusée vous devez
                       simplement changé dans l'initialisation de computer l'appel de la fonction de construction de la fusée.
                       De plus si vous souhaitez changer la zone de lancement vous devez simplement donner les coordonnées géo-
                       graphiques de votre jardin si tel est votre désir, suivant la convention latitude/longitude en degré bien
                       sûr ! Cette classe créera également automatiquement un fichier csv nommé "flight_data.csv" comportant
                       la télémétrie de votre premier vol. 
                       
                       ATTENTION :
                       Si vous exécuter plusieurs fois le programme en voulant par exemple changer de fusée et que vous souhai-
                       tez obtenir la télémtrie de ce nouveau vol vous devez supprimer vous même le fichier "flight_data.csv" 
                       du premier vol. En effet il a été choisi de n'enregistrer que les données du premier vol afin de ne pas
                       surcharger le temps de calcul et d'écriture.
                       
Afin de lancer le tout vous devez simplement télécharger chacun des fichiers dans le même répertoire et exécuter le fichier
computer.py


Quelques règles (qui défient la logique)) à respecter si vous construiser votre fusée avec la fonction add_stage :

1) Les étages de la fusée doivent être catégorisés avec soit :"booster", "stage", "payload".
2) On ne peut avoir des boosters sans avoir un étage attaché à ceux-ci.
3) Il est obligé d'avoir une "payload" en haut de la fusée. (Même Elon Musk il lance au moins sa voiture plutôt que rien du tout.)


Le lien du rapport de ce projet détaillant plus en profondeur certaines parties peut être trouvé à l'adresse suivante:

LIEN URL
