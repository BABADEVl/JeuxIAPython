import heapq
from init import size

#Algo de pathfinding (recherche de chemin)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_path(start, goal, units, size):
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start, []))
    closed_set = set()
    occupied = {(u.x, u.y) for u in units if (u.x, u.y) != goal}
    while open_set:
        _, cost, current, path = heapq.heappop(open_set)
        if current == goal:
            return path
        if current in closed_set:
            continue
        closed_set.add(current)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = current[0]+dx, current[1]+dy
            next_pos = (nx, ny)
            if 0 <= nx < size and 0 <= ny < size and next_pos not in closed_set and next_pos not in occupied:
                heapq.heappush(open_set, (cost + 1 + heuristic(next_pos, goal), cost + 1, next_pos, path + [next_pos]))
    return []

def get_adjacent_positions(x, y, size):
    return [
        (x + dx, y + dy)
        for dx in [-1, 0, 1]
        for dy in [-1, 0, 1]
        if not (dx == 0 and dy == 0)
        if 0 <= x + dx < size and 0 <= y + dy < size
    ]

def ia_play(unit, units, objectives, size):
#///////////////////////////////////////////ATTAQUE\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # 1. Attaquer une unité adverse affaiblie 
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color and u.pv == 1), None)
        if target:
            unit.attack(target, units, objectives)
            return "attack_weak", pos
    
    # 2. Attaque simple
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color), None)
        if target:
            unit.attack(target, units, objectives)
            return "attack", pos

    # 3. tuer une unité adversaire contre un obstacle 
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color), None)
        if target:
            dx = target.x - unit.x
            dy = target.y - unit.y
            new_x = target.x + dx
            new_y = target.y + dy
            obstacle = (
                new_x < 0 or new_x >= size or
                new_y < 0 or new_y >= size or
                any(u.x == new_x and u.y == new_y for u in units)
            )
            if obstacle:
                unit.attack(target, units, objectives)
                return "push_kill", pos
            
#///////////////////////////////////////////OBJECTIF\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # 4. Prendre un objectif MAJEUR adjacent si libre
    for obj in objectives:
        if obj['type'] == 'MAJOR' and (abs(unit.x - obj['x']) <= 1 and abs(unit.y - obj['y']) <= 1):
            if not any(u.x == obj['x'] and u.y == obj['y'] for u in units):
                unit.move(obj['x'], obj['y'])
                return "move_major", (obj['x'], obj['y'])

    # 5. Déplacement vers objectif MAJEUR (astar_path)
    major_objs = [obj for obj in objectives if obj['type'] == 'MAJOR']
    for obj in major_objs:
        path = astar_path((unit.x, unit.y), (obj['x'], obj['y']), units, size)
        if path:
            next_pos = path[0]
            if not any(u.x == next_pos[0] and u.y == next_pos[1] for u in units):
                unit.move(next_pos[0], next_pos[1])
                return "move_major_path", next_pos
            
    # 6. Prendre objectif mineur adjacent si libre
    for obj in objectives:
        if obj['type'] == 'MINOR' and (abs(unit.x - obj['x']) <= 1 and abs(unit.y - obj['y']) <= 1):
            if not any(u.x == obj['x'] and u.y == obj['y'] for u in units):
                unit.move(obj['x'], obj['y'])
                return "move_minor", (obj['x'], obj['y'])
            
    # 7. Déplacement vers objectif mineur (astar_path)
    minor_objs = [obj for obj in objectives if obj['type'] == 'MINOR']
    for obj in minor_objs:
        path = astar_path((unit.x, unit.y), (obj['x'], obj['y']), units, size)
        if path:
            next_pos = path[0]
            if not any(u.x == next_pos[0] and u.y == next_pos[1] for u in units):
                unit.move(next_pos[0], next_pos[1])
                return "move_minor_path", next_pos
    
    # 8. Bloquer un adversaire qui va vers un objectif
    for obj in objectives:
        for enemy in [u for u in units if u.color != unit.color]:
            path = astar_path((enemy.x, enemy.y), (obj['x'], obj['y']), units, size)
            if path and len(path) == 1:  # L'ennemi peut atteindre l'objectif au prochain tour
                for pos in get_adjacent_positions(obj['x'], obj['y'], size):
                    if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                        unit.move(pos[0], pos[1])
                        return "block_enemy", pos

    # 9. Se déplacer pour protéger un objectif
    for obj in objectives:
        for pos in get_adjacent_positions(obj['x'], obj['y'], size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                unit.move(pos[0], pos[1])
                return "protect_objective", pos
            
#///////////////////////////////////////////MOUVEMENT\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # 10. Fuir si faible PV
    if unit.pv == 1:
        for pos in get_adjacent_positions(unit.x, unit.y, size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                # S'éloigner des ennemis
                if all(abs(pos[0] - e.x) > 1 or abs(pos[1] - e.y) > 1 for e in units if e.color != unit.color):
                    unit.move(pos[0], pos[1])
                    return "flee", pos

    # 11. Se regrouper avec alliés
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        if not any(u.x == pos[0] and u.y == pos[1] for u in units):
            if any(abs(pos[0] - a.x) <= 1 and abs(pos[1] - a.y) <= 1 for a in units if a.color == unit.color and a != unit):
                unit.move(pos[0], pos[1])
                return "group", pos

    # 12. Se déplacer pour protéger une unité alliée faible
    weak_allies = [u for u in units if u.color == unit.color and u.pv == 1 and u != unit]
    for ally in weak_allies:
        for pos in get_adjacent_positions(ally.x, ally.y, size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                unit.move(pos[0], pos[1])
                return "protect_ally", pos

    # 13. Se déplacer pour encercler un adversaire
    for enemy in [u for u in units if u.color != unit.color]:
        for pos in get_adjacent_positions(enemy.x, enemy.y, size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                unit.move(pos[0], pos[1])
                return "encircle_enemy", pos

    # 14. Se déplacer pour préparer une attaque combinée
    for enemy in [u for u in units if u.color != unit.color]:
        for pos in get_adjacent_positions(enemy.x, enemy.y, size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                # Vérifie si un allié est déjà adjacent à l'ennemi
                if any(abs(pos[0] - a.x) <= 1 and abs(pos[1] - a.y) <= 1 for a in units if a.color == unit.color and a != unit):
                    unit.move(pos[0], pos[1])
                    return "prepare_combo_attack", pos

    # 15. Se déplacer pour occuper une position stratégique (centre de la map)
    center = (size // 2, size // 2)
    path = astar_path((unit.x, unit.y), center, units, size)
    if path:
        next_pos = path[0]
        if not any(u.x == next_pos[0] and u.y == next_pos[1] for u in units):
            unit.move(next_pos[0], next_pos[1])
            return "strategic_position", next_pos

    # 16. Se déplacer pour fuir une zone dangereuse (plusieurs ennemis proches)
    danger = sum(1 for e in units if e.color != unit.color and abs(unit.x - e.x) <= 2 and abs(unit.y - e.y) <= 2)
    if danger >= 2:
        safe_positions = [pos for pos in get_adjacent_positions(unit.x, unit.y, size)
                          if not any(u.x == pos[0] and u.y == pos[1] for u in units)]
        if safe_positions:
            # Choisir la position la plus éloignée des ennemis
            farthest = max(safe_positions, key=lambda p: min(abs(p[0] - e.x) + abs(p[1] - e.y) for e in units if e.color != unit.color))
            unit.move(farthest[0], farthest[1])
            return "flee_danger_zone", farthest

    # 17. Se déplacer pour maximiser la distance avec les ennemis (pour unité faible)
    if unit.pv == 1:
        safe_positions = [pos for pos in get_adjacent_positions(unit.x, unit.y, size)
                          if not any(u.x == pos[0] and u.y == pos[1] for u in units)]
        if safe_positions:
            farthest = max(safe_positions, key=lambda p: min(abs(p[0] - e.x) + abs(p[1] - e.y) for e in units if e.color != unit.color))
            unit.move(farthest[0], farthest[1])
            return "max_distance_enemy", farthest

    # 18. Se déplacer pour rejoindre un groupe d’alliés
    ally_positions = [(a.x, a.y) for a in units if a.color == unit.color and a != unit]
    if ally_positions:
        path = astar_path((unit.x, unit.y), ally_positions[0], units, size)
        if path:
            next_pos = path[0]
            if not any(u.x == next_pos[0] and u.y == next_pos[1] for u in units):
                unit.move(next_pos[0], next_pos[1])
                return "join_group", next_pos

    # 19. Se déplacer pour préparer une prise d’objectif au prochain tour
    for obj in objectives:
        for pos in get_adjacent_positions(obj['x'], obj['y'], size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                unit.move(pos[0], pos[1])
                return "prepare_objective", pos

    # 20. Passe son tour
    return "pass", None

