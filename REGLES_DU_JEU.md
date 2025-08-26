# RÈGLES DU JEU - Stratégie Tour par Tour

## 🎯 OBJECTIF DU JEU

Le but est d'être le premier à atteindre **50 points** en contrôlant des objectifs stratégiques sur la carte, ou d'éliminer toutes les unités adverses.

## 🗺️ TERRAIN DE JEU

- **Grille 20x20 cases** avec coordonnées (0,0) en haut à gauche
- **Objectifs stratégiques** répartis au centre de la carte :
  - **1 Objectif Majeur** (losange jaune) = **3 points par tour**
  - **3 Objectifs Mineurs** (cercle doré) = **1 point par tour**

## 👥 UNITÉS ET FORCES

### Composition des Forces
- **Joueur** : 5 unités bleues (déploiement ligne du haut, y=0)
- **IA** : 5 unités rouges (déploiement ligne du bas, y=19)

### Caractéristiques des Unités
- **Points de Vie** : 2 PV par unité
- **Portée de mouvement** : 1 case (adjacent, y compris diagonale)
- **Portée d'attaque** : 1 case (adjacent, y compris diagonale)
- **États** : Peut bouger/Déjà bougé (affiché par la couleur)

## 🎮 MÉCANIQUES DE JEU

### Tour de Jeu
1. **Phase Joueur** : Déplace et/ou attaque avec ses unités
2. **Phase IA** : L'IA joue ses unités automatiquement
3. **Décompte des Points** : Attribution selon les objectifs contrôlés
4. **Vérification Victoire** : 50 points ou élimination complète

### Contrôles Joueur
- **Clic Gauche** : Sélectionner une unité (cyclage si plusieurs sur la case)
- **Clic Droit** : Déplacer l'unité sélectionnée OU attaquer une cible
- **Espace / Bouton** : Terminer son tour
- **Indicateur Visuel** : Bordure verte = unité sélectionnée

## ⚔️ SYSTÈME DE COMBAT

### Mécanique d'Attaque
Une unité peut attaquer une cible adjacente selon ces règles :

#### Cible n'ayant pas encore bougé ce tour :
- **Sans obstacle** : La cible est repoussée d'1 case (selon la direction d'attaque)
- **Avec obstacle** : La cible est **éliminée instantanément** (repoussée contre bord/unité)

#### Cible ayant déjà bougé ce tour :
- **Dégâts** : -1 PV à la cible
- **Repoussement** : 1 case si possible
- **Obstacle** : Si repoussée contre obstacle → **élimination**
- **Mort** : Si 0 PV → unité éliminée

### États Après Combat
- L'**attaquant** est marqué "a bougé"
- La **cible** est marquée "a bougé" (si survit)

## 🏆 SYSTÈME DE POINTS

### Gain de Points (par tour)
- **Objectif Majeur contrôlé** : +3 points
- **Objectif Mineur contrôlé** : +1 point
- **Contrôle** : Avoir une unité sur la case objective

### Accumulation
- Les points s'accumulent **tour après tour**
- **Objectif** : Premier à 50 points gagne
- **Stratégie** : Balance entre attaque, défense et contrôle d'objectifs

## 🏅 CONDITIONS DE VICTOIRE

1. **Victoire par Points** : Atteindre 50 points en premier
2. **Victoire par Élimination** : Détruire toutes les unités ennemies
3. **Priorité** : La vérification se fait dans l'ordre ci-dessus

## 🤖 INTELLIGENCE ARTIFICIELLE

L'IA utilise un système de prise de décision hiérarchique :

### Priorités Tactiques (ordre décroissant)
1. **Attaque Létale** : Éliminer unité ennemie affaiblie (1 PV)
2. **Attaque Opportuniste** : Attaquer si obstacle disponible
3. **Contrôle Objectif Majeur** : Capturer/défendre (3 pts)
4. **Contrôle Objectif Mineur** : Capturer/défendre (1 pt)
5. **Blocage Ennemi** : Empêcher capture d'objectif
6. **Positionnement Défensif** : Protection/regroupement
7. **Exploration** : Mouvement vers centre/positions stratégiques

### Apprentissage Automatique
- **Statistiques** : Taux de succès par action
- **Adaptation** : Priorités ajustées selon performances
- **Exploration** : 10-20% d'actions exploratoires
- **Amélioration** : Performance s'améliore au fil des parties

## 📊 INTERFACE UTILISATEUR

### Affichage Principal
- **Grille de Jeu** : 20x20 avec unités et objectifs
- **Scores** : Joueur (gauche) vs IA (droite)
- **Progression** : Barres vers victoire (50 points)
- **Tour Actuel** : "Tour Joueur" / "Tour IA"

### Informations Unité Sélectionnée
- **Type** : Unité Joueur/IA
- **Points de Vie** : Barre visuelle + valeur numérique
- **État** : Peut bouger / A bougé

### Codes Couleurs
- **Bleu clair** : Unité joueur peut bouger
- **Bleu foncé** : Unité joueur a bougé
- **Rouge clair** : Unité IA peut bouger  
- **Rouge foncé** : Unité IA a bougé
- **Vert** : Unité sélectionnée
- **Jaune** : Objectif majeur (3 pts)
- **Doré** : Objectif mineur (1 pt)

## 🎯 STRATÉGIES RECOMMANDÉES

### Pour le Joueur
1. **Contrôle du Centre** : Viser les objectifs dès le début
2. **Formation Groupée** : Éviter l'isolement des unités
3. **Attaques Coordonnées** : Utiliser le repoussement tactique
4. **Protection Mutuelle** : Couvrir les unités affaiblies
5. **Timing** : Bouger les unités vulnérables en premier

### Conseils Avancés
- **Piège à Obstacle** : Attirer l'ennemi près du bord pour élimination
- **Sacrifice Tactique** : Perdre une unité pour position avantageuse  
- **Contrôle de Zone** : Dominer une zone plutôt que se disperser
- **Course aux Points** : Parfois mieux vaut fuir que combattre

## 🐛 CAS PARTICULIERS

### Unités Multiples sur Même Case
- **Sélection** : Clic répétés pour cycler entre unités
- **Combat** : Attaque affecte toutes les unités présentes
- **Affichage** : Symboles "U" multiples

### Repoussement Impossible  
- **Bord de carte** : Élimination instantanée
- **Case occupée** : Élimination instantanée
- **Calcul** : Direction = vecteur attaquant → cible

### Fin de Partie
- **Vérification** : Après chaque tour complet
- **Message** : Affichage du gagnant pendant 5 secondes
- **Statistiques IA** : Rapport de performance affiché

---

## 📈 SYSTÈME D'ENTRAÎNEMENT IA (Développeurs)

### Métriques Collectées
- **Actions par type** : Attaque, mouvement, défense...
- **Taux de succès** : Ratio réussite/tentative par action
- **Performance globale** : Efficacité, agressivité, survie
- **Progression** : Évolution du taux de victoire

### Fichiers Générés
- **ai_stats.json** : Statistiques persistantes de l'IA
- **Rapports** : Analyse de performance en fin de partie

### Optimisation Continue
L'IA s'améliore automatiquement en :
- Privilégiant les actions avec haut taux de succès
- Explorant de nouvelles stratégies (10-20% du temps)
- Adaptant ses priorités selon les résultats passés

---

*Version 2.0 - Jeu de Stratégie Tour par Tour avec IA Adaptative*