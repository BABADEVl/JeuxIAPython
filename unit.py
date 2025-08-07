import pygame
from init import *

class Unit:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        self.moved = False
        self.pv = 2
        self.attacked_this_turn = False

    def draw(self, screen, units, objectives, terrain_x, terrain_y):
        rect = pygame.Rect(
            terrain_x + self.x * tile_size,
            terrain_y + self.y * tile_size,
            tile_size,
            tile_size
        )
        color = PLAYER_COLOR_LIGHT if self.color == PLAYER_COLOR and not self.moved else ENEMY_COLOR_LIGHT if self.color == ENEMY_COLOR and not self.moved else self.color
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
        if 0 <= x < size and 0 <= y < size and abs(self.x - x) <= 1 and abs(self.y - y) <= 1:
            if not any(u.x == x and u.y == y for u in units):
                return True
        return False

    def move(self, x, y):
        self.x = x
        self.y = y
        self.moved = True

    def attack(self, target_unit, units, objectives):
        if abs(self.x - target_unit.x) <= 1 and abs(self.y - target_unit.y) <= 1:
            dx = target_unit.x - self.x
            dy = target_unit.y - self.y
            new_x = target_unit.x + dx
            new_y = target_unit.y + dy

            # Vérifie si la case de repoussement est un obstacle
            obstacle = (
                new_x < 0 or new_x >= size or
                new_y < 0 or new_y >= size or
                any(u.x == new_x and u.y == new_y for u in units)
            )

            if not target_unit.moved:
                if obstacle:
                    # Tué instantanément
                    if target_unit in units:
                        units.remove(target_unit)
                else:
                    target_unit.x = new_x
                    target_unit.y = new_y
                    target_unit.moved = True
                    target_unit.attacked_this_turn = True
            else:
                target_unit.pv -= 1
                target_unit.attacked_this_turn = True
                if obstacle:
                    if target_unit in units:
                        units.remove(target_unit)
                else:
                    target_unit.x = new_x
                    target_unit.y = new_y
                if target_unit.pv <= 0 and target_unit in units:
                    units.remove(target_unit)
        self.moved = True

    def get_symbols_on_same_tile(self, units):
        symbols = [u.get_symbol() for u in units if u.x == self.x and u.y == self.y]
        return ' '.join(symbols)

    def get_symbol(self):
        return "U"