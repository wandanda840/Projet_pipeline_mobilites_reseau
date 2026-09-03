# Démarrage

État actuel : seule la brique d'ingestion (`src/ingestion/position_vehicule.py`)
est fonctionnelle. Les sections Kafka/Spark/dbt/Airflow seront complétées au
fil des séances (voir [roadmap.md](roadmap.md)).

## Prérequis

- Python >= 3.11

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Lancer l'ingestion

```bash
python src/ingestion/position_vehicule.py
```

Interroge le flux GTFS-RT toutes les 10 secondes, sauvegarde chaque réponse
brute dans `local_data/` et affiche l'écart moyen de fraîcheur observé (voir
[data-sources.md](data-sources.md)).

## À venir

- Docker Compose pour l'environnement complet (Kafka, Spark, Postgres,
  Airflow) — voir ADR-007 dans [decisions.md](decisions.md).
- Objectif : un tiers doit pouvoir cloner le dépôt et obtenir un pipeline
  fonctionnel en moins de dix minutes, sans intervention manuelle.
