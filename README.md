# 🎮 Jeu Stratégique avec Intelligence Artificielle

Un jeu de stratégie en temps réel développé en Python avec une IA adaptative qui apprend et évolue.

## 📋 Description

Ce jeu de stratégie met en opposition deux équipes (bleue et rouge) dans un combat tactique pour capturer des objectifs et éliminer les unités adverses. L'IA utilise un système d'apprentissage automatique pour améliorer ses performances au fil du temps.

## 🎯 Objectifs du Jeu

- **Objectifs Majeurs** : 3 points chacun
- **Objectifs Mineurs** : 1 point chacun
- **Premier à 50 points** ou dernier survivant gagne
- Les unités peuvent attaquer, se déplacer et capturer des objectifs

## 🚀 Installation et Lancement

### Prérequis
```bash
pip install pygame
```

### Lancement
```bash
python jeu.py
```

## 🎮 Contrôles

- **Clic gauche** : Sélectionner une unité
- **Clic droit** : Déplacer ou attaquer
- **Espace** : Passer le tour
- **Échap** : Menu/Quitter

## 🤖 Intelligence Artificielle

L'IA implémente plusieurs stratégies :

### Stratégies de Base
- **Agressive** : Attaque prioritaire des unités faibles
- **Défensive** : Protection des unités et repli tactique
- **Objective** : Focus sur la capture d'objectifs
- **Exploration** : Découverte de la carte
- **Groupe** : Coordination des unités

### Apprentissage Adaptatif
L'IA analyse ses performances et ajuste ses stratégies :
- Calcul des taux de succès par action
- Évolution des poids stratégiques
- Adaptation selon les résultats obtenus

## 📁 Structure du Projet

```
.
├── jeu.py              # Point d'entrée principal
├── ia.py               # Intelligence artificielle
├── unit.py             # Classe des unités
├── display.py          # Gestion de l'affichage
├── init.py             # Configuration et constantes
├── ai_stats.json       # Données d'apprentissage de l'IA
└── README.md           # Ce fichier
```

## ⚙️ Fonctionnalités Techniques

### Système de Combat
- Calcul de dégâts basé sur la distance
- Gestion des points de vie
- Mécaniques de ligne de vue

### Gestion des Objectifs
- Capture progressive des points stratégiques
- Bonus selon le type d'objectif
- Contrôle territorial

### IA Adaptative
- Analyse des performances en temps réel
- Ajustement automatique des stratégies
- Sauvegarde persistante de l'apprentissage

## 🎲 Mécaniques de Jeu

### Types d'Actions IA
- **attack** : Attaque directe d'une unité ennemie
- **attack_weak** : Ciblage prioritaire des unités blessées
- **flee** : Repli tactique en cas de danger
- **group** : Regroupement avec des alliés
- **move_major/minor** : Déplacement vers les objectifs
- **explore** : Exploration de zones inconnues

### Calcul des Scores
- Points par objectifs capturés
- Bonus de survie des unités
- Malus pour les pertes

## 🏆 Niveaux de Difficulté IA

L'IA s'adapte automatiquement selon ses performances :
- **Débutant** : Stratégies basiques
- **Intermédiaire** : Combinaison de tactiques
- **Expert** : Adaptation fine et anticipation

## 📊 Statistiques

Le jeu trace automatiquement :
- Taux de victoire
- Actions les plus efficaces
- Évolution des performances
- Temps de jeu moyen

## 🔧 Configuration

Les paramètres peuvent être ajustés dans `init.py` :
- Taille de la carte
- Nombre d'unités
- Points de vie des unités
- Paramètres de l'IA

## 🐛 Dépannage

### Problèmes Courants
- **Pygame non installé** : `pip install pygame`
- **Fichier stats manquant** : Se recrée automatiquement
- **IA trop forte/faible** : L'adaptation est automatique

### Logs et Debug
Les informations de debug s'affichent dans la console lors du jeu.

## 👥 Développement

Développé dans le cadre d'un projet étudiant avec :
- Architecture modulaire
- Code documenté
- Système de tests intégré

## 📝 License

Projet éducatif - Usage libre pour l'apprentissage.

---

**Bon jeu et bonne chance contre l'IA !** 🎯