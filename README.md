# Tech Debt Manager

[English](#english) · [Français](#français)

---

## English

Agent skill to analyze, evaluate, prioritize, and plan the reduction of technical debt in a software project.

### Purpose

`tech-debt-manager` helps engineering teams to:

- audit codebase health;
- identify risk areas (maintainability, tests, complexity, coupling);
- prioritize remediation work by business impact and effort;
- turn technical debt into a concrete action plan.

### When to use it

Use this skill when you want to:

- run a technical debt assessment;
- prepare a refactoring plan;
- balance feature delivery and stabilization;
- produce a debt report for management or stakeholders;
- estimate the cost of technical debt.

### Scope

The skill can support you on:

- qualitative code analysis (code smells, architecture, readability);
- quantitative analysis (cyclomatic complexity, test coverage, incidents);
- prioritization (impact, urgency, effort, risk);
- defining a remediation roadmap;
- building tracking metrics.

### Recommended approach

1. **Inventory** observed technical issues.
2. **Qualify** each debt item (impact, frequency, risk, cost).
3. **Prioritize** with a simple method (impact × urgency / effort).
4. **Plan** work in batches (quick wins, structural initiatives).
5. **Track** progress with KPIs and regular reviews.

### Expected outputs

You should get:

- a prioritized technical debt backlog;
- a proposed remediation schedule;
- an estimate of expected gains (quality, speed, risk reduction);
- governance recommendations (definition of done, reviews, standards).

### Good practices

- Address debt continuously, not only during crises.
- Reserve a fixed capacity each sprint for remediation.
- Tie each technical action to a product or business goal.
- Measure before and after to ground decisions in data.
- Avoid large “big bang” efforts without shippable increments.

### Contributing

Contributions are welcome. To propose an improvement:

1. Open an issue describing the problem or idea.
2. Suggest a solution with a usage example.
3. Add tests or validation cases when possible.

### Global install (`npx skills`)

To add this skill globally from this repository, run:

```bash
npx skills add Ludovic33Fr/tech-debt-manager@tech-debt-manager -g -y
```

---

## Français

Skill pour analyser, évaluer, prioriser et planifier la réduction de la dette technique dans un projet logiciel.

### Objectif

`tech-debt-manager` aide les équipes techniques à :

- auditer la santé d’un codebase ;
- identifier les zones de risque (maintenabilité, tests, complexité, couplage) ;
- prioriser les actions de remédiation selon l’impact business et l’effort ;
- transformer la dette technique en plan d’action concret.

### Cas d’usage

Utilisez ce skill lorsque vous voulez :

- réaliser un diagnostic de dette technique ;
- préparer un plan de refactoring ;
- arbitrer entre livraison de fonctionnalités et stabilisation ;
- produire un rapport de dette pour le management ou les parties prenantes ;
- estimer le coût de la dette technique.

### Ce que couvre le skill

Le skill peut vous accompagner sur :

- l’analyse qualitative du code (code smells, architecture, lisibilité) ;
- l’analyse quantitative (complexité cyclomatique, couverture de tests, incidents) ;
- la priorisation (impact, urgence, effort, risque) ;
- la définition d’une feuille de route de remédiation ;
- la construction d’indicateurs de suivi.

### Approche recommandée

1. **Inventorier** les problèmes techniques observés.
2. **Qualifier** chaque dette (impact, fréquence, risque, coût).
3. **Prioriser** avec une méthode simple (impact × urgence / effort).
4. **Planifier** les actions par lots (quick wins, chantiers structurants).
5. **Suivre** l’évolution avec des KPI et une revue régulière.

### Sorties attendues

En sortie, vous devez obtenir :

- un backlog de dette technique priorisé ;
- une proposition de planning de remédiation ;
- une estimation des gains attendus (qualité, vitesse, réduction de risque) ;
- des recommandations de gouvernance (definition of done, revues, standards).

### Bonnes pratiques

- Traiter la dette en continu, pas uniquement lors de crises.
- Réserver une capacité fixe par sprint pour la remédiation.
- Lier chaque action technique à un objectif produit ou business.
- Mesurer avant et après pour objectiver les décisions.
- Éviter les « gros chantiers » sans incréments livrables.

### Contribution

Les contributions sont les bienvenues. Pour proposer une amélioration :

1. Ouvrez une issue avec le problème ou l’idée.
2. Proposez une solution avec un exemple d’utilisation.
3. Ajoutez, si possible, des tests ou des cas de validation.

### Installation globale (`npx skills`)

Pour ajouter ce skill globalement depuis ce repository, exécutez :

```bash
npx skills add Ludovic33Fr/tech-debt-manager@tech-debt-manager -g -y
```
