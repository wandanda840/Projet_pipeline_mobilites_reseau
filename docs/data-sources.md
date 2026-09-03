# Sources de données

Le réseau STAR (exploité par Keolis pour Rennes Métropole) publie ses données
en open data selon deux standards internationaux complémentaires.

## GTFS (statique) vs GTFS-RT (temps réel)

| | GTFS (statique) | GTFS-RT (temps réel) |
|---|---|---|
| Contenu | L'offre théorique : lignes, arrêts, courses, horaires prévus | L'état réel : position des véhicules, retards constatés, perturbations |
| Format | Archive ZIP de fichiers CSV | Flux binaire Protocol Buffers |
| Fréquence | Une publication par nuit | Rafraîchissement de l'ordre de la dizaine de secondes |
| Volume | Quelques dizaines de Mo | Quelques centaines de ko par appel |
| Rôle dans le projet | Référentiel de comparaison | Flux d'événements à ingérer |

Le retard n'existe dans aucune des deux sources : le GTFS dit ce qui devait
arriver, le GTFS-RT dit où sont les bus maintenant. La ponctualité réelle du
réseau doit être calculée en confrontant les deux univers.

## Accès

| Ressource | URL |
|---|---|
| GTFS statique (version en cours) | `https://eu.ftp.opendatasoft.com/star/gtfs/GTFS_STAR_BUS_METRO_EN_COURS.zip` |
| GTFS-RT positions véhicules | `https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-vehicle-position` |
| GTFS-RT mises à jour de courses | `https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-trip-update` |
| Portail open data | `https://data.rennesmetropole.fr` |

L'ancien jeu de données REST (position des bus en circulation) est en cours
de dépréciation ; l'exploitant recommande l'usage des flux GTFS-RT, mieux
rafraîchis et synchronisés avec le GTFS en vigueur.

## Précaution d'usage

Ces services sont publics et gratuits. Les appels doivent être espacés
raisonnablement et les réponses brutes sauvegardées en local pendant le
développement, pour ne pas solliciter inutilement l'infrastructure (voir
`src/ingestion/position_vehicule.py`, qui sauvegarde chaque appel dans
`local_data/`).

## Fraîcheur observée du flux GTFS-RT

Mesurée en comparant l'horodatage véhicule de deux appels successifs (voir
`src/ingestion/position_vehicule.py`).

| Période | Écart moyen observé |
|---|---|
| Après-midi | ~10 secondes |
| Soir | ~15 secondes |

Le flux se rafraîchit en moyenne toutes les 10 secondes en journée, ce qui
valide la fréquence de polling retenue pour l'ingestion.


## Volumétrie observée

Mesurée sur la taille du message protobuf désérialisé (`feed.SerializeToString()`)
d'un appel au flux GTFS-RT positions véhicules (voir
`src/ingestion/position_vehicule.py`).

| Métrique | Valeur |
|---|---|
| Taille moyenne d'un appel | ~29,35 Ko (29 352 octets) |
| Fréquence de polling | 1 appel / 10 s → 6/min, 360/h, 8 640/jour |
| Volume journalier estimé | ~253,7 Mo |
| Volume mensuel estimé | ~7,6 Go |
| Volume annuel estimé | ~91,2 Go |

Le stockage brut n'est donc pas un facteur limitant pour ce flux, même sur
une rétention longue. 

À nuancer car le calcul à été fait sur une heure de forte affluence.
Il y a aura moins de données par exemple tard la nuit mais ce qu'on cherche c'est un ordre de grandeur. ce résultat reste néanmoins dans la marge haute de la prévision d'occupation d'espace.
