# Décisions d'architecture

Ici je justifie mes choix technique et mes choix d'architecture

Voir [architecture.md](architecture.md) pour la vue d'ensemble et
[glossary.md](glossary.md) pour les notions citées ici.

---

## ADR-001 — Bus d'événements : Apache Kafka

- **Statut** : retenu
- **Contexte** : le flux GTFS-RT est non borné (P1, voir `architecture.md`) ;
  il faut un intermédiaire capable de tamponner et de rejouer les événements
  sans perdre la position de lecture en cas d'interruption.
- **Décision** : Apache Kafka comme bus d'événements entre le producteur
  d'ingestion et les traitements Spark.
- **Alternative écartée** : RabbitMQ — orienté messages, pas conçu pour le
  rejeu d'historique.
- **Justification** : standard de fait du bus d'événements ; durabilité, rejeu
  et découplage producteur/consommateur ; compétence explicitement demandée
  dans beaucoup d' offres data.

## ADR-002 — Traitement du flux : Spark Structured Streaming

- **Statut** : à mettre en œuvre
- **Contexte** : les métriques métier doivent être calculées sur le temps de
  l'événement, pas sur le temps de réception (P2), ce qui impose la gestion
  des retards via un watermark.
- **Décision** : Apache Spark (Structured Streaming) pour le nettoyage,
  l'enrichissement et les agrégations fenêtrées.
- **Alternative écartée** : Flink — excellent en streaming mais moins demandé
  en stage.
- **Justification** : moteur distribué le plus répandu en entreprise, API
  unique pour le flux et le lot, passerelle directe vers Databricks.

## ADR-003 — Format de stockage : Parquet

- **Statut** : à mettre en œuvre
- **Contexte** : l'historique croît en continu ; le découpage des fichiers
  détermine si une requête sur une journée lit des mégaoctets ou des
  gigaoctets (P6).
- **Décision** : Parquet pour les couches bronze et silver, partitionné par
  date.
- **Alternative écartée** : CSV — aucun typage, aucune compression, illisible
  à grande échelle.
- **Justification** : format colonne compressé, lecture sélective des
  colonnes, standard de tout lac de données.

## ADR-004 — Couche de restitution : PostgreSQL

- **Statut** : à mettre en œuvre
- **Contexte** : les indicateurs agrégés (couche gold) doivent être requêtés
  facilement par le dashboard.
- **Décision** : PostgreSQL en local.
- **Alternative écartée** : entrepôt cloud — hors budget pour un projet
  personnel.
- **Justification** : déjà maîtrisé, suffisant pour la restitution, coût nul
  en local.

## ADR-005 — Transformation SQL : dbt

- **Statut** : à mettre en œuvre
- **Contexte** : les modèles SQL manuels ne sont ni versionnés, ni testés, ni
  documentés.
- **Décision** : dbt pour les modèles de la couche gold.
- **Alternative écartée** : scripts SQL manuels — non testables.
- **Justification** : introduit la rigueur logicielle dans le SQL
  (versionnement, tests, documentation, lignage) ; très demandé.

## ADR-006 — Orchestration : Apache Airflow

- **Statut** : à mettre en œuvre
- **Contexte** : les traitements planifiés doivent gérer les dépendances,
  l'idempotence et le rattrapage après incident (P4).
- **Décision** : Apache Airflow.
- **Alternative écartée** : Cron — ne gère ni dépendances ni reprise.
- **Justification** : référence de l'orchestration, expose explicitement les
  notions de dépendance, d'idempotence et de rattrapage.

## ADR-007 — Environnement : Docker Compose + CI

- **Statut** : à mettre en œuvre
- **Contexte** : objectif technique du projet — un tiers doit pouvoir cloner
  le dépôt et démarrer le pipeline en moins de dix minutes.
- **Décision** : Docker Compose pour l'environnement local, GitLab CI (ou
  équivalent) pour l'intégration continue.
- **Alternative écartée** : installation manuelle — non reproductible.
- **Justification** : déjà maîtrisé, garantit la reproductibilité de
  l'environnement.

## ADR-008 — Lambda vs Kappa

- **Statut** : à trancher
- **Contexte** : le flux temps réel et les traitements par lots doivent
  coexister — le streaming alimente le bronze en continu et calcule les
  indicateurs de supervision à faible latence, tandis que des traitements
  planifiés recalculent chaque nuit les agrégats historiques.
- **Décision** : à documenter une fois la couche streaming en place.
- **Options** : lambda (deux chaînes distinctes, batch + streaming) vs kappa
  (une seule chaîne, le batch n'étant qu'un rejeu du flux).
- **Justification** : à argumenter — c'est une décision explicitement
  demandée par le cadrage du projet.
