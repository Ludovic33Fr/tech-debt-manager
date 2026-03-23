# Benchmarks de l'industrie

## 1. Health Score par taille de projet

| Taille (LOC) | Equipe | Health Score moyen | Bon | Excellent |
|-------------|--------|-------------------|-----|-----------|
| < 10K | 1-3 | 72 | > 70 | > 85 |
| 10K-50K | 3-8 | 65 | > 65 | > 80 |
| 50K-200K | 8-20 | 58 | > 55 | > 75 |
| 200K-1M | 20-50 | 50 | > 50 | > 70 |
| > 1M | 50+ | 42 | > 45 | > 65 |

---

## 2. Metriques par langage/ecosysteme

### Python
| Metrique | Median | Bon | Excellent |
|----------|--------|-----|-----------|
| Complexite cyclomatique moyenne | 8 | < 7 | < 5 |
| Couverture de tests | 45% | > 70% | > 85% |
| Duplication | 8% | < 5% | < 3% |
| Dependances obsoletes | 30% | < 15% | < 5% |
| Ratio docstrings | 35% | > 60% | > 80% |

### JavaScript/TypeScript
| Metrique | Median | Bon | Excellent |
|----------|--------|-----|-----------|
| Complexite cyclomatique moyenne | 9 | < 8 | < 5 |
| Couverture de tests | 40% | > 65% | > 80% |
| Duplication | 10% | < 5% | < 3% |
| Dependances obsoletes | 35% | < 20% | < 10% |
| Bundle size growth/mois | 5% | < 2% | < 1% |

### Java
| Metrique | Median | Bon | Excellent |
|----------|--------|-----|-----------|
| Complexite cyclomatique moyenne | 10 | < 8 | < 5 |
| Couverture de tests | 55% | > 75% | > 85% |
| Duplication | 7% | < 5% | < 3% |
| Methodes par classe | 12 | < 10 | < 7 |
| Dependances obsoletes | 25% | < 15% | < 5% |

### Go
| Metrique | Median | Bon | Excellent |
|----------|--------|-----|-----------|
| Complexite cyclomatique moyenne | 6 | < 5 | < 3 |
| Couverture de tests | 50% | > 70% | > 85% |
| Duplication | 5% | < 3% | < 2% |
| LOC par fonction | 25 | < 20 | < 15 |

### Rust
| Metrique | Median | Bon | Excellent |
|----------|--------|-----|-----------|
| Complexite cyclomatique moyenne | 5 | < 5 | < 3 |
| Couverture de tests | 55% | > 70% | > 85% |
| Unsafe blocks | Variable | Minimise | 0 hors FFI |

---

## 3. Metriques de processus par maturite d'equipe

### Startup / Early stage
| Metrique | Typique | Acceptable |
|----------|---------|------------|
| Couverture de tests | 20-40% | > 30% sur le coeur metier |
| Temps de deploiement | 1-4h | < 2h |
| Frequence de deploiement | 1-2x/semaine | > 1x/semaine |
| Temps de review | 1-3 jours | < 2 jours |
| % temps sur la dette | 5-10% | > 10% |

### Scale-up / Croissance
| Metrique | Typique | Acceptable |
|----------|---------|------------|
| Couverture de tests | 40-65% | > 60% |
| Temps de deploiement | 30min-2h | < 1h |
| Frequence de deploiement | 2-5x/semaine | > 3x/semaine |
| Temps de review | 4h-2 jours | < 1 jour |
| % temps sur la dette | 10-20% | > 15% |

### Enterprise / Mature
| Metrique | Typique | Acceptable |
|----------|---------|------------|
| Couverture de tests | 60-80% | > 75% |
| Temps de deploiement | 15-45min | < 30min |
| Frequence de deploiement | Quotidien+ | > 1x/jour |
| Temps de review | 2-8h | < 4h |
| % temps sur la dette | 15-25% | > 20% |

---

## 4. Cout de la dette technique

### Estimations de l'industrie

| Source | Estimation |
|--------|-----------|
| McKinsey (2020) | Les entreprises depensent 10-20% de leur budget tech a gerer la dette |
| Stripe (2018) | Les developpeurs passent 33% de leur temps a gerer la dette |
| CAST Research | Le cout moyen de la dette est de 3.61 USD par ligne de code |
| SonarSource | Chaque probleme de dette coute en moyenne 30 min de remediation |

### Formule d'estimation du cout

```
Cout annuel de la dette = Taille_equipe x Salaire_moyen x %_temps_dette

Exemple :
- Equipe de 5 devs
- Salaire moyen : 60K EUR/an
- Temps sur la dette : 25%
→ Cout = 5 x 60000 x 0.25 = 75 000 EUR/an
```

### Cout de la non-remediation

La dette technique a un effet compose : elle croit exponentiellement si non traitee.

| Temps sans remediation | Facteur de cout |
|-----------------------|-----------------|
| 6 mois | x 1.2 |
| 1 an | x 1.5 |
| 2 ans | x 2.5 |
| 3 ans | x 4.0 |
| 5 ans | x 8.0+ |

---

## 5. Benchmarks de deploiement (DORA metrics)

| Categorie | Frequence de deploiement | Lead time | Taux d'echec | MTTR |
|-----------|------------------------|-----------|-------------|------|
| Elite | Plusieurs/jour | < 1h | < 5% | < 1h |
| Haute | 1x/jour - 1x/semaine | 1 jour - 1 semaine | 5-10% | < 1 jour |
| Moyenne | 1x/semaine - 1x/mois | 1 semaine - 1 mois | 10-15% | 1 jour - 1 semaine |
| Basse | 1x/mois - 1x/6mois | 1-6 mois | 15-30% | 1 semaine - 1 mois |

---

## 6. Comment utiliser ces benchmarks

### Dans un rapport technique
- Comparer les metriques du projet aux medians du langage
- Identifier les ecarts significatifs (> 1 categorie d'ecart)
- Prioriser les metriques les plus eloignees du benchmark

### Dans un rapport executif
- Positionner le projet par rapport a l'industrie
- Montrer ou l'entreprise se situe sur l'echelle de maturite
- Utiliser les couts de l'industrie pour estimer l'impact financier

### Attention aux biais
- Ces chiffres sont des moyennes/medianes, chaque projet est unique
- Un Health Score de 60 peut etre excellent pour un projet legacy de 10 ans
- Les benchmarks sont des guides, pas des objectifs absolus
- Toujours contextualiser avec la realite du projet (contraintes, historique, equipe)
