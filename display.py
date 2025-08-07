import pygame
import random
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
    for y in range(size):
        for x in range(size):
            color = PASSABLE_COLOR
            pygame.draw.rect(
                screen,
                color,
                (terrain_x + x * tile_size, terrain_y + y * tile_size, tile_size, tile_size)
            )

def draw_objectives(screen, objectives, tile_size, terrain_x, terrain_y):
    for obj in objectives:
        color = OBJECTIVE_MAJOR_COLOR if obj['type'] == 'MAJOR' else OBJECTIVE_MINOR_COLOR
        pygame.draw.rect(
            screen,
            color,
            (terrain_x + obj['x'] * tile_size, terrain_y + obj['y'] * tile_size, tile_size, tile_size)
        )

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
    font = pygame.font.SysFont(None, 36)
    text = "Joueur" if player_turn else "Ennemi"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 10))

def draw_end_turn_button(screen, width, height, interface_height, terrain_x, terrain_y, terrain_width, terrain_height, BUTTON_WIDTH, BUTTON_HEIGHT):
    button_img = pygame.image.load("assets/end_turn.png")
    button_img = pygame.transform.scale(button_img, (BUTTON_WIDTH, BUTTON_HEIGHT))
    button_rect = pygame.Rect(
        width // 2 - BUTTON_WIDTH // 2,
        terrain_y + terrain_height + 12,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    pygame.draw.rect(screen, (100, 100, 100), button_rect, border_radius=20)
    screen.blit(button_img, (button_rect.x, button_rect.y))

def end_turn_button_clicked(mouse_pos, width, height, interface_height, terrain_x, terrain_y, terrain_width, terrain_height, BUTTON_WIDTH, BUTTON_HEIGHT):
    x, y = mouse_pos
    button_rect = pygame.Rect(
        width // 2 - BUTTON_WIDTH // 2,
        terrain_y + terrain_height + 12,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )
    return button_rect.collidepoint(x, y)

def draw_unit_attributes(screen, unit, width, height, interface_height):
    if unit:
        font = pygame.font.SysFont(None, 24)
        pv_text = f"PV: {unit.pv} / 2"
        unit_img = font.render("Unité", True, (255, 255, 255))
        pv_img = font.render(pv_text, True, (255, 255, 255))
        screen.blit(unit_img, (10, height + 10))
        screen.blit(pv_img, (10, height + 40))

def draw_scores(screen, player_score, enemy_score, width, height, terrain_x, terrain_y, terrain_width, terrain_height):
    font = pygame.font.SysFont(None, 24)
    player_score_text = f"Score Joueur: {player_score}"
    enemy_score_text = f"Score Ennemi: {enemy_score}"
    player_score_img = font.render(player_score_text, True, (255, 255, 255))
    enemy_score_img = font.render(enemy_score_text, True, (255, 255, 255))
    screen.blit(player_score_img, (terrain_x - 150, terrain_y + terrain_height // 2))
    screen.blit(enemy_score_img, (terrain_x + terrain_width + 20, terrain_y + terrain_height // 2))

def draw_victory_message(screen, message, width, height):
    font = pygame.font.SysFont(None, 48)
    victory_img = font.render(message, True, (255, 255, 255))
    screen.blit(victory_img, (width // 2 - 100, height // 2 - 24))