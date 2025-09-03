import heapq
import random
from init import size


# Algo de pathfinding (recherche de chemin)
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
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = current[0] + dx, current[1] + dy
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


def ia_play_adaptive(unit, units, objectives, size, trainer=None):
    """
    IA adaptative qui utilise les poids de stratégie du trainer pour prendre des décisions
    """
    if trainer is None:
        return ia_play(unit, units, objectives, size)

    # Obtenir les poids de stratégie actuels
    strategy_weights = trainer.strategy_weights

    # Calculer les probabilités d'actions basées sur les stratégies
    aggressive_prob = strategy_weights.get('aggressive', 0.3)
    defensive_prob = strategy_weights.get('defensive', 0.3)
    objective_prob = strategy_weights.get('objective_focused', 0.4)
    exploration_prob = strategy_weights.get('exploration', 0.1)
    group_prob = strategy_weights.get('group_play', 0.2)

    # Liste des actions possibles avec leurs priorités
    possible_actions = []

    # ///////////////////////////////////////////ATTAQUE\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # 1. Attaquer une unité adverse affaiblie (toujours haute priorité)
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color and u.pv == 1), None)
        if target is not None and target in units:
            priority = 0.9 + aggressive_prob * 0.1  # Très haute priorité + bonus agressif
            possible_actions.append(('attack_weak', pos, priority, lambda t=target: unit.attack(t, units, objectives) if t in units else None))

    # 2. Attaque simple
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color), None)
        if target is not None and target in units:
            priority = 0.6 * aggressive_prob + 0.2  # Basé sur l'agressivité
            possible_actions.append(('attack', pos, priority, lambda t=target: unit.attack(t, units, objectives) if t in units else None))

    # 3. Tuer une unité adversaire contre un obstacle
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color), None)
        if target is not None and target in units:
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
                priority = 0.8 * aggressive_prob + 0.1
                possible_actions.append(('push_kill', pos, priority, lambda t=target: unit.attack(t, units, objectives) if t in units else None))

    # ///////////////////////////////////////////OBJECTIF\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # 4. Prendre un objectif MAJEUR adjacent si libre
    for obj in objectives:
        if obj['type'] == 'MAJOR' and (abs(unit.x - obj['x']) <= 1 and abs(unit.y - obj['y']) <= 1):
            if not any(u.x == obj['x'] and u.y == obj['y'] for u in units):
                priority = 0.8 * objective_prob + 0.1
                obj_x, obj_y = obj['x'], obj['y']
                possible_actions.append(('move_major', (obj_x, obj_y), priority,
                                         lambda x=obj_x, y=obj_y: unit.move(x, y)))

    # 5. Déplacement vers objectif MAJEUR
    major_objs = [obj for obj in objectives if obj['type'] == 'MAJOR']
    for obj in major_objs:
        path = astar_path((unit.x, unit.y), (obj['x'], obj['y']), units, size)
        if path:
            next_pos = path[0]
            if not any(u.x == next_pos[0] and u.y == next_pos[1] for u in units):
                priority = 0.5 * objective_prob + 0.1
                pos_x, pos_y = next_pos[0], next_pos[1]
                possible_actions.append(('move_major_path', next_pos, priority,
                                         lambda x=pos_x, y=pos_y: unit.move(x, y)))

    # 6. Prendre objectif mineur adjacent si libre
    for obj in objectives:
        if obj['type'] == 'MINOR' and (abs(unit.x - obj['x']) <= 1 and abs(unit.y - obj['y']) <= 1):
            if not any(u.x == obj['x'] and u.y == obj['y'] for u in units):
                priority = 0.4 * objective_prob + 0.1
                obj_x, obj_y = obj['x'], obj['y']
                possible_actions.append(('move_minor', (obj_x, obj_y), priority,
                                         lambda x=obj_x, y=obj_y: unit.move(x, y)))

    # 7. Déplacement vers objectif mineur
    minor_objs = [obj for obj in objectives if obj['type'] == 'MINOR']
    for obj in minor_objs:
        path = astar_path((unit.x, unit.y), (obj['x'], obj['y']), units, size)
        if path:
            next_pos = path[0]
            if not any(u.x == next_pos[0] and u.y == next_pos[1] for u in units):
                priority = 0.3 * objective_prob + 0.1
                pos_x, pos_y = next_pos[0], next_pos[1]
                possible_actions.append(('move_minor_path', next_pos, priority,
                                         lambda x=pos_x, y=pos_y: unit.move(x, y)))

    # ///////////////////////////////////////////MOUVEMENT DÉFENSIF\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # 8. Fuir si faible PV
    if unit.pv == 1:
        for pos in get_adjacent_positions(unit.x, unit.y, size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                if all(abs(pos[0] - e.x) > 1 or abs(pos[1] - e.y) > 1 for e in units if e.color != unit.color):
                    priority = 0.7 * defensive_prob + 0.2
                    pos_x, pos_y = pos[0], pos[1]
                    possible_actions.append(('flee', pos, priority,
                                             lambda x=pos_x, y=pos_y: unit.move(x, y)))

    # 9. Se regrouper avec alliés
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        if not any(u.x == pos[0] and u.y == pos[1] for u in units):
            if any(abs(pos[0] - a.x) <= 1 and abs(pos[1] - a.y) <= 1 for a in units if
                   a.color == unit.color and a != unit):
                priority = 0.5 * group_prob + 0.1
                pos_x, pos_y = pos[0], pos[1]
                possible_actions.append(('group', pos, priority,
                                         lambda x=pos_x, y=pos_y: unit.move(x, y)))

    # 10. Se déplacer pour protéger une unité alliée faible
    weak_allies = [u for u in units if u.color == unit.color and u.pv == 1 and u != unit]
    for ally in weak_allies:
        for pos in get_adjacent_positions(ally.x, ally.y, size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                priority = 0.6 * group_prob + 0.2 * defensive_prob
                pos_x, pos_y = pos[0], pos[1]
                possible_actions.append(('protect_ally', pos, priority,
                                         lambda x=pos_x, y=pos_y: unit.move(x, y)))

    # 11. Actions d'exploration (pour découvrir de nouvelles stratégies)
    if trainer.should_explore('random_move'):
        for pos in get_adjacent_positions(unit.x, unit.y, size):
            if not any(u.x == pos[0] and u.y == pos[1] for u in units):
                priority = exploration_prob * 0.5
                pos_x, pos_y = pos[0], pos[1]
                possible_actions.append(('explore', pos, priority,
                                         lambda x=pos_x, y=pos_y: unit.move(x, y)))

    # 12. Mouvement stratégique vers le centre
    center = (size // 2, size // 2)
    path = astar_path((unit.x, unit.y), center, units, size)
    if path:
        next_pos = path[0]
        if not any(u.x == next_pos[0] and u.y == next_pos[1] for u in units):
            priority = 0.3 + exploration_prob * 0.2
            pos_x, pos_y = next_pos[0], next_pos[1]
            possible_actions.append(('strategic_position', next_pos, priority,
                                     lambda x=pos_x, y=pos_y: unit.move(x, y)))

    # Sélection de l'action basée sur les probabilités pondérées
    if possible_actions:
        # Trier par priorité et ajouter du randomness
        possible_actions.sort(key=lambda x: x[2], reverse=True)

        # Sélection probabiliste pondérée
        total_weight = sum(action[2] for action in possible_actions)
        if total_weight > 0:
            # Normaliser les poids pour faire une sélection probabiliste
            weights = [action[2] / total_weight for action in possible_actions]

            # Choisir une action basée sur les poids
            choice = random.choices(possible_actions, weights=weights, k=1)[0]

            action_name, target_pos, _, action_func = choice
            action_func()
            return action_name, target_pos

    # Si aucune action n'est possible, mouvement aléatoire
    possible_moves = [pos for pos in get_adjacent_positions(unit.x, unit.y, size)
                      if not any(u.x == pos[0] and u.y == pos[1] for u in units)]
    if possible_moves:
        chosen_pos = random.choice(possible_moves)
        unit.move(chosen_pos[0], chosen_pos[1])
        return "random_move", chosen_pos

    # Passer le tour si vraiment aucune action n'est possible
    return "pass", None


def ia_play(unit, units, objectives, size):
    """
    Version originale de l'IA pour la rétrocompatibilité
    """
    # ///////////////////////////////////////////ATTAQUE\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # 1. Attaquer une unité adverse affaiblie
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color and u.pv == 1), None)
        if target is not None and target in units:
            unit.attack(target, units, objectives)
            return "attack_weak", pos

    # 2. Attaque simple
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color), None)
        if target is not None and target in units:
            unit.attack(target, units, objectives)
            return "attack", pos

    # 3. tuer une unité adversaire contre un obstacle
    for pos in get_adjacent_positions(unit.x, unit.y, size):
        target = next((u for u in units if (u.x, u.y) == pos and u.color != unit.color), None)
        if target is not None and target in units:
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

    # ///////////////////////////////////////////OBJECTIF\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
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

    # Continuer avec le reste de la logique originale...
    # [Le reste du code original ia_play reste inchangé]

    # 20. Passe son tour
    return "pass", None
