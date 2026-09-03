# Glossaire

## Formats et protocoles

- **GTFS** (General Transit Feed Specification) — standard mondial de
  description d'une offre de transport public (lignes, arrêts, horaires
  théoriques). Utilisé par Google Maps, Citymapper, etc.
- **GTFS-RT** — extension temps réel du GTFS, encodée en Protocol Buffers.
  Décrit l'état réel : position des véhicules, retards, perturbations.
- **Protocol Buffers (Protobuf)** — format binaire à schéma défini, plus
  compact et plus contraint que du JSON.

## Kafka

- **Topic** — flux nommé d'événements dans Kafka.
- **Partition** — subdivision d'un topic permettant le parallélisme.
- **Offset** — position de lecture d'un consommateur dans une partition.
- **Groupe de consommateurs** — ensemble de consommateurs se répartissant les
  partitions d'un topic.

## Temps et streaming

- **Temps de l'événement** vs **temps de traitement** — l'heure à laquelle un
  événement s'est réellement produit (ex. position émise par le bus) contre
  l'heure à laquelle le pipeline le reçoit. Les agrégations métier doivent se
  baser sur le temps de l'événement.
- **Watermark** — seuil de temps au-delà duquel un événement en retard n'est
  plus attendu, et un résultat peut être figé.

## Modélisation en couches

- **Architecture médaillon** — organisation des données en couches
  successives : bronze (brut), silver (nettoyé/typé), gold (agrégé pour la
  restitution).
- **Couche bronze** — événements bruts, jamais modifiés, partitionnés par
  date.
- **Couche silver** — données typées, dédupliquées, jointes au référentiel
  GTFS versionné.
- **Couche gold** — tables d'indicateurs agrégés, prêtes à être requêtées.
- **Architecture lambda** — deux chaînes de traitement distinctes (batch et
  streaming).
- **Architecture kappa** — une seule chaîne, le traitement par lots n'étant
  qu'un rejeu du flux.

## Fiabilité

- **Idempotence** — propriété d'un traitement rejoué produisant exactement le
  même résultat, sans doublons.
- **Rejeu** — capacité à retraiter des événements passés (ex. après un
  incident) sans intervention manuelle.
- **Référentiel de données** (reference/master data) — ici, le GTFS statique,
  republié chaque nuit ; chaque événement temps réel doit être joint à la
  version du référentiel en vigueur au moment où il s'est produit.
