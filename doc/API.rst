API
===

L’API utilise un websocket pour toutes ses requêtes. Il est situé à l’adresse
suivante : ``api.last-dev.com``. Toutes les informations sont transmises
suivant le format JSON.

Si le serveur ne peut pas exécuter la requête, une “alert” s’affiche pour
l’utilisateur ou l’erreur est logguée dans la console javascript.  Les erreurs
affichées sont celles susceptibles d’avoir été provoquées par l’utilisateur.
