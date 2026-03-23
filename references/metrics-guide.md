# Guide de calcul des metriques

## 1. Complexite cyclomatique

### Definition
Nombre de chemins lineairement independants dans le code. Chaque point de decision (if, for, while, case, catch, &&, ||) ajoute 1 a la complexite.

### Calcul

```
CC = 1 + nombre_de_points_de_decision
```

Points de decision :
- `if`, `elif`, `else if`
- `for`, `while`, `do...while`
- `case` (dans switch)
- `catch`, `except`
- `&&`, `||` (operateurs logiques)
- `?:` (ternaire)
- `?.` (optional chaining compte si utilise comme garde)

### Seuils

| CC | Niveau | Interpretation |
|----|--------|----------------|
| 1-5 | Bon | Code simple, facile a tester |
| 6-10 | Acceptable | Complexite moderee |
| 11-20 | Attention | Difficile a tester, envisager refactoring |
| 21-50 | Critique | Tres difficile a maintenir |
| > 50 | Extreme | Refactoring obligatoire |

### Script de calcul

Utiliser `scripts/analyze_codebase.py` qui utilise l'AST pour Python/JS/TS ou des heuristiques regex pour les autres langages.

---

## 2. Duplication de code

### Definition
Pourcentage de code qui existe en copies identiques ou quasi-identiques dans le codebase.

### Methode de detection

1. Decouper le code en blocs de N lignes (N = 6 par defaut)
2. Normaliser (supprimer espaces, commentaires)
3. Hasher chaque bloc
4. Identifier les hash dupliques

### Seuils

| % Duplication | Niveau |
|--------------|--------|
| < 3% | Bon |
| 3-5% | Acceptable |
| 5-10% | Attention |
| 10-20% | Critique |
| > 20% | Extreme |

---

## 3. Taille des fichiers et fonctions

### Seuils pour les fichiers

| LOC / fichier | Niveau |
|--------------|--------|
| < 200 | Bon |
| 200-500 | Acceptable |
| 500-1000 | Attention |
| > 1000 | Critique |

### Seuils pour les fonctions

| LOC / fonction | Niveau |
|---------------|--------|
| < 20 | Bon |
| 20-50 | Acceptable |
| 50-100 | Attention |
| > 100 | Critique |

---

## 4. Profondeur d'imbrication (nesting)

### Definition
Nombre maximal de niveaux d'indentation dans une fonction.

### Seuils

| Niveaux | Niveau |
|---------|--------|
| <= 2 | Bon |
| 3 | Acceptable |
| 4 | Attention |
| >= 5 | Critique |

### Remediation
- Early return / Guard clauses
- Extraction de fonctions
- Pattern Strategy / State

---

## 5. Couplage afferent et efferent

### Definitions
- **Couplage afferent (Ca)** : Nombre de modules qui dependent de ce module (= responsabilite)
- **Couplage efferent (Ce)** : Nombre de modules dont ce module depend (= dependance)
- **Instabilite (I)** : Ce / (Ca + Ce) — 0 = stable, 1 = instable

### Seuils

| Ca + Ce | Niveau |
|---------|--------|
| < 5 | Bon |
| 5-10 | Acceptable |
| 10-20 | Attention |
| > 20 | Critique |

### Detection
Analyser le graphe d'imports/requires du projet.

---

## 6. Ratio code/tests

### Definition
Nombre de fichiers de tests divise par le nombre de fichiers source.

### Conventions de detection des fichiers de tests
- `*_test.py`, `test_*.py` (Python)
- `*.test.js`, `*.spec.js`, `*.test.ts`, `*.spec.ts` (JavaScript/TypeScript)
- `*Test.java`, `*Spec.java` (Java)
- `*_test.go` (Go)
- `*_spec.rb` (Ruby)

### Seuils

| Ratio test/src | Niveau |
|---------------|--------|
| > 0.8 | Bon |
| 0.5 - 0.8 | Acceptable |
| 0.3 - 0.5 | Attention |
| < 0.3 | Critique |

---

## 7. Age du code (fossilisation)

### Definition
Temps ecoule depuis la derniere modification d'un fichier.

### Calcul
```bash
git log -1 --format="%ci" -- <fichier>
```

### Seuils

| Derniere modification | Niveau |
|----------------------|--------|
| < 3 mois | Actif |
| 3-12 mois | Stable |
| 1-2 ans | Vieillissant |
| > 2 ans | Fossilise |

Note : Un fichier fossilise n'est pas forcement problematique. Il le devient si :
- Il contient des patterns obsoletes
- Il n'a pas de tests
- Il utilise des API depreciees

---

## 8. Densite de marqueurs de dette

### Definition
Nombre de TODO, FIXME, HACK, XXX, WORKAROUND par 1000 lignes de code.

### Calcul
```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND" --include="*.{py,js,ts,java,go,rb,rs}" | wc -l
```

### Seuils

| Marqueurs / KLOC | Niveau |
|------------------|--------|
| < 2 | Bon |
| 2-5 | Acceptable |
| 5-10 | Attention |
| > 10 | Critique |

---

## 9. Health Score — Formule complete

### Etape 1 : Score par categorie (0-100, 100 = parfait)

Pour chaque categorie, calculer un score base sur les metriques disponibles :

```
score_code = f(complexite, duplication, taille, nesting, dead_code)
score_architecture = f(couplage, dependances_circulaires, layering)
score_tests = f(ratio_tests, couverture, temps_ci)
score_dependances = f(obsolescence, vulnerabilites, abandonnees)
score_documentation = f(readme, docstrings, api_docs)
score_infrastructure = f(ci_cd, linting, monitoring)
```

Chaque sous-metrique est normalisee sur 0-100 en utilisant les seuils ci-dessus.

### Etape 2 : Score global pondere

```
Health Score = Somme(poids_i * score_i) pour i dans categories

Poids par defaut :
  code: 0.25
  architecture: 0.20
  tests: 0.20
  dependances: 0.15
  documentation: 0.10
  infrastructure: 0.10
```

### Etape 3 : Interpretation

| Health Score | Interpretation |
|-------------|----------------|
| 80-100 | Excellent : Dette maitrisee, maintenance aisee |
| 60-79 | Bon : Quelques points d'attention, globalement sain |
| 40-59 | Attention : Dette significative, plan de remediation necessaire |
| 20-39 | Critique : Dette importante, impact sur la productivite |
| 0-19 | Urgence : Risque eleve, action immediate requise |

---

## 10. Metriques avancees (optionnelles)

### Churn rate
Frequence de modification d'un fichier. Un fichier avec un churn eleve et une complexite elevee est un hotspot prioritaire.

```bash
git log --format=format: --name-only --since="6 months ago" | sort | uniq -c | sort -rn | head -20
```

### Code ownership
Nombre de contributeurs distincts par fichier. Un fichier avec beaucoup de contributeurs differents peut manquer de coherence.

```bash
git log --format='%aN' -- <fichier> | sort -u | wc -l
```

### Coupling temporel
Fichiers qui sont frequemment modifies ensemble (suggerent un couplage implicite).

```bash
git log --format=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn
```
