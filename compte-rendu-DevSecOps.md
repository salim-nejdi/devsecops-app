# Compte rendu — DevSecOps Projet

## 1. Objetcif

Ce document décrit le **Threat Modeling** du projet devsecops.

L'objectif est de partir de l'architecture et du code source de l'application, pour identifier **les composants**, **les actis à protéger**, **les acteurs**, **les flux**, pûis d'associer les menaces aux catégories **STRIDE** et aux contrôles DevSecops correspondants.

---

## 2. Prémiètre

Le périmètre couvre la chaîne suivante:

```text
Développeur
    ↓
GitHub Repository
    ↓
GitHub Actions
    ↓
Build Docker
    ↓
GitHub Container Registry (GHCR)
    ↓
K3s
    ↓
Application Flask
    ↓
SQLite
```

Choix des technologies:

- Github pour le dépôt Git ;
- gitHub Actions pour la CI/CD ;
- Docker pour la conteneurisation
- GHCR pour stocker les images ;
- K3s en mono-noeud pour l'environnement Kube ;
- Le microframwork Flask pour l'application ;
- SQLite comme base de donnée locale pour sa légèreté;

---

## 3. Composants

Les composants principaux sont :

```text
1. VM de développement
2. Repository GitHub
3. GitHub Actions
4. Workflow CI/CD
5. Dockerfile
6. Image Docker
7. GitHub Container Registry
8. K3s
9. Deployment Kubernetes
10. Service Kubernetes
11. Application Flask
12. Base SQLite
13. Fichiers uploadés
14. Dépendances Python
```

---

## 4. Assets

Les principaux actifs à protéger sont :

### Code source

```text
app.py
Dockerfile
requirements.txt
workflows GitHub Actions
manifests K3s
```

### Secrets et credentials

Exemples :

```text
tokens GitHub
secrets applicatifs
variables CI/CD
credentials BDD
credentials Kubernetes
```

### Artefacts

```text
images Docker
digests
rapports de scan
```

### Infrastructure

```text
runner GitHub Actions
registry GHCR
noeud K3s
```

---

## 5. Acteurs

### Acteurs légitimes

```text
Développeur
GitHub Actions
K3s
```

### Acteurs potentiellement malveillants

```text
Utilisateur externe
Attaquant Internet
Compte GitHub compromis
Dépendance tierce compromise
Image ou package malveillant
Contributeur malveillant (hein les red team on vous voit ! )
```
---

## 6. Flux principaux

### Flux 1 — Commit (Frontières de confiance)

```text
Développeur
↓
git push
↓
GitHub
```

### Flux 2 — CI (Frontières de confiance)

```text
GitHub
↓
GitHub Actions
↓
lint
↓
tests
```

### Flux 3 — Build

```text
GitHub Actions
↓
Docker build
↓
image
```

### Flux 4 — Registry (Frontières de confiance)

```text
Image Docker
↓
tag avec SHA Git
↓
GHCR
```

### Flux 5 — Déploiement (Frontières de confiance)

```text
GHCR
↓
K3s
↓
Deployment
↓
Pod
```

### Flux 6 — Utilisation (Frontières de confiance)

```text
Utilisateur
↓
Service K3s
↓
Flask
↓
SQLite / uploads
```
Chaque traversée de frontière de confiance constitue une zone où il faut vérifier :

- l'identité ;
- les permissions ;
- l'intégrité ;
- la provenance ;
- les secrets ;
- les données échangées.
---

## 7. Tableau des menaces

Par manque de temps, l'ensemble des contrôles identifiés dans le Threat Modeling n'a pas pu être implémenté. Nous avons donc priorisé les mécanismes les plus représentatifs de la chaîne DevSecOps afin de couvrir les principaux risques du projet et de valider le fonctionnement des contrôles de sécurité.

| Composant | Menace | STRIDE | Impact potentiel | Contrôle envisagé | Outil / mécanisme |
|---|---|---|---|---|---|
| GitHub | Compte développeur compromis | Spoofing | Commit ou modification non autorisée | Authentification forte, permissions minimales | GitHub |
| GitHub | Modification malveillante du code | Tampering | Code compromis livré | Review, protection de branche | GitHub |
| GitHub | Secret commité | Information Disclosure | Fuite de credential | Secret scanning | Gitleaks |
| GitHub Actions | Workflow CI modifié | Tampering | Exécution de commandes malveillantes | Review du workflow | GitHub |
| GitHub Actions | Token trop permissif | Elevation of Privilege | Accès excessif au dépôt ou registry | Least privilege | permissions GitHub Actions |
| GitHub Actions | Absence de logs exploitables | Repudiation | Difficulté à retracer une action | Conservation des logs | GitHub Actions |
| Dépendances | Package vulnérable | Elevation / Tampering | Exploitation de vulnérabilités | SCA | Trivy |
| Dépendances | Package malveillant | Tampering | Compromission de l'application | Version pinning + SCA | Trivy |
| Dockerfile | Image de base vulnérable | Elevation / Tampering | Vulnérabilités dans l'image | Image scanning | Trivy |
| Dockerfile | Exécution root | Elevation of Privilege | Impact accru en cas de compromission | Docker hardening | Trivy / revue |
| Dockerfile | Secret présent dans l'image | Information Disclosure | Fuite de credential | Secret scanning / image scan | Gitleaks / Trivy |
| GHCR | Image remplacée ou ambiguë | Tampering | Mauvaise image déployée | Tag SHA + digest | GHCR |
| GHCR | Image publique contenant des données sensibles | Information Disclosure | Exposition publique | Vérifier le contenu avant publication | Trivy / Gitleaks |
| K3s | Conteneur privilégié | Elevation of Privilege | Accès excessif au nœud | SecurityContext restrictif | Trivy |
| K3s | Mauvaise configuration Kubernetes | Elevation / Information Disclosure | Surface d'attaque accrue | IaC scanning | Trivy |
| K3s | Service trop exposé | Information Disclosure / DoS | Accès externe non souhaité | Contrôle réseau | K3s / NetworkPolicy |
| Flask | Entrées utilisateur non contrôlées | Tampering | Manipulation de requêtes | Validation des entrées | Semgrep + tests |
| Flask | Données sensibles exposées | Information Disclosure | Fuite d'informations | Contrôle des réponses | Semgrep / tests |
| Flask | Action non autorisée | Spoofing / Elevation | Opération réalisée sans contrôle | AuthN/AuthZ | Code applicatif |
| Flask | Requête coûteuse ou abusive | Denial of Service | Saturation du service | Validation / rate limiting | Application |
| Uploads | Fichier non sûr | Tampering | Contenu malveillant stocké | Validation du type et du nom | Application / SAST |
| SQLite | Requête manipulée | Tampering / Information Disclosure | Lecture ou modification de données | Requêtes paramétrées | Semgrep / tests |
| Pipeline | Scan ignoré ou contourné | Tampering | Livraison malgré un problème | Security Gate | GitHub Actions |
| Pipeline | Finding non traçable | Repudiation | Difficulté à justifier une décision | Rapports conservés | Artifacts CI |

---

## 8. Contrôles DevSecOps

Les contrôles seront ajoutés progressivement dans la CI/CD.

### Secret scanning

```text
Outil : Gitleaks
But   : détecter les secrets présents dans Git
```

### SAST

```text
Outil : Semgrep
But   : analyser le code source sans l'exécuter
```

### SCA / dépendances

```text
Outil : Trivy
But   : identifier les CVE des dépendances
```

### IaC scanning

```text
Outil : Trivy
But   :  analyser les manifests K3s et les fichiers de configuration de l'infrastructure avant déploiement.
```

### Image scanning

```text
Outil : Trivy
But   : analyser l'image Docker produite
```

### Tests

```text
Outil : pytest
But   : valider le comportement applicatif
```

### Lint

```text
Outil : Ruff
But   : détecter erreurs et mauvaises pratiques Python
```

---

## 9. Security Gates

La politique prévue est :

```text
CRITICAL → BLOCK
HIGH     → BLOCK
MEDIUM   → WARNING
LOW      → INFORMATION
```

Le pipeline devra donc être capable de :

```text
Scan
↓
Finding
↓
Classification
↓
Décision
```

Exemple :

```text
Trivy détecte une vulnérabilité CRITICAL
↓
le job retourne un échec
↓
le pipeline s'arrête
↓
aucune image n'est déployée
```

---

## 10. Pipeline CI/CD mise en place

La pipeline finale est exécutée avec **GitHub Actions** sur les `push`.

```text
Développeur
    ↓
Git push / Pull Request
    ↓
GitHub Actions
    ↓
Ruff + Pytest
    ↓
├── Gitleaks
├── Semgrep
├── Trivy dépendances
├── Trivy IaC
├── OPA / Conftest
├── OWASP ZAP
└── SBOM CycloneDX
    ↓
Security Gates
    ↓
Vulnérabilité bloquante ?
   /                 \
 OUI                 NON
  ↓                   ↓
Pipeline          Build Docker
bloquée               ↓
                  Trivy Image
                      ↓
                 Security Gate
                      ↓
                     GHCR
                      ↓
              Récupération digest
                      ↓
                    Cosign
                      ↓
             Vérification signature
                      ↓
               Image disponible
                      ↓
             K3s (déploiement manuel)
```

Les scans Trivy sur les dépendances, l'IaC et l'image bloquent la pipeline en cas de vulnérabilité `HIGH` ou `CRITICAL`.

L'image n'est poussée dans **GHCR** depuis `main` que si les contrôles nécessaires sont validés. Elle est ensuite signée avec **Cosign** et sa signature est vérifiée.

Le déploiement sur K3s a été réalisé et validé manuellement. Le projet étant principalement centré sur les tests et la sécurisation de la chaîne CI/CD, nous avons fait le choix de ne pas automatisé jusqu’au déploiement final de l’image, afin de nous concentrer sur le cœur du projet et aussi par manque de temps.

---

## 11. BONUS ChatOps et Intelligence Artificielle

Un bot **Discord ChatOps** utilisant **OpenAI Codex** afin de mettre en place un agent spécialisé dans notre projet DevSecOps.

Le bot surveille les pipelines GitHub Actions, récupère leurs résultats et centralise les findings de sécurité dans Discord. Codex dispose du contexte du projet et peut analyser le code ainsi que les vulnérabilités détectées afin de proposer une remédiation adaptée.

```text
GitHub Actions
      ↓
Résultats des scans
      ↓
Bot Discord
      ↓
OpenAI Codex
      ↓
Analyse
      ↓
Proposition de remédiation
```

Codex est exécuté en **lecture seule** et ne modifie pas directement le repository.

Lorsqu'une remédiation est demandée depuis Discord, l'agent propose les corrections. Le bot contrôle ensuite les modifications et les applique sur une branche dédiée.

```text
Finding détecté
      ↓
Analyse Codex
      ↓
Proposition de correction
      ↓
Validation depuis chat discord
      ↓
Branche remediation/
      ↓
Application des corrections
      ↓
Ruff + Pytest
      ↓
Git push
      ↓
Nouvelle pipeline
      ↓
Re-scan de sécurité
      ↓
Si pas de vulnérabilité merge vers la branch main (non mis en place volontairement pour les besoins du projet)
```

La branche `main` n'est donc jamais modifiée directement par l'IA.

Si de nouveaux problèmes sont détectés, une nouvelle remédiation peut être effectuée sur la même branche jusqu'à obtenir une version validée.

L'étape finale prévue était de merger la branche `remediation/*` vers `main` une fois tous les contrôles validés.
Nous avons volontairement choisi de ne pas automatiser cette dernière étape afin de conserver la branche `main` vulnérable pour la démonstration lors de la soutenance.

L'IA assiste donc l'analyse et la remédiation, tandis que le bot et la CI/CD conservent le contrôle sur les modifications réellement appliquées.

---

## 12. Protection Git

La branche `main` a été protégée avec un **Ruleset GitHub**.

```text
Pull Request obligatoire
1 approbation minimum
nouvelle validation après modification
résolution des conversations
interdiction du force-push
interdiction de supprimer main
```
---

## 13. BONUS Bis Challenge Red Team

Nous avons audité deux projets d'autres groupes.

### Groupe de Rémi Anas et Esteban:

Nous avons réussi à contourner leur contrôle SAST avec une exécution de commande obfusquée.

Une Pull Request externe a passé leurs contrôles de sécurité puis a été mergée sur `main`, démontrant qu'une modification malveillante pouvait contourner leur Security Gate.

### Groupe Eli, Enza et Eliot:

Nous avons démontré localement qu'il était possible de masquer des CVE Trivy avec `.trivyignore`.

Une Merge Request contenant une dépendance vulnérable ainsi que les suppressions Trivy a ensuite été mergée sur leur branche `main`.

Le contournement réel du gate Trivy sur leur infrastructure n'a cependant pas pu être confirmé, car leur pipeline a rencontré une panne du runner avant l'analyse Trivy.

Nous avons également identifié :

```text
images et outils CI utilisant des tags :latest
image poussée dans le registry avant son scan Trivy
```

Le détail des attaques et des preuves est disponible dans `REDTEAM-FINDINGS.md`.

---

## 14. Conclusion

Le projet a permis de mettre en place une chaîne DevSecOps complète intégrant les principaux contrôles de sécurité vus dans le cadre du cours : analyse du code, détection de secrets, analyse des dépendances, contrôle des manifests Kubernetes, scan de l'image Docker, DAST, génération d'un SBOM, Security Gates et signature de l'image.

L'ajout du bot ChatOps connecté à Codex a permis d'aller plus loin en ajoutant une boucle de remédiation assistée par IA. 

Le projet nous a donc permis de mettre en pratique une approche DevSecOps complète, basée sur le principe suivant : **détecter, bloquer, analyser, corriger puis re-scanner avant validation**.
