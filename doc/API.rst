Le but de cette page est de décrire comment fonctionne l’API du projet,
c’est-à-dire de donner :

-  la liste des types requêtes possibles
-  le contenu des requêtes et des réponses
-  le comportement en cas de réponse invalide

.. contents::


Généralités
===========

L’API utilise un websocket pour toutes ses requêtes. Il est situé à l’adresse
suivante : ``api.arenaoftitans.com``. Toutes les informations sont transmises
suivant le format JSON.

Si le serveur ne peut pas exécuter la requête, une “alert” s’affiche pour
l’utilisateur ou l’erreur est logguée dans la console javascript.  Les erreurs
affichées sont celles susceptibles d’avoir été provoquées par l’utilisateur.


Liste des types de requêtes
===========================

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
--------------------------

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

ADD_SLOT
--------

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
--------------------------------

#. Lorsque le joueur ajoute un slot, le serveur lui renvoie les paramètres du
   nouveau slot si tout c’est bien passé.
#. Lorque qu’un joueur modifie un slot (modification du status, ajout du nom,
   …), il fait cette requête au serveur. Tous reçoivent une requête de même type
   avec les paramètres mis à jour. Cela permet à l'investigateur de la requête
   qu'elle est correctement passée par le serveur.

Client vers serveur
~~~~~~~~~~~~~~~~~~~

   -  Ajout du nom ou changement de statut : le client renvoie tout le JSON et
      le serveur répond ce même JSON à tous.

      .. literalinclude:: api/requests/update_slot.json
         :language: json
         :linenos:


Serveur vers clients
~~~~~~~~~~~~~~~~~~~~

   -  Joueur rejoins

      .. sourcecode:: json

	 {
	     "rt": "SLOT_UPDATED",
	     "player_name": "Player 2",
	     "player_id": "ac0f2fa7-9d1f-400f-8f5f-c7be0cb050ce",
	     "index": 1,
	     "state": "TAKEN"
	 }

   -  Changement de status

      .. sourcecode:: json

	 {
	     "rt": "SLOT_UPDATED",
	     "player_name": "",
	     "index": 3,
	     "state": "RESERVED"
	 }

CREATE\_GAME
------------

Cette requête est effectuée quand le joueur principal décide de créer la partie
avec les joueurs présents.

#. Client vers serveur

   .. sourcecode:: json

      {
          "rt": "CREATE_GAME",
	  "player_id": "253f8902-0aa7-4c34-8f2c-f736bb5bf673",
	  "create_game_request": [
	     {
	         "name": "Player 1",
		 "index": 0
	     },
	     {
	         "name": "Player 2",
		 "index": 1
	     }
	  ]
      }

#. Serveur vers clients (tous, y compris celui qui a fait la requête)

   .. sourcecode:: json

      {
          "rt": "CREATE_GAME",
	  "nextPlayer": {
	      "index": 0,
	      "name": "Player 1"
	  },
	  "possibleCardsNextPlayer": [
	      {
	          "color": "BLUE",
		  "name": "Queen"
	      },
	      {
	          "color": "RED",
		  "name": "Wizard"
	      },
	      {
                  "color":"YELLOW",
		  "name":"Queen"
	      },
	      {
                  "color":"BLUE",
		  "name":"Wizard"
	     },
	     {
	         "color":"BLUE",
		 "name":"Warrior"
	     }
	  ],
	  "gameOver":false,
	  "winners":[],
	  "trumpsNextPlayer":[
	     {
	         "name":"Reinforcements",
		 "description":"Allow the player to play one more move.",
		 "duration":0,
		 "cost":0,
		 "repeatForEachColor":false,
		 "mustTargetPlayer":false
	     },
	     {
                 "name":"Tower BLACK",
		 "description":"Prevent the player to move on some colors.",
		 "duration":0,
		 "cost":0,
		 "repeatForEachColor":false,
		 "mustTargetPlayer":true
	     },
	     {
	         "name":"Tower BLUE",
		 "description":"Prevent the player to move on some colors.",
		 "duration":0,
		 "cost":0,
		 "repeatForEachColor":false,
		 "mustTargetPlayer":true
	     },
	     {
                 "name":"Tower RED",
		 "description":"Prevent the player to move on some colors.",
		 "duration":0,
		 "cost":0,
		 "repeatForEachColor":false,
		 "mustTargetPlayer":true
	     },
	     {
                 "name":"Tower YELLOW",
		 "description":"Prevent the player to move on some colors.",
		 "duration":0,
		 "cost":0,
		 "repeatForEachColor":false,
		 "mustTargetPlayer":true
	     }
	  ],
	  "players": [
	     {
                 "index":0,
		 "name":"Player 1"
	     },
	     {
                 "index":1,
		 "name":"Player 2"
	     }
	  ],
	  "trumps": [
	     {
                 "playerIndex":0,
		 "playerName":"Player 1",
		 "trumpNames": []
	     },
	     {
                 "playerIndex":1,
		 "playerName":"Player 2",
		 "trumpNames":[]
	     }
	  ]
      }


VIEW_POSSIBLE_SQUARES
---------------------

Cette requête est effectée lorsqu’un joueur clique sur une carte et pour la
réponse du serveur.

#. Client

   .. sourcecode:: json

      {
          "rt":"VIEW_POSSIBLE_SQUARES",
	  "player_id":"39272e3f-2616-493a-a1a1-fed24a355f22",
	  "play_request": {
	     "card_name":"King",
	     "card_color":"RED"
	  }
      }

#. Réponse serveur (à tous)

   .. sourcecode:: json

      {
          "possible_squares": [
	     "square-0-7"
	  ],
	  "rt":"VIEW_POSSIBLE_SQUARES"
      }

PLAY
----

Cette requête est effectuée lorsqu’un joueur clique sur une case sur laquelle il
peut se déplacer, s’il passe son tour ou s’il se défausse d’une carte.

-  Déplacement :

   #. Client

      .. sourcecode:: json

	 {
	      "rt": "PLAY",
	      "player_id":"39272e3f-2616-493a-a1a1-fed24a355f22",
	      "play_request": {
	          "card_name": "King",
		  "card_color": "RED",
		  "x": 0,
		  "y": 7
	      }
	 }

   #. Réponse serveur

      .. sourcecode:: json

	 {
	     "newSquare": {
	         "x": 0,
		 "y": 7
	     },
	     "nextPlayer": {
	          "index": 0,
		  "name": "Player 1"
	     },
	     "possibleCardsNextPlayer": [
		{
		    "color": "RED",
		    "name": "Bishop"
		},
		{
		    "color": "BLACK",
		    "name": "Bishop"
		},
		{
		    "color": "BLUE",
		    "name": "Knight"
		},
		{
		    "color": "RED",
		    "name": "Warrior"
		}
	     ],
	     "gameOver": false,
	     "winners": [],
	     "trumpsNextPlayer":[
		{
                   "name": "Reinforcements",
		   "description": "Allow the player to play one more move.",
		   "duration": 0,
		   "cost": 0,
		   "repeatForEachColor": false,
		   "mustTargetPlayer": false
		},
		{
         	   "name":"Tower BLACK",
		   "description":"Prevent the player to move on some colors.",
		   "duration":0,
		   "cost":0,
		   "repeatForEachColor":false,
		   "mustTargetPlayer":true
		},
		{
	          "name":"Tower BLUE",
		  "description":"Prevent the player to move on some colors.",
		  "duration":0,
		  "cost":0,
		  "repeatForEachColor":false,
		  "mustTargetPlayer":true
		},
		{
		  "name":"Tower RED",
	          "description":"Prevent the player to move on some colors.",
		  "duration":0,
		  "cost":0,
		  "repeatForEachColor":false,
		  "mustTargetPlayer":true
		},
		{
		  "name":"Tower YELLOW",
		  "description":"Prevent the player to move on some colors.",
		  "duration":0,
		  "cost":0,
		  "repeatForEachColor":false,
		  "mustTargetPlayer":true
		}
	     ],
	     "players":[
		{
		  "index":0,
		  "name":"Player 1"
		},
		{
		  "index":1,
		  "name":"Player 2"
		},
		{
	          "index":2,
		  "name":"Player 3"
		}
	     ],
	     "trumps": [
		{
		  "playerIndex":0,
		  "playerName":"Player 1",
		  "trumpNames":[]
		},
		{
		  "playerIndex":1,
		  "playerName":"Player 2",
		  "trumpNames":[]
		},
		{
		  "playerIndex":2,
		  "playerName":"Player 3",
		  "trumpNames":[]
		}
	     ],
	     "rt":"PLAY"
	 }

-  Passe son tour

   #. Client

      .. sourcecode:: json

	 {
		"rt":"PLAY",
		"player_id":"253f8902-0aa7-4c34-8f2c-f736bb5bf673",
		"play_request":{
		    "pass":true
		}
	 }

   #. Réponse serveur : idem

-  Défausse

   #. Client

      .. sourcecode:: json

	 {
		"rt":"PLAY",
		"player_id":"39272e3f-2616-493a-a1a1-fed24a355f22",
		"play_request": {
		    "discard":true,
		    "card_name":"Warrior",
		    "card_color":"RED"
		}
	 }

   #. Réponse server : idem

PLAY_TRUMP
----------

Cette requête est effectuée lorsqu’un joueur joue un atout et pour la réponse du
serveur.

-  Atout qui n’a pas besoin d’avoir un joueur cible

   #. Client

      .. sourcecode:: json

	 {
		"rt":"PLAY_TRUMP",
		"player_id":"253f8902-0aa7-4c34-8f2c-f736bb5bf673",
		"trump_request":{
		    "target_index":null,
		    "name":"Reinforcements"
		}
	 }

   #. Réponse du serveur

      .. sourcecode:: json

	 {
		"rt":"PLAY_TRUMP",
		"play_trump":[
		  {
		      "playerIndex":0,
		      "playerName":"Player 1",
		      "trumpNames":["Reinforcements"]
		  },
		  {
		      "playerIndex":1,
		      "playerName":"Player 2",
		      "trumpNames":[]
		  }
		]
	 }

- Atout qui doit avoir un joueur cible

  #. Client

     .. sourcecode:: json

	{
	       "rt":"PLAY_TRUMP",
	       "player_id":"253f8902-0aa7-4c34-8f2c-f736bb5bf673",
	       "trump_request":{
	           "target_index":1,
		   "name":"Tower BLACK"
	       }
	}

   #. Réponse du serveur

      .. sourcecode:: json

	 {
		"rt":"PLAY_TRUMP",
		"play_trump":[
		  {
		      "playerIndex":0,
		      "playerName":"Player 1",
		      "trumpNames":["Reinforcements"]
		  },
		  {
		      "playerIndex":1,
		      "playerName":"Player 2",
		      "trumpNames":["Tower BLACK"]
		  }
		]
	 }
