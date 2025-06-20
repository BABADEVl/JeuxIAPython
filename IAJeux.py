import random

# Définition des couleurs
PLAYER_COLOR = "blue"
ENEMY_COLOR = "red"

# Classe pour représenter une unité
class Unit:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.hp = 10  # Points de vie
        self.attack_range = 1  # Distance d'attaque
        self.movement_range = 2  # Distance de déplacement

    def can_move(self, target_x, target_y):
        """Vérifie si l'unité peut se déplacer vers la cible."""
        distance = abs(self.x - target_x) + abs(self.y - target_y)
        return distance <= self.movement_range

    def move(self, target_x, target_y):
        """Déplace l'unité vers la cible."""
        self.x += max(-self.movement_range, min(self.movement_range, target_x - self.x))
        self.y += max(-self.movement_range, min(self.movement_range, target_y - self.y))
        print(f"{self.color} unit moved to ({self.x}, {self.y})")

    def attack(self, target, units, objectives):
        """Attaque une unité ennemie."""
        if self.can_attack(target):
            target.hp -= 5
            print(f"{self.color} unit attacked {target.color} unit at ({target.x}, {target.y}). HP left: {target.hp}")
            if target.hp <= 0:
                units.remove(target)
                print(f"{target.color} unit at ({target.x}, {target.y}) was destroyed!")

    def can_attack(self, target):
        """Vérifie si l'unité peut attaquer une cible."""
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return distance <= self.attack_range

# Fonction de logique d'IA
def ai_decision(units, objectives):
    for unit in units:
        if unit.color == ENEMY_COLOR:
            # Recherche de la cible la plus proche
            nearest_target = None
            min_distance = float('inf')
            for other_unit in units:
                if other_unit.color == PLAYER_COLOR:
                    distance = abs(unit.x - other_unit.x) + abs(unit.y - other_unit.y)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_target = other_unit
            
            # Attaque si possible
            if nearest_target and unit.can_attack(nearest_target):
                unit.attack(nearest_target, units, objectives)
                return True
            
            # Recherche de l'objectif le plus proche
            nearest_objective = None
            min_distance = float('inf')
            for obj in objectives:
                distance = abs(unit.x - obj['x']) + abs(unit.y - obj['y'])
                if distance < min_distance:
                    min_distance = distance
                    nearest_objective = obj
            
            # Déplacement vers l'objectif le plus proche
            if nearest_objective:
                target_x, target_y = nearest_objective['x'], nearest_objective['y']
                if unit.can_move(target_x, target_y):
                    unit.move(target_x, target_y)
                    return True
    
    return False

# Fonction principale
def main():
    # Initialisation des unités et des objectifs
    units = [
        Unit(0, 0, PLAYER_COLOR),
        Unit(5, 5, PLAYER_COLOR),
        Unit(10, 10, ENEMY_COLOR),
        Unit(12, 12, ENEMY_COLOR),
    ]

    objectives = [
        {'x': 3, 'y': 3, 'value': 10},
        {'x': 8, 'y': 8, 'value': 20},
    ]

    # Boucle de jeu
    turn = 0
    while units:
        print(f"\n--- Turn {turn} ---")
        # Affichage des positions
        for unit in units:
            print(f"{unit.color} unit at ({unit.x}, {unit.y}) with {unit.hp} HP")
        
        # Tour du joueur
        print("Player's turn:")
        for unit in units:
            if unit.color == PLAYER_COLOR:
                if objectives:
                    target = objectives[0]
                    if unit.can_move(target['x'], target['y']):
                        unit.move(target['x'], target['y'])
                        objectives.remove(target)
                        print(f"Player captured objective at ({target['x']}, {target['y']})!")
        
        # Tour de l'IA
        print("AI's turn:")
        ai_decision(units, objectives)
        
        # Fin de la partie si toutes les unités d'une couleur sont détruites
        player_units = [u for u in units if u.color == PLAYER_COLOR]
        enemy_units = [u for u in units if u.color == ENEMY_COLOR]
        if not player_units:
            print("AI wins!")
            break
        if not enemy_units:
            print("Player wins!")
            break
        
        turn += 1

if __name__ == "__main__":
    main()
