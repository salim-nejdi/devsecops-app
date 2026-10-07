# DevSecOps - Projet

Projet réalisé dans le cadre du module **DevSecOps – ESGI M2**.

L’objectif est de mettre en place une chaîne de livraison sécurisée autour d’une application Flask volontairement vulnérable.

**BONUS:** Un bot ChatOps Discord récupère les résultats des pipelines GitHub Actions, centralise les findings de sécurité et utilise **OpenAI Codex** pour analyser les vulnérabilités et proposer des corrections.

Le projet couvre l’ensemble du cycle :

**Code → Tests → Scans de sécurité → Security Gates → Analyse IA → Remédiation sur branche dédiée→ Re-scan → Merge + Livraison**

---

## 1. Objectif du projet

L’application présente dans la branche `main` contient volontairement plusieurs vulnérabilités afin de tester la capacité de la chaîne CI/CD à les détecter et à bloquer la livraison.

La plateforme mise en place permet notamment de :

- vérifier la qualité du code ;
- exécuter les tests automatisés ;
- détecter les secrets ;
- analyser le code avec du SAST ;
- analyser les dépendances ;
- analyser les manifests Kubernetes ;
- appliquer des politiques de sécurité avec OPA / Conftest ;
- analyser l’image Docker ;
- exécuter un scan DAST ;
- générer un SBOM ;
- bloquer la livraison lorsqu’une vulnérabilité critique ou élevée est détectée ;
- signer l’image finale avec Cosign ;
- proposer des remédiations via un bot ChatOps.

---

## 2. Architecture

```text
Développeur
    |
    v
GitHub
    |
    v
GitHub Actions
    |
    +--> Ruff / Pytest
    |
    +--> Gitleaks
    |
    +--> Semgrep
    |
    +--> Trivy Dependencies
    |
    +--> Trivy IaC
    |
    +--> OPA / Conftest
    |
    +--> OWASP ZAP
    |
    +--> CycloneDX SBOM
                   |
                   v
              SECURITY GATES
                    |
             Vulnérabilité ?
               /         \
             oui         non
              |            |
              v            v
        Livraison       Build image
         bloquée            |
              |             v
              |         Trivy Image
              |             |
              |             v
              |           GHCR
              |             |
              |             v
              |          Cosign
              |             |
              |             v
              |            K3s
              |
              v
        Bot ChatOps Discord
              |
              v
         OpenAI Codex
              |
              v
        Analyse des findings
              |
              v
      Proposition de remédiation
              |
              v
       Branche remediation/*
              |
              v
         Nouvelle pipeline
              |
              v
            Re-scan
              |
              v
       Corrections validées ?
          /             \
        non             oui
         |               |
         v               v
  Nouvelle remédiation   Merge / Livraison
