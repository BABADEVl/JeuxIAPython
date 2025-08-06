import pygame
import random
from init import *
from unit import Unit  

pygame.init()
background_img = pygame.image.load("background.jpg")
background_img = pygame.transform.scale(background_img, (width, height + interface_height))

# Générer carte
def generate_map(size):
    print([[1 for _ in range(size)] for _ in range(size)])
    return [[1 for _ in range(size)] for _ in range(size)]

# Afficher carte
def draw_map(screen, game_map, tile_size):
    for y in range(size):
        for x in range(size):
            color = PASSABLE_COLOR
            pygame.draw.rect(
                screen,
                color,
                (terrain_x + x * tile_size, terrain_y + y * tile_size, tile_size, tile_size)
            )

# Générer unités 
def generate_units():
    units = []
    player_positions = [(0, i) for i in range(size)]
    enemy_positions = [(size - 1, i) for i in range(size)]

    player_positions = random.sample(player_positions, 5)
    enemy_positions = random.sample(enemy_positions, 5)

    player_units = [Unit(*pos, PLAYER_COLOR) for pos in player_positions]
    enemy_units = [Unit(*pos, ENEMY_COLOR) for pos in enemy_positions]
    
    units.extend(player_units)
    units.extend(enemy_units)
    
    return units




# Ajouter objectifs sur la map
def add_objectives():
    objectives = []
    center_x, center_y = size // 2, size // 2
    while True:
        x, y = random.randint(center_x - 3, center_x + 3), random.randint(center_y - 3, center_y + 3)
        if not any(obj['x'] == x and obj['y'] == y for obj in objectives):
            objectives.append({'x': x, 'y': y, 'type': 'MAJOR'})
            break

    for _ in range(3):
        while True:
            x, y = random.randint(center_x - 5, center_x + 5), random.randint(center_y - 5, center_y + 5)
            if not any(obj['x'] == x and obj['y'] == y for obj in objectives):
                objectives.append({'x': x, 'y': y, 'type': 'MINOR'})
                break

    return objectives

# Afficher  objectifs sur la map
def draw_objectives(screen, objectives, tile_size):
    for obj in objectives:
        color = OBJECTIVE_MAJOR_COLOR if obj['type'] == 'MAJOR' else OBJECTIVE_MINOR_COLOR
        pygame.draw.rect(
            screen,
            color,
            (terrain_x + obj['x'] * tile_size, terrain_y + obj['y'] * tile_size, tile_size, tile_size)
        )

# Calculer scores
def calculate_scores(units, objectives):
    player_score = 0
    enemy_score = 0

    for obj in objectives:
        if any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == PLAYER_COLOR for unit in units):
            player_score += 3 if obj['type'] == 'MAJOR' else 1
        elif any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == ENEMY_COLOR for unit in units):
            enemy_score += 3 if obj['type'] == 'MAJOR' else 1

    return player_score, enemy_score

# Afficher message de changement de tour
def draw_turn_indicator(screen, player_turn):
    #Affiche l'indicateur de tour
    font = pygame.font.SysFont(None, 36)
    text = "Joueur" if player_turn else "Ennemi"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 10))

# Afficher bouton changement de tour
def draw_end_turn_button(screen, width, height, interface_height):
    button_img = pygame.image.load("end_turn.png")
    button_img = pygame.transform.scale(button_img, (BUTTON_WIDTH, BUTTON_HEIGHT))

    button_rect = pygame.Rect(
        width // 2 - BUTTON_WIDTH // 2,
        terrain_y + terrain_height + 12,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    pygame.draw.rect(screen, (100, 100, 100), button_rect, border_radius=20)
    screen.blit(button_img, (button_rect.x, button_rect.y))

# Vérifier click changement de tour 
def end_turn_button_clicked(mouse_pos, width, height, interface_height):
    x, y = mouse_pos
    button_rect = pygame.Rect(
        width // 2 - BUTTON_WIDTH // 2,
        terrain_y + terrain_height + 12,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    return button_rect.collidepoint(x, y)

# Afficher infos unit
def draw_unit_attributes(screen, unit, width, height, interface_height):
    if unit:
        font = pygame.font.SysFont(None, 24)
        pv_text = f"PV: {unit.pv} / 2"
        unit_img = font.render("Unité", True, (255, 255, 255))
        pv_img = font.render(pv_text, True, (255, 255, 255))
        screen.blit(unit_img, (10, height + 10))
        screen.blit(pv_img, (10, height + 40))

# Afficher scores
def draw_scores(screen, player_score, enemy_score, width, height):
    font = pygame.font.SysFont(None, 24)
    player_score_text = f"Score Joueur: {player_score}"
    enemy_score_text = f"Score Ennemi: {enemy_score}"
    player_score_img = font.render(player_score_text, True, (255, 255, 255))
    enemy_score_img = font.render(enemy_score_text, True, (255, 255, 255))
    # À gauche du terrain
    screen.blit(player_score_img, (terrain_x - 150, terrain_y + terrain_height // 2))
    # À droite du terrain
    screen.blit(enemy_score_img, (terrain_x + terrain_width + 20, terrain_y + terrain_height // 2))

# Afficher message de victoire
def draw_victory_message(screen, message, width, height):
    font = pygame.font.SysFont(None, 48)
    victory_img = font.render(message, True, (255, 255, 255))
    screen.blit(victory_img, (width // 2 - 100, height // 2 - 24))

# Param  fenêtre
screen = pygame.display.set_mode((width, height + interface_height))
pygame.display.set_caption("Carte de 20x20 avec unités et déplacement")

# Générer map de 20 par 20
game_map = generate_map(size)

# Générer unités
units = generate_units()

# Ajouter objectifs
objectives = add_objectives()

selected_unit = None
player_turn = True  # True pour le tour du joueur, False pour le tour adverse
units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
player_score = 0
enemy_score = 0
victory = False
victory_message = ""

# Calculs pour centrer le terrain
terrain_width = tile_size * size
terrain_height = tile_size * size
terrain_x = (width - terrain_width) // 2
terrain_y = 20  # Un petit espace en haut

# Boucle principale du jeu
running = True
while running:
    if not victory:
        unit_moved = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    unit_moved = True
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if end_turn_button_clicked((x, y), width, height, interface_height):
                    unit_moved = True
                else:
                    grid_x = (x - terrain_x) // tile_size
                    grid_y = (y - terrain_y) // tile_size
                    if 0 <= grid_x < size and 0 <= grid_y < size:
                        if event.button == 1:  # Clic gauche pour sélectionner
                            possible_units = [u for u in units if u.x == grid_x and u.y == grid_y and not u.moved and u.color == (PLAYER_COLOR if player_turn else ENEMY_COLOR)]
                            if selected_unit in possible_units:
                                current_index = possible_units.index(selected_unit)
                                selected_unit.selected = False
                                selected_unit = possible_units[(current_index + 1) % len(possible_units)]
                            else:
                                if selected_unit:
                                    selected_unit.selected = False
                                if possible_units:
                                    selected_unit = possible_units[0]
                            if selected_unit:
                                selected_unit.selected = True

                        elif event.button == 3:  # Clic droit pour déplacer ou attaquer
                            if selected_unit and selected_unit.color == (PLAYER_COLOR if player_turn else ENEMY_COLOR):
                                # Si unité adverse sur la case, on attaque
                                target_unit = [u for u in units if u.x == grid_x and u.y == grid_y and u.color != selected_unit.color]
                                if target_unit:
                                    for cible in target_unit:
                                        selected_unit.attack(cible, units, objectives)
                                    # NE PAS déplacer l'unité qui attaque !
                                    selected_unit.selected = False
                                    selected_unit = None
                                # Sinon, case vide, on déplace
                                elif selected_unit.can_move(grid_x, grid_y, units):
                                    selected_unit.move(grid_x, grid_y)
                                    selected_unit.selected = False
                                    selected_unit = None

        if unit_moved:
            for unit in units_to_move:
                unit.moved = False  # Réinitialiser l'indicateur de mouvement
                unit.attacked_this_turn = False  # Réinitialiser l'indicateur d'attaque
            player_turn = not player_turn
            units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
            player_score_turn, enemy_score_turn = calculate_scores(units, objectives)
            player_score += player_score_turn
            enemy_score += enemy_score_turn

            if player_score >= 50:
                victory = True
                victory_message = "Victoire Joueur!"
            elif enemy_score >= 50:
                victory = True
                victory_message = "Victoire Ennemi!"
            elif not any(unit.color == PLAYER_COLOR for unit in units):
                victory = True
                victory_message = "Victoire Ennemi!"
            elif not any(unit.color == ENEMY_COLOR for unit in units):
                victory = True
                victory_message = "Victoire Joueur!"

            pygame.display.flip()

    screen.fill((0, 0, 0))
    screen.blit(background_img, (0, 0))
    draw_map(screen, game_map, tile_size)
    draw_objectives(screen, objectives, tile_size)
    
    # Ajoute une bordure noire autour de la zone de jeu
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        (terrain_x, terrain_y, terrain_width, terrain_height),
        1  # épaisseur de la bordure
    )
    
    for unit in units:
        unit.draw(screen, units, objectives, terrain_x, terrain_y)

    draw_turn_indicator(screen, player_turn)
    draw_end_turn_button(screen, width, height, interface_height)
    draw_unit_attributes(screen, selected_unit, width, height, interface_height)
    draw_scores(screen, player_score, enemy_score, width, height)

    if victory:
        draw_victory_message(screen, victory_message, width, height)
        pygame.display.flip()
        pygame.time.wait(5000)
        running = False

    pygame.display.flip()

pygame.quit()
