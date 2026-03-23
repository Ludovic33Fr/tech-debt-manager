# Taxonomie de la dette technique

## 1. Dette de Code

### Description
Problemes directement lies a la qualite du code source : lisibilite, maintenabilite, complexite.

### Sous-categories

#### 1.1 Code Smells
- **Fonctions trop longues** (> 50 LOC)
- **Classes God Object** (> 20 methodes ou > 15 attributs)
- **Nesting profond** (> 4 niveaux d'indentation)
- **Parametres excessifs** (> 5 par fonction)
- **Magic numbers** (litteraux numeriques hors constantes)
- **Dead code** (fonctions, imports, variables non utilises)

#### 1.2 Duplication
- Blocs de code copies-colles (> 6 lignes identiques)
- Logique dupliquee avec variations mineures
- Constantes dupliquees dans plusieurs fichiers

#### 1.3 Complexite
- Complexite cyclomatique elevee (> 15 par fonction)
- Expressions conditionnelles imbriquees
- Switch/case avec trop de branches (> 10)

### Exemples par langage

**Python** :
```python
# MAUVAIS : God function, magic numbers, nesting profond
def process_order(order, user, items, discount, shipping, tax, currency):
    if order:
        if user:
            if items:
                total = 0
                for item in items:
                    if item.price > 100:
                        total += item.price * 0.9
                    elif item.price > 50:
                        total += item.price * 0.95
                    else:
                        total += item.price
                if discount:
                    if discount > 30:
                        total *= 0.7
```

**JavaScript/TypeScript** :
```typescript
// MAUVAIS : Couplage fort, pas de separation de responsabilites
export class UserService {
    async createUser(data: any) {
        // Validation directe dans le service
        if (!data.email || !data.email.includes('@')) throw new Error('bad email');
        // Acces direct a la DB
        const db = require('./database');
        const user = await db.query('INSERT INTO users...');
        // Envoi d'email directement
        const smtp = require('nodemailer');
        await smtp.sendMail({...});
        // Logging directement
        console.log('User created: ' + user.id);
        return user;
    }
}
```

**Java** :
```java
// MAUVAIS : Classe God Object
public class ApplicationManager {
    // Gere tout : users, orders, payments, notifications, reports, cache...
    public void createUser() { ... }
    public void deleteUser() { ... }
    public void processOrder() { ... }
    public void refundOrder() { ... }
    public void sendNotification() { ... }
    public void generateReport() { ... }
    public void clearCache() { ... }
    // ... 50+ methodes
}
```

---

## 2. Dette d'Architecture

### Description
Problemes structurels dans l'organisation et les relations entre composants.

### Sous-categories

#### 2.1 Couplage fort
- Modules fortement interdependants
- Dependances circulaires (A -> B -> C -> A)
- Violation du principe d'inversion de dependance

#### 2.2 Monolithe non structure
- Pas de separation claire en couches ou modules
- Logique metier melangee avec l'infrastructure
- Pas d'interfaces entre composants

#### 2.3 God Module
- Un module central importe par > 60% des autres modules
- Point unique de defaillance
- Modification risquee (effet domino)

#### 2.4 Layering Violations
- Module d'infrastructure qui importe un module UI
- Module domaine qui depend directement de la base de donnees
- Controller qui contient de la logique metier

### Detection

```
# Detecter les dependances circulaires (Python)
grep -r "from.*import\|import " --include="*.py" | analyse_graphe_imports

# Detecter les God Modules
grep -r "import\|require\|from" --include="*.{py,js,ts}" | sort | uniq -c | sort -rn | head -20

# Detecter les violations de couches
# Si un fichier dans /infra/ importe depuis /ui/ ou /presentation/
```

---

## 3. Dette de Tests

### Description
Manque de tests, tests fragiles, ou couverture insuffisante.

### Sous-categories

#### 3.1 Couverture insuffisante
- Pas de tests unitaires sur le code metier critique
- Couverture globale < 50%
- Chemins critiques non testes

#### 3.2 Tests fragiles
- Tests dependant de l'ordre d'execution
- Tests dependant de donnees externes ou de l'horloge
- Tests avec des timeouts ou des sleep
- Tests dependant de fixtures globales mutables

#### 3.3 Tests absents
- Pas de tests d'integration
- Pas de tests de regression pour les bugs corriges
- Pas de tests de performance/charge

#### 3.4 Tests de mauvaise qualite
- Tests sans assertions significatives (assert True)
- Tests qui testent l'implementation plutot que le comportement
- Tests trop couples au code source

### Indicateurs

| Indicateur | Bon | Attention | Critique |
|-----------|-----|-----------|----------|
| Ratio fichiers src/test | > 0.8 | 0.5 - 0.8 | < 0.5 |
| Couverture code metier | > 80% | 50-80% | < 50% |
| Temps CI des tests | < 5 min | 5-15 min | > 15 min |
| Tests flaky / semaine | 0 | 1-3 | > 3 |

---

## 4. Dette de Documentation

### Description
Documentation absente, obsolete ou incoherente avec le code.

### Sous-categories

- **Absente** : Pas de README, pas de docstrings, pas de commentaires sur la logique complexe
- **Obsolete** : Documentation qui ne reflete plus le code actuel
- **Incoherente** : Plusieurs sources de verite contradictoires
- **Insuffisante** : Documentation presente mais trop superficielle
- **API non documentee** : Endpoints, contrats, schemas non decrits

### Detection

```
# Fichiers sans docstrings (Python)
grep -rL '"""' --include="*.py" src/

# README absent
find . -maxdepth 2 -name "README*" | wc -l

# Commentaires TODO dans la doc
grep -r "TODO\|FIXME\|OUTDATED\|UPDATE" --include="*.md"
```

---

## 5. Dette d'Infrastructure

### Description
Problemes lies a l'outillage, au CI/CD, et a la configuration.

### Sous-categories

- **CI/CD manquant ou incomplet** : Pas de pipeline, deploiement manuel
- **Configurations hardcodees** : URLs, credentials, ports en dur dans le code
- **Pas de linting/formatting** : Pas de regle de style automatisee
- **Environnements non reproductibles** : Pas de Docker, pas de requirements pin
- **Monitoring absent** : Pas de logs structures, pas d'alerting

---

## 6. Dette de Dependances

### Description
Dependances obsoletes, vulnerables ou abandonnees.

### Sous-categories

- **Versions obsoletes** : Dependances en retard de > 2 versions majeures
- **Vulnerabilites connues** : CVEs non patchees
- **Libs abandonnees** : Pas de commit depuis > 2 ans
- **Dependances fantomes** : Declarees mais non utilisees
- **Lock file absent** : Pas de package-lock.json, poetry.lock, etc.

### Outils de detection

| Ecosysteme | Outil natif |
|-----------|------------|
| npm/yarn | `npm audit`, `npm outdated` |
| Python | `pip-audit`, `safety check` |
| Rust | `cargo audit` |
| Java | `mvn versions:display-dependency-updates` |
| Go | `go list -m -u all` |

---

## 7. Dette de Design/API

### Description
Interfaces mal concues, contrats non respectes, inconsistances d'API.

### Sous-categories

- **Interfaces incoherentes** : Nommage different pour des concepts similaires
- **Contrats non documentes** : Pas de schemas, pas de types
- **Breaking changes non geres** : Pas de versioning d'API
- **Over-fetching/Under-fetching** : API qui retourne trop ou pas assez de donnees
- **Erreurs mal gerees** : Codes d'erreur inconsistants, pas de messages utiles

---

## 8. Dette de Processus

### Description
Absence de pratiques de developpement saines.

### Sous-categories

- **Pas de code review** : Merge direct sans relecture
- **Pas de standards** : Pas de guide de contribution, pas de conventions
- **Pas de branching strategy** : Tout sur main/master
- **Pas de release process** : Versions non taguees, pas de changelog
- **Pas de pair programming** : Silos de connaissance
