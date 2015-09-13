Classement des joueurs
======================

Après plusieurs recherches, je me suis rendu compte que, quasiment partout,
c’était le classement elo qui était utilisé. Faudra qu’on rediscute des
problèmes qu’il peut poser mais a priori, ça va être compliqué de faire un truc
vraiment différent car c’est déjà assez compliqué de comprendre le classement
elo de base mathématiquement. Je vous explique vite fait en quoi il consiste.


.. contents::


Classement elo
--------------

Principe pour 2 joueurs
~~~~~~~~~~~~~~~~~~~~~~~

Quand on commence notre première partie, on part avec un nombre de points elo
moyen puis ce nombre augmente lorsqu’on gagne et diminue lorsqu’on perd.

On gagne d’autant plus de points que notre adversaire est fort par rapport à
nous (qd on gagne) :

- si on bat un adversaire qui a moins de points elo que nous, on gagne d’autant
  plus de points elo que son classement est proche du notre.
- si on bat un adversaire qui a plus de points elo que nous, on gagne d’autant
  plus de points elo que son classement est grand par rapport au nôtre.

C’est le même principe si on perd puisque le nombre de points que gagne le
vainqueur est égal au nombre de points perdus par le perdant.

Les mathématiques qu’il y a derrière
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le but final du classement elo est qu’il représente le niveau des
joueurs. Intuitivement, la courbe statistique du niveau des joueurs est une
gaussienne alors on veut que la courbe statistique s’approche d’une gaussienne.

On cherche à exprimer la probabilité d’un joueur de gagner contre un autre en
fonction de la différence entre leurs classements elo. Pour ça, on a plutôt
cherché à exprimer l’inverse, la différence de classement D en fonction de la
proba de gagner d’un joueur contre un autre p.

On a trois joueurs A,B et C et on note :

- :math:`q = P(A / B)` la probabilité de gain de A contre B.
- :math:`r = P(B / C)` la probabilité de gain de B contre C.
- :math:`p = P(A / C)` la proba de gain de A contre C.

Le rapport f(p)=p/(1-p) exprime la force relative d’un joueur par rapport à un
autre. On a :

.. math::

   \frac{p}{1 - p} = \frac{q}{1 - q} \times \frac{r}{1 - r}

On a une fonction f tq f(p) = f(q)*f(r) mais on une fonction D tq l’écart de
force entre A et C soit égal à l’écart entre A et B plus l’écart entre B et C,
ie D(p) = D(q) + D(r).

On voit qu’on a besoin de la fonction log :

.. math::

   D(q) = 400 \times \log (\frac{p}{1 - p})

(400 est un facteur multiplicatif sur lequel on peut jouer)

Finalement,

.. math::

   p(D) = \frac{1}{1 + 10^{\frac{-D}{400}}}

Voici maintenant la formule pour calculer le nouveau classement après une
partie :

.. math::

   E_{n+1} = E_n + K \times (W - p(D))

Avec :

- En : classement elo
- K : facteur qui dépend du nombre de parties jouées (on peut choisir)
- W : résultat de la partie (1 pour une victoire, 0.5 pour un nul et 0 pour une
  défaite)
- Rq : p(D) représente en fait le résultat attendu pour cette partie au vu de la
  différence de classement entre les 2 joueurs


Conclusion
~~~~~~~~~~

Trucs qui restent à faire :

- regarder comment transposer ça à une partie à plus de 2 joueurs
-  Faut-il montrer ce classement aux joueurs ou plutôt faire un système du type débutant-confirmé-expert suivant dans quelle tranche du classement elo on se trouve ? ou les deux ?
- voir quelle valeur on donne au coeff sur lesquels on peut jouer.
- réfléchir à comment implanter ça informatiquement
