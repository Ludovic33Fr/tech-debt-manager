# Patterns de remediation courants

## 1. Remediation de la dette de Code

### 1.1 Extract Method / Function
**Probleme** : Fonction trop longue, responsabilites multiples
**Solution** : Extraire des blocs logiques en fonctions nommees
**Effort** : Faible (1-2h par fonction)
**Risque** : Faible si tests existants

```
AVANT:
def process_order(order):
    # 100 lignes de code melange validation, calcul, persistence

APRES:
def process_order(order):
    validated = validate_order(order)
    total = calculate_total(validated)
    return save_order(validated, total)
```

### 1.2 Replace Magic Numbers with Constants
**Probleme** : Litteraux numeriques disperses
**Solution** : Extraire en constantes nommees
**Effort** : Tres faible (quelques minutes)
**Risque** : Tres faible

### 1.3 Simplify Conditionals (Guard Clauses)
**Probleme** : Nesting profond
**Solution** : Inverser les conditions et faire des early returns
**Effort** : Faible
**Risque** : Faible si tests existants

```
AVANT:
def foo(x):
    if x:
        if x.valid:
            if x.active:
                return process(x)

APRES:
def foo(x):
    if not x: return None
    if not x.valid: return None
    if not x.active: return None
    return process(x)
```

### 1.4 Remove Dead Code
**Probleme** : Code non reference, imports inutiles
**Solution** : Supprimer le code mort
**Effort** : Faible
**Risque** : Moyen (s'assurer que le code est vraiment mort)

### 1.5 DRY — Eliminate Duplication
**Probleme** : Code duplique
**Solution** : Extraire la logique commune dans une fonction/classe partagee
**Effort** : Moyen
**Risque** : Moyen (trouver la bonne abstraction)

---

## 2. Remediation de la dette d'Architecture

### 2.1 Strangler Fig Pattern
**Probleme** : Monolithe a migrer
**Solution** : Creer un nouveau systeme autour de l'ancien, migrer incrementalement
**Effort** : Eleve (mois)
**Risque** : Faible (l'ancien systeme reste fonctionnel)

Etapes :
1. Identifier un module a extraire
2. Creer le nouveau service/module
3. Router le trafic vers le nouveau module
4. Supprimer l'ancien code une fois le nouveau valide

### 2.2 Dependency Inversion
**Probleme** : Couplage fort entre modules
**Solution** : Introduire des interfaces/abstractions entre les couches
**Effort** : Moyen
**Risque** : Moyen

### 2.3 Break Circular Dependencies
**Probleme** : A -> B -> C -> A
**Solution** :
- Extraire l'interface commune dans un module separe
- Utiliser l'injection de dependances
- Appliquer le Mediator Pattern
**Effort** : Moyen a eleve
**Risque** : Moyen

### 2.4 Modularisation
**Probleme** : Monolithe non structure
**Solution** : Identifier les bounded contexts, creer des modules avec interfaces claires
**Effort** : Eleve
**Risque** : Eleve (changement structurel profond)

---

## 3. Remediation de la dette de Tests

### 3.1 Ajouter des tests sur le code critique
**Probleme** : Pas de tests sur le coeur metier
**Solution** : Ecrire des tests unitaires pour les fonctions les plus critiques
**Effort** : Moyen
**Priorite** : Tres haute

Strategie :
1. Identifier le code le plus risque (complexite elevee + pas de tests)
2. Ecrire d'abord des tests de caracterisation (capturer le comportement actuel)
3. Puis ajouter des tests unitaires cibles

### 3.2 Corriger les tests fragiles
**Probleme** : Tests qui echouent de maniere intermittente
**Solution** : Eliminer les dependances a l'etat externe, aux timers, a l'ordre d'execution
**Effort** : Moyen
**Risque** : Faible

### 3.3 Reduire le temps de CI
**Probleme** : Suite de tests trop lente
**Solution** :
- Paralleliser les tests
- Utiliser des mocks pour les I/O lentes
- Separer tests unitaires / integration / e2e
- Executer les tests rapides en premier
**Effort** : Moyen
**Risque** : Faible

---

## 4. Remediation de la dette de Documentation

### 4.1 README minimum viable
**Probleme** : Pas de README
**Solution** : Creer un README avec : description, installation, usage, contribution
**Effort** : Faible (1-2h)

### 4.2 Docstrings sur l'API publique
**Probleme** : Pas de documentation sur les interfaces
**Solution** : Ajouter des docstrings sur toutes les fonctions/classes publiques
**Effort** : Moyen
**Risque** : Tres faible

### 4.3 Architecture Decision Records (ADR)
**Probleme** : Decisions architecturales non documentees
**Solution** : Adopter les ADR pour documenter les decisions importantes
**Effort** : Faible (processus continu)

---

## 5. Remediation de la dette de Dependances

### 5.1 Mise a jour incrementale
**Probleme** : Dependances obsoletes
**Solution** : Mettre a jour une dependance a la fois, tester, repeter
**Effort** : Variable
**Risque** : Moyen (regressions possibles)

Strategie :
1. Commencer par les patches de securite (CVEs)
2. Puis les mises a jour mineures
3. Puis les mises a jour majeures (une par une)

### 5.2 Supprimer les dependances inutilisees
**Probleme** : Dependances fantomes
**Solution** : Identifier et supprimer les dependances non referencees
**Effort** : Faible
**Outils** : `depcheck` (npm), `pip-autoremove` (Python)

### 5.3 Remplacer les libs abandonnees
**Probleme** : Dependance plus maintenue
**Solution** : Trouver et migrer vers une alternative active
**Effort** : Variable (simple a tres eleve)

---

## 6. Remediation de la dette d'Infrastructure

### 6.1 Ajouter un pipeline CI/CD
**Probleme** : Pas de CI/CD
**Solution** : Mettre en place un pipeline basique (lint, test, build)
**Effort** : Moyen (1-3 jours)
**ROI** : Tres eleve

### 6.2 Externaliser les configurations
**Probleme** : Configs hardcodees
**Solution** : Utiliser des variables d'environnement ou des fichiers de config
**Effort** : Faible a moyen
**Risque** : Faible

### 6.3 Ajouter du linting et formatting
**Probleme** : Style inconsistant
**Solution** : Configurer ESLint/Prettier, Black/Ruff, etc. avec pre-commit hooks
**Effort** : Faible (quelques heures)
**ROI** : Eleve

---

## 7. Strategie generale de remediation

### Regle des 20/80
Se concentrer sur les 20% du code qui causent 80% des problemes. Identifier les hotspots :
- Fichiers les plus modifies (churn eleve)
- Fichiers les plus complexes
- Fichiers sans tests
- L'intersection de ces trois ensembles est la zone prioritaire

### Boy Scout Rule
"Laisser le code plus propre qu'on ne l'a trouve." Appliquer de petites ameliorations lors de chaque modification.

### Dedicated Debt Sprints
Allouer 15-20% du temps de chaque sprint a la reduction de dette. Ou planifier un sprint dedie tous les 4-6 sprints.

### Metriques de suivi
Suivre l'evolution :
- Health Score au fil du temps
- Nombre d'items de dette ouverts vs fermes
- Temps moyen de remediation
- Couverture de tests
