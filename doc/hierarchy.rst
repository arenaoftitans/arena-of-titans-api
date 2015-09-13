Hiérarchie des cartes
=====================

On remarque que la hiérarchie n’est pas une relation d’ordre car non transitive
:

M>C et C>F mais M<F

Donc, je ne pense pas qu’on va pouvoir l’implémenter à l’aide d’un seul nombre
(car ils suivent une relation d’ordre).

Mon idée (Robin) :

- A = (4,0)
- R = (3,0)
- D = (2,0)
- M = (1,-1)
- F = (1,0)
- C = (1,1)
- G = (0,0)

H : hiérarchie

#. Si h’=h ou h’[1]<>h[1], facile
#. Sinon, on regarde la deuxième coordonnée
#. Si h’[2] et h[2] ont le même signe, alors on les compare normalement
#. Sinon, on fait l’inverse
