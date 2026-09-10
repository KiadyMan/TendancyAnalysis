# TendancyAnalysis

Projet d'analyse de tendances et de prédiction des ventes de technologique pour l'année 2026, par marque. Le projet combine un pipeline de data science (nettoyage, agrégation, machine learning) et une API backend et une front 

---

## Sommaire

- [Concept du projet](#concept-du-projet)
- [Le pipeline IA (`ai/`)](#le-pipeline-ia-ai)
- [Le backend (`backend/`)](#le-backend-backend)
- [Endpoints de l'API](#endpoints-de-lapi)
- [Installation](#installation)
- [Lancement du projet](#lancement-du-projet)
- [Débogage](#débogage)

---

## Concept du projet

Question à laquelle répond le projet : **quelles marques de téléphones vont bien se vendre en 2026, et où faut-il investir ?**

Pour y répondre, le projet :
1. Nettoie et enrichit des données de ventes historiques (CSV brut)
2. Agrège ces données par marque et par mois
3. Entraîne un modèle de machine learning (RandomForest) sur ces agrégations
4. Projette les ventes 2026 par marque et calcule un score d'opportunité relatif
5. Sert ces résultats via une API REST (FastAPI + MongoDB), consommable par un frontend 

Le pipeline de data science (`ai/`) et le backend (`backend/`) sont **volontairement découplés** :
- `ai/`  il lit/écrit des CSV et un modèle `.pkl`
- `backend/`  il orchestre l'exécution du pipeline, lit ses résultats (CSV), les insère dans MongoDB, et les sert en JSON

---

## Le pipeline IA (`ai/`)

Quatre étapes séquentielles, chacune produisant un artefact utilisé par la suivante.

### P1 — Nettoyage (`data_processing/spark_job.py`)

- Lit le CSV brut de ventes (`data/raw/mobile_sales_data.csv`)
- Nettoie les lignes incomplètes (dates, quantités, prix, marque manquants)
- Calcule pour chaque vente : `Revenue`, `Growth_Rate_%` (variation par rapport à la vente précédente de la même marque), et l'étiquette `Trend` (Forte Hausse / Stable / Baisse / Nouvelle)
- Écrit `data/processed/cleaned_data.csv`
- Utilise **PySpark** — conçu pour tenir sur de gros volumes (50 000+ lignes)

### P2 — Agrégation (`ai/preprocessing/features.py`)

- Relit `cleaned_data.csv` avec pandas
- Agrège les ventes par `(Brand, Year, Month)` : quantité totale mensuelle, prix moyen, nombre de transactions
- Encode les variables catégorielles (`pd.get_dummies`) pour préparer les features du modèle
- Retourne `df`, `df_monthly`, `X` (features), `y` (cible = quantité mensuelle)

### P3 — Entraînement (`ai/models/train.py`)

- Entraîne un `RandomForestRegressor` (100 arbres, profondeur max 6)
- Split temporel : entraînement sur `Year <= 2024`, test sur `Year == 2025`
- Évalue le modèle (R² ≈ 96%, MAE ≈ 33 unités/mois)
- Sauvegarde le modèle dans `ai/models/model.pkl`

### P4 — Prédiction (`ai/prediction/run_predictions.py`)

- Recharge `model.pkl`
- Pour chaque marque, construit des features 2026 (proxy : moyennes 2025) et appelle `model.predict()` mois par mois, puis somme sur l'année
- Calcule aussi un taux de croissance historique (2025 vs 2024) pour étiqueter la tendance (`Predicted_Trend`)
- Appelle `calculate_opportunities()` (voir ci-dessous) pour enrichir le résultat
- Écrit `data/processed/p2_predictions_output.csv`

### Score d'opportunité (`ai/opportunity/proposal.py`)

```python
OpportunityScore = (Predicted_Quantity_2026 / max(Predicted_Quantity_2026)) * 100
```

C'est une **normalisation en pourcentage** de la quantité prédite par rapport à la marque qui vend le plus — pas un score stratégique combinant croissance et volume. La marque avec la plus grosse quantité prédite reçoit toujours 100 ; les autres reçoivent un pourcentage relatif. `ProposedProduct` est un texte généré automatiquement (`"Écosystème Intelligent & Flagship {Brand}"`).

---

## Le backend (`backend/`)

Son rôle :
1. Déclencher l'exécution du pipeline `ai/` (via `POST /pipeline/run`)
2. Lire les CSV produits (`cleaned_data.csv`, `p2_predictions_output.csv`)
3. Insérer ces résultats dans MongoDB (via Beanie/Motor)
4. Servir ces données en JSON via des routes REST

### Rôle de chaque couche

| Dossier | Rôle |
|---|---|
| `database/` | Connexion à MongoDB (Motor) et initialisation de Beanie |
| `models/` | Documents Beanie — définissent la **structure** des collections MongoDB (champs, types). Ne prédisent rien, ne calculent rien. |
| `schemas/` | Contrats Pydantic — définissent la **forme des réponses JSON** de l'API, séparément de la structure interne stockée en base |
| `services/` | Logique métier — lisent les CSV de `ai/`, transforment les lignes en documents Beanie, écrivent/lisent MongoDB |
| `routes/` | Endpoints FastAPI — reçoivent les requêtes HTTP, appellent les services, renvoient du JSON |

---

## Endpoints de l'API

### `GET /health`

Vérification simple que le serveur tourne.

### `GET /trends/`

Historique des ventes, **une ligne par transaction**, sortie de P1. Répond à : *"qu'est-ce qui s'est passé dans le passé ?"*


### `GET /trends/{brand}`

Même format, filtré sur une marque (ex. `/trends/Samsung`).

### `GET /predictions/`

Projection 2026, **une ligne par marque**, sortie de P4. Répond à : *"combien va-t-on vendre l'an prochain ?"*


### `GET /predictions/{brand}`

Même format, filtré sur une marque.

### `GET /opportunities/`

Classement des marques par score relatif de volume (0–100), sortie enrichie de P4. Répond à : *"quel est le poids relatif de chaque marque en volume prédit ?"*


### `POST /pipeline/run`

Déclenche l'enchaînement complet P1 (Spark) → P3 (entraînement) → P4 (prédictions), puis pousse les résultats dans MongoDB. Tourne **en arrière-plan** (`BackgroundTasks`) — la réponse est immédiate et ne reflète pas la fin réelle du traitement.


## Installation

### Prérequis

- Python 3.12
- MongoDB 
- Java (requis par PySpark)

### 1. Cloner et créer l'environnement virtuel

```bash
cd TendancyAnalysis
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

Versions à respecter impérativement pour MongoDB (Motor/Beanie/PyMongo sont sensibles aux incompatibilités de version) :

```
motor==3.6.0
beanie==1.26.0
pymongo==4.9.2
```

### 3. Installer et démarrer MongoDB

**Option locale (Ubuntu) :**
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Option Docker :**
```bash
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

---

## Lancement du projet

### 1. Démarrer le backend

```bash
uvicorn backend.main:app --reload --port 8000
```

L'API est disponible sur `http://localhost:8000`, la documentation interactive Swagger sur `http://localhost:8000/docs`.

### 2. Lancer le pipeline complet

Une fois le serveur démarré, déclencher le pipeline pour remplir MongoDB :

```bash
curl -X POST http://localhost:8000/pipeline/run
```

Ou directement depuis `/docs` dans le navigateur.

Attendre la fin des logs serveur (repérable par la ligne `Prédictions 2026 générées et sauvegardées dans : ...`) avant d'interroger les routes de lecture.

### 3. Consulter les résultats

```bash
curl http://localhost:8000/trends/
curl http://localhost:8000/predictions/
curl http://localhost:8000/opportunities/
```

---

## Débogage

### Vérifier le contenu de MongoDB directement

```bash
mongosh
```

Si un compteur renvoie `0` après un `POST /pipeline/run` réussi, l'insertion a probablement échoué silencieusement (limite connue de `BackgroundTasks`, qui n'exposent pas leurs exceptions). Ajouter des logs `print()` temporaires dans `pipeline_service.run_full_pipeline()` autour des appels `insert_many()` pour identifier l'étape en cause.

### Erreurs de connexion MongoDB

```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: Connection refused
```

→ MongoDB n'est pas démarré. Vérifier avec `sudo systemctl status mongod` (ou `docker ps` si conteneurisé).

### Erreurs de version Beanie/Motor

```
TypeError: MotorDatabase object is not callable
```

→ Conflit de versions entre `beanie`, `motor` et `pymongo`. Réinstaller le trio pinné exact indiqué dans la section Installation.