import pygame
import os
from init import *


class Unit:
    # Cache des sprites pour éviter de recharger les images à chaque fois
    _sprite_cache = {}

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        self.moved = False
        self.pv = 2
        self.attacked_this_turn = False

        # Charger les sprites si disponibles
        self._load_sprites()

    def _load_sprites(self):
        """Charge les sprites des unités depuis les assets"""
        if not Unit._sprite_cache:  # Charger une seule fois
            try:
                # Sprites pour unité joueur
                player_sprite_path = "assets/player_unit.png"
                player_sprite_weak_path = "assets/player_unit_weak.png"

                # Sprites pour unité ennemie
                enemy_sprite_path = "assets/enemy_unit.png"
                enemy_sprite_weak_path = "assets/enemy_unit_weak.png"

                if os.path.exists(player_sprite_path):
                    Unit._sprite_cache['player'] = pygame.transform.scale(
                        pygame.image.load(player_sprite_path), (tile_size, tile_size)
                    )

                if os.path.exists(player_sprite_weak_path):
                    Unit._sprite_cache['player_weak'] = pygame.transform.scale(
                        pygame.image.load(player_sprite_weak_path), (tile_size, tile_size)
                    )

                if os.path.exists(enemy_sprite_path):
                    Unit._sprite_cache['enemy'] = pygame.transform.scale(
                        pygame.image.load(enemy_sprite_path), (tile_size, tile_size)
                    )

                if os.path.exists(enemy_sprite_weak_path):
                    Unit._sprite_cache['enemy_weak'] = pygame.transform.scale(
                        pygame.image.load(enemy_sprite_weak_path), (tile_size, tile_size)
                    )

            except pygame.error as e:
                print(f"Erreur lors du chargement des sprites: {e}")
                # Les sprites ne seront pas utilisés, on utilisera les couleurs par défaut

    def draw(self, screen, units, objectives, terrain_x, terrain_y):
        rect = pygame.Rect(
            terrain_x + self.x * tile_size,
            terrain_y + self.y * tile_size,
            tile_size,
            tile_size
        )

        # Déterminer la couleur ou le sprite à utiliser
        sprite_key = None
        color = None

        if self.color == PLAYER_COLOR:
            if self.pv == 1 and 'player_weak' in Unit._sprite_cache:
                sprite_key = 'player_weak'
            elif 'player' in Unit._sprite_cache:
                sprite_key = 'player'
            else:
                color = PLAYER_COLOR_LIGHT if not self.moved else PLAYER_COLOR
        else:  # ENEMY_COLOR
            if self.pv == 1 and 'enemy_weak' in Unit._sprite_cache:
                sprite_key = 'enemy_weak'
            elif 'enemy' in Unit._sprite_cache:
                sprite_key = 'enemy'
            else:
                color = ENEMY_COLOR_LIGHT if not self.moved else ENEMY_COLOR

        # Dessiner le sprite ou la couleur
        if sprite_key:
            # Dessiner d'abord un fond coloré si l'unité n'a pas bougé
            if not self.moved:
                bg_color = PLAYER_COLOR_LIGHT if self.color == PLAYER_COLOR else ENEMY_COLOR_LIGHT
                pygame.draw.rect(screen, bg_color, rect)

            # Dessiner le sprite par dessus
            screen.blit(Unit._sprite_cache[sprite_key], rect)
        else:
            # Utiliser les couleurs par défaut si pas de sprite
            pygame.draw.rect(screen, color, rect)

        # Bordure de sélection
        if self.selected:
            pygame.draw.rect(screen, SELECTED_COLOR, rect, 3)

        # Afficher les symboles texte (pour compatibilité)
        font = pygame.font.SysFont(None, 16)
        symbols = self.get_symbols_on_same_tile(units)
        if symbols.strip():  # Seulement si il y a des symboles
            combined_text = font.render(symbols, True, (255, 255, 255))
            text_width = combined_text.get_width()
            text_x = terrain_x + self.x * tile_size + (tile_size - text_width) // 2

            # Fond semi-transparent pour le texte
            text_rect = pygame.Rect(text_x - 2, terrain_y + self.y * tile_size + 5, text_width + 4, 12)
            overlay = pygame.Surface((text_width + 4, 12))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (text_x - 2, terrain_y + self.y * tile_size + 5))

            screen.blit(combined_text, (text_x, terrain_y + self.y * tile_size + 5))

        # Indicateur de PV faible
        if self.pv == 1:
            # Petite croix rouge si PV faible
            cross_size = 4
            cross_x = terrain_x + self.x * tile_size + tile_size - cross_size - 2
            cross_y = terrain_y + self.y * tile_size + 2
            pygame.draw.line(screen, (255, 0, 0),
                             (cross_x, cross_y),
                             (cross_x + cross_size, cross_y + cross_size), 2)
            pygame.draw.line(screen, (255, 0, 0),
                             (cross_x + cross_size, cross_y),
                             (cross_x, cross_y + cross_size), 2)

        # Bordure verte si sur un objectif
        for obj in objectives:
            if self.x == obj['x'] and self.y == obj['y']:
                pygame.draw.rect(screen, (0, 255, 0), rect, 2)
                break

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