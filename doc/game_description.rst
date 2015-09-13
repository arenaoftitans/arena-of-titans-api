Description du jeu
==================

Cette page décrit comment doit être écrit le fichier JSON qui représente le
jeu. Ce fichier doit donc contenir pour chaque version du jeu :

-  Les informations sur les cartes de mouvements.
-  Les informations sur les cartes atouts.
-  Les informations sur le plateau.

Un exemple complet qui ne contient que le jeu de base est fourni à la fin.

.. contents::


Jeux
----

Chaque jeu est identifé par son nom. Ce nom sert de clé dans le fichier JSON
principal.


Plateau
-------

À la clé *board* on associe le dictionnaire décrivant le plateau. Il contient
les entrées :

-  *number_arms* (int)
-  *arms_width*\ (int)
-  *arms_length* (int)
-  *inner_circle_colors* : Liste de string représentant les couleurs à répéter
   sur une ligne.

   -  **Exemple :**

      .. literalinclude:: ../aot/resources/games/standard.json
         :language: json
         :linenos:
         :lines: 80-84
         :dedent: 4

      Dans cet exemple, ``YELLOW,YELLOW,BLACK,BLACK,BLACK,BLACK,YELLOW,YELLOW``
      représente la liste des couleurs à répéter sur la première ligne (idem
      pour les autres éléments).

-  *arm_colors* : Liste de string représentant les couleurs à répéter sur
   un bras (même principe que pour *circle_colors*).

   -  **Exemple :**

      .. literalinclude:: ../aot/resources/games/standard.json
         :language: json
         :linenos:
         :lines: 85-92
         :dedent: 4

-  *svg* : objet décrivant le svg.

svg
~~~

L’objet associé à la clé *svg* est constitué des éléments suivants :

- *rotationCenter* : String donnant les coordonnées du centre de rotation
   concaténée.

   -  **Exemple :** ``"rotation_center": "985,985"``

- *fillOrigin* : String donnant les coordonnées du point à partir duquel on
   commence à remplir le plateau avec un même élément basique.

   -  **Exemple :** ``"fill_origin": "808,1516"``

- *fill* : Dictionnaire décrivant l’élément utilisé pour remplir le plateau.

   -  **Exemple :**

      .. sourcecode:: json

	 "fill": {"tag": "rect", "height": "90", "width": "89"}

- *lines* : Liste donnant pour chaque ligne la liste des éléments qu’elle
   contient.

lines
+++++

Les éléments sont décrits par un dictionnaire comme suit :

- *tag* : le tag de l’élément.
- *d* : comment tracer l’élément.

Exemple
```````

.. literalinclude:: ../aot/resources/games/standard.json
   :language: json
   :linenos:
   :lines: 101-174
   :dedent: 4

Cet exemple contient deux lignes. Chacune de ces lignes contient trois
éléments.


Cartes de mouvements
--------------------

À la clé *movementsCards* on associe le dictionnaire constitué des clés
suivantes :

- *number_cards_per_color* (int) : nombre de carte pour chaque couleur.
- *cards* : la liste des dictionnaires décrivant les cartes.

  - *number_of_movements* : le nombre de mouvements possibles.
  - *movements_type* : List de strings donnant le type de mouvements.
  - Types supportés :

    - *line*
    - *diagonal*
    - *knight*

  - *additional_movements_colors* (facultatif) : Liste de Strings donnant les cases
    sur lesquelles la carte peut aller en plus de sa couleur.
  - *complementary_colors* : Dictionnaire donnant pour chaque couleur une liste
    de couleurs supplémentaire sur lesquelles la carte peut aller.

Exemple pour la clé *cards*
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../aot/resources/games/standard.json
   :language: json
   :linenos:
   :lines: 6-49
   :dedent: 4

Atouts
------

À la clé *trumps* on associe la liste des dictionnaires décrivant les
cartes. Ces dictionnaires contiennent les clés suivantes :

- *name* : le nom de l’atout.
- *description* : une description plus détaillée de l’atout.
- *cost* (int) : le coût de l’atout.
- *duration* (int) : le nombre de tour pendant lequel l’atout est valide.
- *repeat_for_each_color* (bool) : si à vrai, alors une version de l’atout est crée
  pour chaque couleur.
- *must_target_player* (bool) : si à vrai, on doit choisir un joueur cible pour
  l’atout.
- *type* : dictionnaire donnant le type (qui doit correspondre à une classe
  Java) et les paramètres spécifiques à ce type.

Exemple pour la clé *trumps*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../aot/resources/games/standard.json
   :language: json
   :linenos:
   :lines: 51-75
   :dedent: 4

Liste des types disponibles et leurs paramètres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ModifyNumberOfMovesInATurnTrump
+++++++++++++++++++++++++++++++

Ajoute ou enlève des mouvements pour les tours pendant lesquels il est
valide. Paramètre :

- *delta_of_moves* (int) : le nombre de mouvements à ajouter ou enlever.

RemovingColorTrump
++++++++++++++++++

Empêche le joueur d’aller sur les cases de couleurs données. Paramètre :

- *additionnalColors* (list) : la liste des couleurs sur lesquelles le joueur ne
  peut pas aller en plus de la couleur actuelle. Si *repeatForEachColor* n’est
  pas présent ou est à faux, seule cette liste est prise en compte.


Couleurs
--------

À la clé *colors* on associe la liste des couleurs possibles. Ces
couleurs sont en anglais sous forme de string et écrites en majuscule.
La “couleur” *ALL* qui correspont à n’importe quelle couleur est ajoutée
automatiquement.

**Exemple :** ``"colors": ["YELLOW", "RED"]``


Exemple complet
---------------

.. literalinclude:: ../aot/resources/games/standard.json
   :language: json
   :linenos:
