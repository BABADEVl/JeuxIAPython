import pygame
import random
import math
from init import *
from unit import *


def generate_map(size):
    return [[1 for _ in range(size)] for _ in range(size)]


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


def draw_map(screen, game_map, tile_size, terrain_x, terrain_y):
    """Dessiner la grille avec un effet de damier subtil"""
    for y in range(size):
        for x in range(size):
            # Effet damier subtil
            if (x + y) % 2 == 0:
                color = PASSABLE_COLOR
            else:
                color = (190, 190, 190)  # Légèrement plus sombre

            rect = pygame.Rect(
                terrain_x + x * tile_size,
                terrain_y + y * tile_size,
                tile_size,
                tile_size
            )
            pygame.draw.rect(screen, color, rect)

            # Bordure fine pour chaque case
            pygame.draw.rect(screen, (160, 160, 160), rect, 1)


def draw_objectives(screen, objectives, tile_size, terrain_x, terrain_y):
    """Dessiner les objectifs avec des effets visuels améliorés"""
    for obj in objectives:
        x_pos = terrain_x + obj['x'] * tile_size
        y_pos = terrain_y + obj['y'] * tile_size

        if obj['type'] == 'MAJOR':
            # Objectif majeur avec effet de brillance
            color = OBJECTIVE_MAJOR_COLOR
            # Effet de pulsation
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
            bright_color = tuple(min(255, int(c * pulse)) for c in color)

            # Dessiner un losange pour l'objectif majeur
            center_x = x_pos + tile_size // 2
            center_y = y_pos + tile_size // 2
            diamond_size = tile_size // 3
            diamond_points = [
                (center_x, center_y - diamond_size),  # Haut
                (center_x + diamond_size, center_y),  # Droite
                (center_x, center_y + diamond_size),  # Bas
                (center_x - diamond_size, center_y)  # Gauche
            ]
            pygame.draw.polygon(screen, bright_color, diamond_points)
            pygame.draw.polygon(screen, (200, 200, 0), diamond_points, 2)
        else:
            # Objectif mineur
            color = OBJECTIVE_MINOR_COLOR
            center_x = x_pos + tile_size // 2
            center_y = y_pos + tile_size // 2
            circle_radius = tile_size // 4

            pygame.draw.circle(screen, color, (center_x, center_y), circle_radius)
            pygame.draw.circle(screen, (180, 150, 0), (center_x, center_y), circle_radius, 2)


def calculate_scores(units, objectives):
    player_score = 0
    enemy_score = 0
    for obj in objectives:
        if any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == PLAYER_COLOR for unit in units):
            player_score += 3 if obj['type'] == 'MAJOR' else 1
        elif any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == ENEMY_COLOR for unit in units):
            enemy_score += 3 if obj['type'] == 'MAJOR' else 1
    return player_score, enemy_score


def draw_turn_indicator(screen, player_turn):
    """Indicateur de tour amélioré avec fond coloré"""
    font = pygame.font.SysFont(None, 36)
    text = "Tour Joueur" if player_turn else "Tour IA"

    # Couleur de fond selon le joueur
    bg_color = (0, 100, 200) if player_turn else (200, 100, 0)
    text_color = (255, 255, 255)

    # Créer le texte
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()

    # Fond coloré avec bordures arrondies
    bg_rect = pygame.Rect(10, 10, text_rect.width + 20, text_rect.height + 10)
    pygame.draw.rect(screen, bg_color, bg_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2, border_radius=10)

    # Afficher le texte centré
    screen.blit(text_surface, (bg_rect.x + 10, bg_rect.y + 5))


def draw_end_turn_button(screen, width, height, interface_height, terrain_x, terrain_y, terrain_width, terrain_height,
                         BUTTON_WIDTH, BUTTON_HEIGHT):
    """Bouton fin de tour avec effets de survol"""
    button_rect = pygame.Rect(
        width // 2 - BUTTON_WIDTH // 2,
        terrain_y + terrain_height + 12,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    # Vérifier si la souris survole le bouton
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = button_rect.collidepoint(mouse_pos)

    # Couleurs selon l'état
    button_color = (150, 150, 150) if is_hovered else (100, 100, 100)
    border_color = (200, 200, 200) if is_hovered else (150, 150, 150)

    # Dessiner le bouton
    pygame.draw.rect(screen, button_color, button_rect, border_radius=15)
    pygame.draw.rect(screen, border_color, button_rect, 3, border_radius=15)

    # Charger et afficher l'image si elle existe
    try:
        button_img = pygame.image.load("assets/end_turn.png")
        button_img = pygame.transform.scale(button_img, (BUTTON_WIDTH - 10, BUTTON_HEIGHT - 10))
        screen.blit(button_img, (button_rect.x + 5, button_rect.y + 5))
    except:
        # Si pas d'image, afficher du texte
        font = pygame.font.SysFont(None, 24)
        text = font.render("Fin de Tour", True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)


def end_turn_button_clicked(mouse_pos, width, height, interface_height, terrain_x, terrain_y, terrain_width,
                            terrain_height, BUTTON_WIDTH, BUTTON_HEIGHT):
    x, y = mouse_pos
    button_rect = pygame.Rect(
        width // 2 - BUTTON_WIDTH // 2,
        terrain_y + terrain_height + 12,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    return button_rect.collidepoint(x, y)


def draw_unit_attributes(screen, unit, width, height, interface_height):
    """Interface d'informations d'unité améliorée"""
    if unit:
        # Fond pour les informations d'unité
        info_rect = pygame.Rect(10, height + 10, 200, 80)
        pygame.draw.rect(screen, (50, 50, 50), info_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 150), info_rect, 2, border_radius=10)

        font_title = pygame.font.SysFont(None, 28)
        font_info = pygame.font.SysFont(None, 24)

        # Titre selon la couleur de l'unité
        unit_type = "Unité Joueur" if unit.color == PLAYER_COLOR else "Unité IA"
        title_color = PLAYER_COLOR if unit.color == PLAYER_COLOR else ENEMY_COLOR

        unit_img = font_title.render(unit_type, True, title_color)
        screen.blit(unit_img, (info_rect.x + 10, info_rect.y + 5))

        # Informations PV avec barre visuelle
        pv_text = f"PV: {unit.pv} / 2"
        pv_img = font_info.render(pv_text, True, (255, 255, 255))
        screen.blit(pv_img, (info_rect.x + 10, info_rect.y + 30))

        # Barre de PV
        bar_width = 100
        bar_height = 8
        bar_x = info_rect.x + 10
        bar_y = info_rect.y + 55

        # Fond de la barre
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Barre de PV actuelle
        pv_ratio = unit.pv / 2
        current_width = int(bar_width * pv_ratio)
        bar_color = (0, 200, 0) if unit.pv == 2 else (200, 200, 0) if unit.pv == 1 else (200, 0, 0)
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, current_width, bar_height))

        # Bordure de la barre
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

        # Statut de mouvement
        if unit.moved:
            status_text = "A bougé"
            status_color = (200, 200, 0)
        else:
            status_text = "Peut bouger"
            status_color = (0, 200, 0)

        status_img = font_info.render(status_text, True, status_color)
        screen.blit(status_img, (info_rect.x + 110, info_rect.y + 45))


def draw_scores(screen, player_score, enemy_score, width, height, terrain_x, terrain_y, terrain_width, terrain_height):
    """Affichage des scores amélioré"""
    font_title = pygame.font.SysFont(None, 28)
    font_score = pygame.font.SysFont(None, 32)

    # Score joueur (gauche)
    player_title = font_title.render("JOUEUR", True, PLAYER_COLOR)
    player_score_text = f"{player_score}"
    player_score_img = font_score.render(player_score_text, True, PLAYER_COLOR)

    # Fond pour le score joueur
    player_bg = pygame.Rect(terrain_x - 160, terrain_y + terrain_height // 2 - 40, 140, 80)
    pygame.draw.rect(screen, (30, 30, 60), player_bg, border_radius=10)
    pygame.draw.rect(screen, PLAYER_COLOR, player_bg, 2, border_radius=10)

    screen.blit(player_title, (player_bg.x + 10, player_bg.y + 5))
    screen.blit(player_score_img, (player_bg.x + 10, player_bg.y + 30))

    # Barre de progression vers la victoire (50 points)
    progress_width = 120
    progress_height = 6
    progress_x = player_bg.x + 10
    progress_y = player_bg.y + 60

    pygame.draw.rect(screen, (100, 100, 100), (progress_x, progress_y, progress_width, progress_height))
    player_progress = min(progress_width, int((player_score / 50) * progress_width))
    pygame.draw.rect(screen, PLAYER_COLOR, (progress_x, progress_y, player_progress, progress_height))

    # Score ennemi (droite)
    enemy_title = font_title.render("IA", True, ENEMY_COLOR)
    enemy_score_text = f"{enemy_score}"
    enemy_score_img = font_score.render(enemy_score_text, True, ENEMY_COLOR)

    # Fond pour le score ennemi
    enemy_bg = pygame.Rect(terrain_x + terrain_width + 20, terrain_y + terrain_height // 2 - 40, 140, 80)
    pygame.draw.rect(screen, (60, 30, 30), enemy_bg, border_radius=10)
    pygame.draw.rect(screen, ENEMY_COLOR, enemy_bg, 2, border_radius=10)

    screen.blit(enemy_title, (enemy_bg.x + 10, enemy_bg.y + 5))
    screen.blit(enemy_score_img, (enemy_bg.x + 10, enemy_bg.y + 30))

    # Barre de progression ennemi
    enemy_progress = min(progress_width, int((enemy_score / 50) * progress_width))
    pygame.draw.rect(screen, (100, 100, 100), (enemy_bg.x + 10, progress_y, progress_width, progress_height))
    pygame.draw.rect(screen, ENEMY_COLOR, (enemy_bg.x + 10, progress_y, enemy_progress, progress_height))


def draw_victory_message(screen, message, width, height):
    """Message de victoire amélioré avec effets"""
    # Fond semi-transparent
    overlay = pygame.Surface((width, height + 200))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Texte principal
    font_big = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)

    # Couleur selon le gagnant
    if "Joueur" in message:
        text_color = PLAYER_COLOR
        bg_color = (0, 50, 150)
    else:
        text_color = ENEMY_COLOR
        bg_color = (150, 50, 0)

    victory_img = font_big.render(message, True, text_color)
    victory_rect = victory_img.get_rect(center=(width // 2, height // 2 - 50))

    # Fond du message
    bg_rect = pygame.Rect(victory_rect.x - 30, victory_rect.y - 20,
                          victory_rect.width + 60, victory_rect.height + 100)
    pygame.draw.rect(screen, bg_color, bg_rect, border_radius=20)
    pygame.draw.rect(screen, text_color, bg_rect, 4, border_radius=20)

    screen.blit(victory_img, victory_rect)

    # Instruction
    instruction = font_small.render("Le jeu se fermera dans 5 secondes...", True, (255, 255, 255))
    instruction_rect = instruction.get_rect(center=(width // 2, height // 2 + 30))
    screen.blit(instruction, instruction_rect)


def draw_grid_coordinates(screen, terrain_x, terrain_y, tile_size):
    """Afficher les coordonnées de la grille (optionnel, pour debug)"""
    font = pygame.font.SysFont(None, 16)

    # Coordonnées X (en haut)
    for x in range(size):
        if x % 5 == 0:  # Afficher seulement tous les 5
            coord_text = font.render(str(x), True, (100, 100, 100))
            screen.blit(coord_text, (terrain_x + x * tile_size + tile_size // 2 - 4, terrain_y - 20))

    # Coordonnées Y (à gauche)
    for y in range(size):
        if y % 5 == 0:  # Afficher seulement tous les 5
            coord_text = font.render(str(y), True, (100, 100, 100))
            screen.blit(coord_text, (terrain_x - 20, terrain_y + y * tile_size + tile_size // 2 - 6))


def draw_game_info(screen, width, height, turn_count=0):
    """Informations générales du jeu"""
    font = pygame.font.SysFont(None, 20)

    # Objectif du jeu
    info_text = "Objectif: 50 points pour gagner | Clic gauche: sélectionner | Clic droit: déplacer/attaquer"
    text_surface = font.render(info_text, True, (200, 200, 200))
    text_rect = text_surface.get_rect(center=(width // 2, height + 150))
    screen.blit(text_surface, text_rect)

    # Légende des couleurs
    legend_y = height + 170
    legend_items = [
        ("Objectif Majeur (3 pts)", OBJECTIVE_MAJOR_COLOR),
        ("Objectif Mineur (1 pt)", OBJECTIVE_MINOR_COLOR),
        ("Unité sélectionnée", SELECTED_COLOR)
    ]

    x_offset = width // 2 - 200
    for i, (text, color) in enumerate(legend_items):
        # Petit carré de couleur
        color_rect = pygame.Rect(x_offset + i * 140, legend_y, 15, 15)
        pygame.draw.rect(screen, color, color_rect)
        pygame.draw.rect(screen, (255, 255, 255), color_rect, 1)

        # Texte explicatif
        legend_text = font.render(text, True, (180, 180, 180))
        screen.blit(legend_text, (x_offset + i * 140 + 20, legend_y - 2))

