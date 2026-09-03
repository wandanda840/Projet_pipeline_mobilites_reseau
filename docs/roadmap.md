# Feuille de route

Déroulé du module tel que défini dans le document de cadrage. Chaque séance
produit un livrable versionné sur Git.

- [x] **Séance 1 — Cadrage et exploration de la source**
      Concevoir une architecture, lire une spécification, caractériser une
      source. *Livrable : document de cadrage, `docs/data-sources.md`.*
- [ ] **Séance 2 — Ingestion et producteur** *(en cours)*
      Consommation d'API, décodage Protobuf, résilience réseau.
      *Livrable : `src/ingestion/position_vehicule.py`.*
- [ ] **Séance 3 — Kafka : fondamentaux**
      Topics, partitions, offsets, groupes de consommateurs, garanties de
      livraison.
- [ ] **Séance 4 — Spark : modèle d'exécution**
      DataFrame, évaluation paresseuse, partitions, coût du shuffle.
- [ ] **Séance 5 — Spark Structured Streaming**
      Temps de l'événement, watermark, agrégations à état, points de
      reprise.
- [ ] **Séance 6 — Stockage et modélisation**
      Parquet, partitionnement, couches bronze / silver / gold.
- [ ] **Séance 7 — Orchestration et dbt**
      Graphes de tâches, idempotence, rattrapage, tests de modèles.
- [ ] **Séance 8 — Qualité, supervision, CI/CD**
      Contrats de données, tests bloquants, industrialisation.
- [ ] **Séance 9 — Valorisation**
      Dashboard, README, argumentaire d'entretien.

Voir [architecture.md](architecture.md) pour l'architecture cible et
[decisions.md](decisions.md) pour l'état des choix techniques par brique.
