import pygame
from init import *

class Unit:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        self.moved = False  # Indicateur de mouvement pour le tour
        self.pv = 2  # Points de Vie
        self.attacked_this_turn = False  # Indicateur d'attaque dans ce tour

    def draw(self, screen, units, objectives, terrain_x, terrain_y):
        rect = pygame.Rect(terrain_x + self.x * tile_size, terrain_y + self.y * tile_size, tile_size, tile_size)
        if not self.moved:
            color = PLAYER_COLOR_LIGHT if self.color == PLAYER_COLOR else ENEMY_COLOR_LIGHT
        else:
            color = self.color
        pygame.draw.rect(screen, color, rect)

        if self.selected:
            pygame.draw.rect(screen, SELECTED_COLOR, rect, 3)

        font = pygame.font.SysFont(None, 16)
        symbols = self.get_symbols_on_same_tile(units)
        combined_text = font.render(symbols, True, (255, 255, 255))
        text_width = combined_text.get_width()
        text_x = terrain_x + self.x * tile_size + (tile_size - text_width) // 2
        screen.blit(combined_text, (text_x, terrain_y + self.y * tile_size + 5))

        for obj in objectives:
            if self.x == obj['x'] and self.y == obj['y']:
                pygame.draw.rect(screen, (0, 255, 0), rect, 1)

    def can_move(self, x, y, units):
        # Vérifie que la case est dans la grille et adjacente
        if 0 <= x < size and 0 <= y < size:
            if abs(self.x - x) <= 1 and abs(self.y - y) <= 1:
                # Vérifie qu'aucune unité n'occupe déjà la case
                if not any(u.x == x and u.y == y for u in units):
                    return True
        return False

    def move(self, x, y):
        self.x = x
        self.y = y
        self.moved = True

    def attack(self, target_unit, units, objectives):
        # Vérifie si la cible est adjacente
        if abs(self.x - target_unit.x) <= 1 and abs(self.y - target_unit.y) <= 1:
            dx = target_unit.x - self.x
            dy = target_unit.y - self.y
            new_x = target_unit.x + dx
            new_y = target_unit.y + dy

            case_libre = (
                0 <= new_x < size and
                0 <= new_y < size and
                not any(u.x == new_x and u.y == new_y for u in units)
            )

            if not target_unit.moved:
                # Repousse et immobilise la cible
                if case_libre:
                    target_unit.x = new_x
                    target_unit.y = new_y
                target_unit.moved = True
                target_unit.attacked_this_turn = True
            else:
                # Si déjà immobilisé, perd 1 PV et est repoussé si possible
                target_unit.pv -= 1
                target_unit.attacked_this_turn = True
                if case_libre:
                    target_unit.x = new_x
                    target_unit.y = new_y
                if target_unit.pv <= 0:
                    units.remove(target_unit)

    def get_symbols_on_same_tile(self, units):
        symbols = [u.get_symbol() for u in units if u.x == self.x and u.y == self.y]
        return ' '.join(symbols)

    def get_symbol(self):
        return "U"