# Architecture



## En une phrase

Construire une chaîne de traitement de données complète qui ingère en continu
la position temps réel des bus du réseau STAR de Rennes, la confronte à
l'offre théorique de transport, et produit des indicateurs de ponctualité
exploitables — le tout industrialisé avec les outils standards du métier de
data engineer.

## Principe non négociable

Le pipeline est organisé selon le **modèle médaillon** (voir
[glossary.md](glossary.md)). La donnée brute n'est jamais écrasée : c'est le
seul point de vérité qui permet de rejouer l'histoire quand la logique métier
s'avère fausse.

## Couches

| Étage | Technologie | Rôle |
|---|---|---|
| Sources | API HTTP publiques | Flux GTFS-RT binaire et archive GTFS statique |
| Ingestion | Producteur Python | Interrogation périodique, décodage Protobuf, publication d'événements |
| Bus d'événements | Apache Kafka | Tampon durable, découplage producteur/consommateur, rejeu possible |
| Traitement flux | Spark Structured Streaming | Nettoyage, enrichissement, agrégations fenêtrées en temps de l'événement |
| Couche bronze | Fichiers Parquet | Événements bruts, jamais modifiés, partitionnés par date |
| Couche silver | Fichiers Parquet | Données typées, dédupliquées, jointes au référentiel GTFS versionné |
| Couche gold | PostgreSQL | Tables d'indicateurs agrégés prêts à être requêtés |
| Transformation | dbt | Modèles SQL versionnés, documentés et testés |
| Orchestration | Apache Airflow | Planification, dépendances, reprise sur incident, rattrapage |
| Restitution | Dashboard | Visualisation des indicateurs de ponctualité |
| Industrialisation | Docker Compose, CI | Environnement reproductible, tests automatisés |

Le flux temps réel et les traitements par lots coexistent : le streaming
alimente le bronze en continu et calcule les indicateurs de supervision à
faible latence, tandis que des traitements planifiés recalculent chaque nuit
les agrégats historiques de façon fiable. Le choix entre architecture
**lambda** (deux chaînes distinctes) et **kappa** (une seule chaîne, le batch
n'étant qu'un rejeu du flux) est documenté dans
[decisions.md](decisions.md) (ADR-008).

## Problématiques d'ingénierie adressées

| # | Problème | Réponse architecturale |
|---|---|---|
| P1 | Flux non borné | Kafka comme tampon rejouable |
| P2 | Temps de l'événement vs temps du traitement | Watermark dans Spark Structured Streaming |
| P3 | Référentiel GTFS republié chaque nuit | Versionnement du référentiel, jointure à la version en vigueur |
| P4 | Idempotence et rejeu | Conception des écritures/partitions/tâches d'orchestration |
| P5 | Qualité et confiance | Règles de qualité testées à chaque exécution (dbt, CI) |
| P6 | Volumétrie et stockage | Partitionnement Parquet |

## État d'avancement

Voir [roadmap.md](roadmap.md). Justification détaillée de chaque brique
technique : [decisions.md](decisions.md).
