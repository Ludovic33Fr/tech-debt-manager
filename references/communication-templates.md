# Templates de communication pour differentes audiences

## 1. Audience technique (developpeurs)

### Template rapport technique

```markdown
# Audit de dette technique — [Module/Projet]

## Metriques cles
| Metrique | Valeur | Seuil | Statut |
|----------|--------|-------|--------|
| Complexite cyclomatique moyenne | XX | < 10 | OK/KO |
| Duplication | XX% | < 5% | OK/KO |
| Couverture de tests | XX% | > 80% | OK/KO |
| Dependances obsoletes | XX | 0 | OK/KO |

## Findings detailles

### [CRIT-001] Description du probleme
- **Fichier** : `path/to/file.ext:L42`
- **Severite** : Critique
- **Type** : Code / Architecture / Tests / etc.
- **Description** : Explication technique detaillee
- **Impact** : Ce que ca cause concretement
- **Remediation** :
  ```diff
  - ancien code
  + nouveau code
  ```
- **Effort estime** : 2h / 1 jour / 1 sprint
- **Tests a ajouter** : Description des tests necessaires

## Backlog de remediation
| ID | Description | Severite | Effort | Priorite |
|----|-------------|----------|--------|----------|
| CRIT-001 | ... | Critique | 2h | P0 |
| HIGH-001 | ... | Eleve | 1j | P1 |
```

### Vocabulaire technique
- Utiliser les termes techniques precis (complexite cyclomatique, couplage afferent, etc.)
- Fournir des snippets de code et des diff
- Localiser precisement les problemes (fichier:ligne)
- Proposer des solutions concretes avec du code

---

## 2. Audience management (tech leads, engineering managers)

### Template rapport management

```markdown
# Rapport de dette technique — [Projet]
**Date** : [date] | **Health Score** : [XX/100]

## Resume
La dette technique de [projet] est a un niveau [bon/attention/critique].
Les principaux risques sont [X, Y, Z].
L'effort total de remediation est estime a [N] jours-homme.

## Impact sur l'equipe
- **Velocite** : La dette ralentit le developpement de ~[X]%
- **Incidents** : [N] incidents lies a la dette sur les 3 derniers mois
- **Onboarding** : Un nouveau dev met [N] jours de plus que necessaire

## Top 5 des actions prioritaires
| # | Action | Impact | Effort | Quick Win? |
|---|--------|--------|--------|------------|
| 1 | ... | Eleve | 2j | Oui |
| 2 | ... | Eleve | 1 sprint | Non |

## Plan propose
### Sprint N (quick wins)
- [ ] Action 1 (2j)
- [ ] Action 2 (1j)

### Sprint N+1 a N+3
- [ ] Action 3 (1 sprint)
- [ ] Action 4 (2 sprints)

## Ressources necessaires
- [N] jours de developpeur sur le sprint courant
- [N] sprints dedies sur le trimestre
```

### Vocabulaire management
- Parler en jours-homme ou story points
- Quantifier l'impact sur la velocite et les incidents
- Utiliser des graphiques et des tendances
- Montrer le ROI des actions de remediation
- Eviter le jargon technique trop specifique

---

## 3. Audience executive (CTO, VP Engineering, direction)

### Template rapport executif

```markdown
# Sante technique — [Projet/Produit]
**Score de sante** : [XX/100] | **Tendance** : [amelioration/stable/degradation]

## En une phrase
[Le projet est en bonne sante technique / presente des risques significatifs
qui impactent notre capacite a livrer et notre fiabilite.]

## Indicateurs cles
- **Fiabilite** : [X] incidents/mois lies a la qualite du code
- **Productivite** : L'equipe passe ~[X]% de son temps a gerer la dette
- **Risque** : [N] vulnerabilites de securite non corrigees
- **Cout** : La dette represente environ [N] jours-homme de travail

## Comparaison avec les benchmarks de l'industrie
| Metrique | Notre projet | Benchmark industrie | Ecart |
|----------|-------------|--------------------|----- |
| Health Score | XX/100 | 65/100 | +/- XX |
| Temps de deploiement | Xh | 30min | ... |

## Recommandation
[Investir X% du temps de l'equipe pendant N mois pour ramener
le score de sante a [cible]. ROI estime : [reduction incidents,
amelioration velocite].]

## Budget demande
- [N] sprints dedies (soit ~[N] jours-homme)
- Cout estime : [N] EUR/USD
- ROI attendu sous [N] mois
```

### Vocabulaire executif
- Parler en euros/dollars, risques business, et ROI
- Utiliser des analogies accessibles :
  - "La dette technique, c'est comme l'entretien differe d'un batiment : moins on en fait, plus ca coute cher a rattraper"
  - "Chaque fonctionnalite ajoutee sur de la dette technique coute 2x plus cher et prend 2x plus de temps"
  - "C'est comme rouler avec des pneus uses : on avance, mais le risque d'accident augmente chaque jour"
- Graphiques visuels : jauge, tendance, radar
- Limiter a 1-2 pages / 5-8 slides max
- Toujours conclure avec une recommandation claire et un budget

---

## 4. Presentation PowerPoint (structure)

### Slide 1 : Titre
- Titre : "Sante technique — [Projet]"
- Sous-titre : Date, auteur
- Visual : Jauge du Health Score (couleur selon le niveau)

### Slide 2 : Resume executif
- 3 bullet points maximum
- 1 graphique radar des categories de dette
- Message cle en gras

### Slide 3 : Top 5 des risques
- Tableau simple : Risque | Impact | Probabilite | Severite
- Code couleur : rouge/orange/jaune/vert

### Slide 4 : Tendance (si donnees historiques)
- Graphique lineaire du Health Score sur les derniers mois
- Points d'inflexion annotes

### Slide 5 : Plan d'action
- Timeline visuelle : Court terme / Moyen terme / Long terme
- Quick wins mis en evidence
- Jalons cles

### Slide 6 : ROI et budget
- Cout de la dette actuelle (en productivite perdue)
- Cout du plan de remediation
- Economies attendues
- Break-even point

### Slide 7 : Demande
- Ce qu'on demande concretement (temps, ressources, budget)
- Prochaines etapes
- Date de revue

---

## 5. Adaptation du ton par contexte

### En cas de crise (incident lie a la dette)
- Ton urgent mais factuel
- Focus sur la cause racine et la remediation immediate
- Plan a court terme concret
- Pas de blame

### En revue reguliere
- Ton neutre et factuel
- Tendances et evolution
- Celebration des ameliorations
- Focus sur les prochaines etapes

### En justification de budget
- Ton persuasif mais base sur les donnees
- Chiffrer l'impact financier de l'inaction
- Montrer le ROI concret
- Proposer des scenarios (minimal, recommande, optimal)
