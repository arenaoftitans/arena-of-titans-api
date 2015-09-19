API
===

Le but de cette page est de décrire comment fonctionne l’API du projet,
c’est-à-dire de donner :

-  la liste des types requêtes possibles
-  le contenu des requêtes et des réponses
-  le comportement en cas de réponse invalide

.. contents::


Généralités
-----------

L’API utilise un websocket pour toutes ses requêtes. Il est situé à l’adresse
suivante : ``api.arenaoftitans.com``. Toutes les informations sont transmises
suivant le format JSON.

Si le serveur ne peut pas exécuter la requête, une “alert” s’affiche pour
l’utilisateur ou l’erreur est logguée dans la console javascript.  Les erreurs
affichées sont celles susceptibles d’avoir été provoquées par l’utilisateur.


Liste des types de requêtes
---------------------------

::

    init_game: 'INIT_GAME'
    game_initialized: 'GAME_INITIALIZED'
    add_slot: 'ADD_SLOT'
    slot_updated: 'SLOT_UPDATED'
    create_game: 'CREATE_GAME'
    view: 'VIEW_POSSIBLE_SQUARES'
    play: 'PLAY'
    play_trump: 'PLAY_TRUMP'

Elles sont stockées dans l’enum ``aot.api.utils.RequestType`` et dans le
controller du jeu en JavaScript dans l’objet rt.

Sans précision, les requêtes sont faîtes du client vers le serveur. Les requêtes
sont ici décrite dans l'ordre dans lequel elles se passent lors d'un jeu.

INIT_GAME/GAME_INITIALIZED
~~~~~~~~~~~~~~~~~~~~~~~~~~

Création du jeu
+++++++++++++++

Requête permettant d'initialiser le jeu. Le client fait cette requête afin
d'obtenir un nouvel identifiant de jeu généré par le serveur.

1. Client

  .. literalinclude:: api/requests/init_game.json
     :language: json
     :linenos:

2. Serveur

  .. literalinclude:: api/responses/init_game.json
     :language: json
     :linenos:

3.  Réponse du client : ADD_SLOT.

Rejoindre le jeu
++++++++++++++++

Requête permettant de rejoindre le jeu.

1. Client

   .. literalinclude:: api/requests/join_game.json
      :language: json
      :linenos:

2. Serveur

   .. literalinclude:: api/responses/join_game.json
      :language: json
      :linenos:

3. Autres joueurs

   .. literalinclude:: api/responses/join_game_other_players.json
      :language: json
      :linenos:

ADD_SLOT
~~~~~~~~

Une fois le jeu initialisé, le client ajoute les 2 slots initiaux avec des
requêtes ADD_SLOT. Cette requête est aussi faite lorsque l’utilisateur clique
sur ajouter un joueur.

1. Client

   .. literalinclude:: api/requests/add_slot.json
      :language: json
      :linenos:

-  Réponse du serveur : SLOT_UPDATED

   .. literalinclude:: api/responses/add_slot.json
      :language: json
      :linenos:

SLOT_UPDATED (client ou serveur)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Lorsque le joueur ajoute un slot, le serveur lui renvoie les paramètres du
   nouveau slot si tout c’est bien passé.
#. Lorque qu’un joueur modifie un slot (modification du status, ajout du nom,
   …), il fait cette requête au serveur. Tous reçoivent une requête de même type
   avec les paramètres mis à jour. Cela permet à l'investigateur de la requête
   qu'elle est correctement passée par le serveur.

Client vers serveur
+++++++++++++++++++

   -  Ajout du nom ou changement de statut : le client renvoie tout le JSON et
      le serveur répond ce même JSON à tous.

      .. literalinclude:: api/requests/update_slot.json
         :language: json
         :linenos:


CREATE_GAME
~~~~~~~~~~~

Cette requête est effectuée quand le joueur principal décide de créer la partie
avec les joueurs présents.

1. Client vers serveur

   .. literalinclude:: api/requests/create_game.json
      :language: json
      :linenos:


2. Serveur vers clients : chaque client reçoit une réponse personnalisée avec
   ses cartes et ses atouts.

   .. literalinclude:: api/responses/create_game.json


VIEW_POSSIBLE_SQUARES
---------------------

Cette requête est effectée lorsqu’un joueur clique sur une carte et pour la
réponse du serveur.

#. Client

   .. literalinclude:: api/requests/view_possible_squares.json
      :language: json
      :linenos:

#. Réponse serveur (à tous)

   .. literalinclude:: api/responses/view_possible_squares.json
      :language: json
      :linenos:

PLAY
~~~~

Cette requête est effectuée lorsqu’un joueur clique sur une case sur laquelle il
peut se déplacer, s’il passe son tour ou s’il se défausse d’une carte.

-  Déplacement :

   #. Client

      .. literalinclude:: api/requests/play_card.json
         :language: json
         :linenos:

   #. Réponse serveur

      .. literalinclude:: api/responses/play_card.json
         :language: json
         :linenos:


-  Passe son tour

   #. Client

      .. literalinclude:: api/requests/pass_turn.json
         :language: json
         :linenos:

   #. Réponse serveur : idem

-  Défausse

   #. Client

      .. literalinclude:: api/requests/discard_card.json
         :language: json
         :linenos:

   #. Réponse server : idem

La requête PLAY est systématiquement suivie pour tous les joueurs d'une requête
PLAYER_MOVED qui donne la nouvelle case du joueur qui vient de jouer.

.. literalinclude:: api/responses/player_moved.json
   :language: json
   :linenos:


PLAY_TRUMP
~~~~~~~~~~

Cette requête est effectuée lorsqu’un joueur joue un atout et pour la réponse du
serveur.

-  Atout qui n’a pas besoin d’avoir un joueur cible

   #. Client

      .. literalinclude:: api/requests/play_trump_no_target.json
            :linenos:
            :language: json

   #. Réponse du serveur

      .. literalinclude:: api/responses/play_trump_no_target.json
            :linenos:
            :language: json

- Atout qui doit avoir un joueur cible

  #. Client

     .. literalinclude:: api/requests/play_trump_with_target.json
            :linenos:
            :language: json

  #. Réponse du serveur

     .. literalinclude:: api/responses/play_trump_with_target.json
            :linenos:
            :language: json
