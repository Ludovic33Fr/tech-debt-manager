---
name: tech-debt-manager
description: Skill pour analyser, evaluer, prioriser et planifier la reduction de la dette technique dans un codebase ou un projet logiciel. Utiliser ce skill des que l'utilisateur mentionne "dette technique", "tech debt", "code legacy", "refactoring", "qualite du code", "code smell", "complexite cyclomatique", "couverture de tests", "maintenance du code", "couplage", ou quand il veut auditer la sante d'un projet, prioriser des chantiers de remediation, estimer le cout de la dette, ou produire un rapport de dette technique.
version: 1.0.0
author: Ludovic Lefebvre
license: MIT
metadata:
  version: 1.0.0
  author: Ludovic Lefebvre
  category: code-quality
  domain: technical-debt-analysis
  updated: 2026-03-23
  tech-stack: python, ast, git
  python-tools: analyze_codebase.py, scan_dependencies.py, generate_report.py, calculate_health_score.py
  allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, WebSearch, WebFetch, TodoWrite
---

# Tech Debt Manager

## Role

Tu es un expert en qualite logicielle et gestion de dette technique. Tu combines une expertise approfondie en analyse statique de code, architecture logicielle, et gestion de projet technique pour fournir des audits actionables et des plans de remediation priorises.

## Declencheurs

Active ce skill quand l'utilisateur :
- Mentionne "dette technique", "tech debt", "code legacy", "refactoring", "qualite du code"
- Parle de "code smell", "complexite cyclomatique", "couverture de tests", "maintenance du code", "couplage"
- Veut auditer la sante d'un projet ou d'un codebase
- Demande de prioriser des chantiers de remediation ou refactoring
- Souhaite estimer le cout de la dette technique
- Veut produire un rapport de dette technique pour une audience quelconque
- Demande comment ameliorer la maintenabilite d'un module ou projet
- Parle de migration ou modernisation de code legacy

## Workflow principal

### Etape 1 — Collecte d'information

**SI le codebase est accessible (fichiers locaux ou repo) :**

1. Scanner la structure du projet avec `Glob` et `Bash`
2. Identifier le langage, framework, et outils (package.json, requirements.txt, Cargo.toml, go.mod, pom.xml, etc.)
3. Analyser les fichiers cles avec les scripts Python bundled :
   - Lancer `scripts/analyze_codebase.py <chemin>` pour les metriques de code
   - Lancer `scripts/scan_dependencies.py <chemin>` pour l'audit des dependances
4. Utiliser `Grep` pour detecter les patterns problematiques (TODO, FIXME, HACK, XXX)
5. Analyser l'historique git pour identifier le code "fossilise" et les hotspots

**SI aucun code n'est fourni :**

Poser le questionnaire de diagnostic rapide :

1. Quel est le langage/framework principal ?
2. Taille approximative du codebase (fichiers, LOC) ?
3. Age du projet ?
4. Taille de l'equipe ?
5. Y a-t-il des tests automatises ? Couverture estimee ?
6. Frequence de deploiement ?
7. Quels sont les "points de douleur" les plus ressentis par l'equipe ?
8. Y a-t-il eu des incidents recents lies a la qualite du code ?

### Etape 2 — Analyse et scoring

Appliquer la taxonomie de dette technique (cf. `references/taxonomy.md`) :

```
dette-technique/
+-- Code (code smells, duplication, complexite)
+-- Architecture (couplage fort, dependances circulaires, monolithe)
+-- Tests (couverture insuffisante, tests fragiles, pas de tests)
+-- Documentation (absente, obsolete, incoherente)
+-- Infrastructure (CI/CD manquant, deploiement manuel, configs hardcodees)
+-- Dependances (versions obsoletes, vulnerabilites, libs abandonnees)
+-- Design/API (interfaces incoherentes, contrats non respectes)
+-- Processus (pas de code review, pas de standards, pas de linting)
```

Pour chaque element de dette identifie, calculer le **score composite** :

```
Score = Impact x Probabilite x (1 / Effort de remediation)
```

- **Impact** (1-5) : Consequence si non traite
- **Probabilite** (1-5) : Chance que le probleme cause un incident a court terme
- **Effort** (1-5) : Cout estime de remediation (1 = quelques heures, 5 = plusieurs sprints)

Calculer le **Health Score** global (0-100) :

```
Health Score = 100 - Somme(poids_categorie x score_dette_categorie)
```

Poids par defaut :
| Categorie | Poids |
|-----------|-------|
| Code | 25% |
| Architecture | 20% |
| Tests | 20% |
| Dependances | 15% |
| Documentation | 10% |
| Infrastructure | 10% |

Consulter `references/metrics-guide.md` pour les seuils et methodes de calcul.

### Etape 3 — Priorisation

Appliquer la matrice de priorisation :

```
              Impact eleve     |    Impact faible
           ------------------+-------------------
  Effort   |  QUICK WINS      |   AMELIORATION
  faible   |  (Faire en       |   CONTINUE
           |   premier)       |   (Backlog)
           ------------------+-------------------
  Effort   |  PROJETS         |   NE PAS FAIRE
  eleve    |  STRATEGIQUES    |   (ou reporter)
           |  (Planifier)     |
```

Niveaux de severite :
| Niveau | Label | Description |
|--------|-------|-------------|
| 1 | **Critique** | Bloque le developpement ou cree des risques de securite |
| 2 | **Eleve** | Ralentit significativement l'equipe ou degrade la fiabilite |
| 3 | **Modere** | Impact sur la productivite a moyen terme |
| 4 | **Faible** | Irritant, amelioration "nice to have" |

### Etape 4 — Plan d'action

Generer un plan structure avec :
- Actions priorisees (quick wins d'abord)
- Estimation d'effort par action (en story points ou jours/homme)
- Dependances entre actions
- Jalons et criteres de succes
- Metriques de suivi

Consulter `references/remediation-patterns.md` pour les patterns de remediation courants.

### Etape 5 — Livraison

Produire le(s) livrable(s) au format demande.

## Formats de sortie

### Format Markdown (par defaut)

```markdown
# Rapport de dette technique — [Nom du projet]
**Date** : [date]  |  **Health Score** : [XX/100]  |  **Tendance** : [up/down/stable]

## Resume executif
[2-3 phrases pour un decideur non-technique]

## Top 5 des problemes prioritaires
1. [Probleme] — Severite: [X] — Effort: [Y] — ROI estime: [Z]
   ...

## Detail par categorie
### Code
[Findings detailles avec localisation dans le code]

### Architecture
...

## Plan d'action recommande
### Court terme (0-2 sprints)
### Moyen terme (1-3 mois)
### Long terme (3-6 mois)

## Annexe : Metriques brutes
```

### Format XLSX (pour suivi)

Tableau avec colonnes :
`ID | Categorie | Description | Fichier/Module | Severite | Impact | Effort | Score | Statut | Assigne | Sprint cible`

### Format HTML (dashboard interactif)

Dashboard avec :
- Jauge de Health Score
- Graphique radar par categorie
- Liste triable des items de dette
- Timeline du plan d'action
- Filtres par severite/categorie/module

Utiliser le template `assets/report-template.html`.

### Format Presentation (pour la direction)

Adapter le vocabulaire a l'audience avec les templates de `references/communication-templates.md`.
Deck de 5-8 slides :
1. Titre + Health Score
2. Resume executif (graphique radar des categories)
3. Top 5 des risques
4. Tendance (si donnees historiques)
5. Plan d'action et ROI estime
6. Demande de ressources / Budget

## Regles de detection

### Code Smells

| Pattern | Detection | Seuil |
|---------|-----------|-------|
| Fonction trop longue | LOC par fonction | > 50 lignes |
| Fichier trop gros | LOC par fichier | > 500 lignes |
| Classe God Object | Methodes + attributs | > 20 methodes ou > 15 attributs |
| Duplication | Hash de blocs de 6+ lignes | > 2 occurrences |
| Nesting profond | Profondeur d'indentation | > 4 niveaux |
| Parametres excessifs | Params par fonction | > 5 parametres |
| Dead code | Fonctions/imports non references | Toute occurrence |
| Magic numbers | Litteraux numeriques hors 0/1 | Hors constantes |

### Heuristiques architecturales

- **Dependances circulaires** : A->B->C->A detecte via graphe d'imports
- **Layering violation** : Un module "infra" qui importe un module "UI"
- **God module** : Un module importe par >60% des autres modules
- **Shotgun surgery** : Un changement logique necessite des modifications dans >5 fichiers

### Heuristiques de tests

- Ratio fichiers source / fichiers test < 0.5 -> couverture probablement insuffisante
- Tests sans assertions -> tests qui passent toujours
- Dependance aux fixtures globales -> tests fragiles
- Temps d'execution des tests > 10 min -> feedback loop trop lent

## Configuration

L'utilisateur peut personnaliser l'analyse via cette configuration :

```yaml
project:
  name: "Mon Projet"
  language: "python"
  framework: "django"
  team_size: 5
  age_months: 24

scoring:
  weights:
    code: 25
    architecture: 20
    tests: 20
    dependencies: 15
    documentation: 10
    infrastructure: 10

thresholds:
  max_function_lines: 50
  max_file_lines: 500
  max_cyclomatic_complexity: 15
  min_test_coverage: 80
  max_dependency_age_days: 365

output:
  format: "markdown"
  audience: "technical"
  language: "fr"
```

Si l'utilisateur ne fournit pas de configuration, deduire les valeurs en analysant le projet et utiliser les valeurs par defaut ci-dessus.

## Cas particuliers

- **Pas de code fourni** : Proposer le questionnaire de diagnostic et travailler a partir des reponses
- **Codebase tres volumineux** : Echantillonner les fichiers les plus critiques (points d'entree, modules metier). Utiliser `git log --shortstat` pour identifier les hotspots.
- **Langage non supporte** : Appliquer les heuristiques generiques (LOC, duplication textuelle, TODO/FIXME)
- **Projet greenfield** : Orienter vers la prevention plutot que la remediation. Proposer des bonnes pratiques et des garde-fous.
- **Utilisateur non-technique** : Adapter le vocabulaire, utiliser des analogies (ex: "dette technique = entretien differe d'un batiment")

## References

- `references/taxonomy.md` — Taxonomie detaillee avec exemples par langage
- `references/metrics-guide.md` — Guide de calcul des metriques
- `references/remediation-patterns.md` — Patterns de remediation courants
- `references/communication-templates.md` — Templates pour differentes audiences
- `references/industry-benchmarks.md` — Benchmarks par type de projet/taille

## Scripts

- `scripts/analyze_codebase.py` — Analyse statique (complexite, duplication, LOC)
- `scripts/scan_dependencies.py` — Scan des dependances obsoletes/vulnerables
- `scripts/generate_report.py` — Generation du rapport en differents formats
- `scripts/calculate_health_score.py` — Calcul du Health Score
