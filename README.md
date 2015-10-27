# Commande à distance du robot aspirateur Neato XV-25 avec un Raspberry Pi

## Avant propos et objectifs

Voilà quelques temps que je suis l'heureux possesseur du robot aspirateur Neato XV-25.

Sur les conseils de mon ami milk et souhaitant acheter un robot de qualité, efficace contre les poils de chat, pas trop bruyant et pouvant être programmé par un port facilement accessible (USB), je suis ravi de ce choix.

Son utilisation est simple, pour lancer un nettoyage (comme la majorité des robots aspirateurs ) il faut programmer un horaire de nettoyage par jour de la semaine.

Le problème à l'usage, c'est qu'il arrive de temps en temps d'oublier de le programmer, et de se dire une fois sortis de chez soi, “mince j'aurais du le programmer pour qu'il aspire maintenant” !

L'idée est donc d'ajouter une fonctionnalité qui permettrait de le lancer en direct à distance via Internet mais aussi de changer le planning via un site web.

Pour cela je vais utiliser un mini ordinateur Raspberry Pi (RPI) en Wifi, connecté en USB à l'aspirateur et via son API lancer des nettoyages.

Les possibilités de cette API sont multiples (déplacement des moteurs, valeurs des capteurs, etc..), on peut facilement imaginer créer un robot en utilisant le socle du XV-25 pour faire tout autre chose, mais mon objectif consiste à garder sa fonction principale : passer l'aspirateur !
