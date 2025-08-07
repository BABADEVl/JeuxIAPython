import pygame
from init import *
from unit import Unit
from display import *

pygame.init()
background_img = pygame.image.load("assets/background.jpg")
background_img = pygame.transform.scale(background_img, (width, height + interface_height))

screen = pygame.display.set_mode((width, height + interface_height))
pygame.display.set_caption("Carte de 20x20 avec unités et déplacement")

game_map = generate_map(size)
units = generate_units()
objectives = add_objectives()

selected_unit = None
player_turn = True
units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
player_score = 0
enemy_score = 0
victory = False
victory_message = ""

terrain_width = tile_size * size
terrain_height = tile_size * size
terrain_x = (width - terrain_width) // 2
terrain_y = 20

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
                if end_turn_button_clicked(
                    (x, y), width, height, interface_height,
                    terrain_x, terrain_y, terrain_width, terrain_height,
                    BUTTON_WIDTH, BUTTON_HEIGHT
                ):
                    unit_moved = True
                else:
                    grid_x = (x - terrain_x) // tile_size
                    grid_y = (y - terrain_y) // tile_size
                    if 0 <= grid_x < size and 0 <= grid_y < size:
                        if event.button == 1:
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
                        elif event.button == 3:
                            if selected_unit and selected_unit.color == (PLAYER_COLOR if player_turn else ENEMY_COLOR):
                                target_unit = [u for u in units if u.x == grid_x and u.y == grid_y and u.color != selected_unit.color]
                                if target_unit:
                                    for cible in target_unit:
                                        selected_unit.attack(cible, units, objectives)
                                    selected_unit.selected = False
                                    selected_unit = None
                                elif selected_unit.can_move(grid_x, grid_y, units):
                                    selected_unit.move(grid_x, grid_y)
                                    selected_unit.selected = False
                                    selected_unit = None

        if unit_moved:
            for unit in units_to_move:
                unit.moved = False
                unit.attacked_this_turn = False
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

    screen.blit(background_img, (0, 0))
    draw_map(screen, game_map, tile_size, terrain_x, terrain_y)
    draw_objectives(screen, objectives, tile_size, terrain_x, terrain_y)

    for unit in units:
        unit.draw(screen, units, objectives, terrain_x, terrain_y)

    draw_turn_indicator(screen, player_turn)
    draw_end_turn_button(
        screen, width, height, interface_height,
        terrain_x, terrain_y, terrain_width, terrain_height,
        BUTTON_WIDTH, BUTTON_HEIGHT
    )
    draw_unit_attributes(screen, selected_unit, width, height, interface_height)
    draw_scores(
        screen, player_score, enemy_score, width, height,
        terrain_x, terrain_y, terrain_width, terrain_height
    )

    if victory:
        draw_victory_message(screen, victory_message, width, height)
        pygame.display.flip()
        pygame.time.wait(5000)
        running = False

    pygame.display.flip()

pygame.quit()