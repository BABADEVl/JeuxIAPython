import pygame
from init import *
from unit import Unit
from display import *
from ia import ia_play_adaptive
from ai_trainer import AITrainer

pygame.init()

# Charger l'image de fond ou utiliser une couleur par défaut
try:
    background_img = pygame.image.load("assets/background.jpg")
    background_img = pygame.transform.scale(background_img, (width, height + interface_height))
except pygame.error:
    background_img = pygame.Surface((width, height + interface_height))
    background_img.fill((30, 30, 50))  # Bleu foncé

screen = pygame.display.set_mode((width, height + interface_height))
pygame.display.set_caption("Jeu Stratégique - Joueur vs IA Entraînée")

# Initialiser le système d'IA entraînée
ai_trainer = AITrainer()
print(f"IA chargée avec {ai_trainer.global_stats.get('games_played', 0)} parties d'expérience")
if ai_trainer.global_stats.get('games_played', 0) > 0:
    winrate = ai_trainer.global_stats['games_won'] / ai_trainer.global_stats['games_played'] * 100
    print(f"Taux de victoire de l'IA : {winrate:.1f}%")
    print(f"Génération actuelle : {ai_trainer.global_stats.get('generation', 0)}")

# Initialisation du jeu
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
turn_count = 0

# Variables pour l'IA
ai_delay = 1000  # Délai en millisecondes entre chaque action IA (ajustable)
last_ai_action = 0
ai_units_to_process = []
ai_processing = False

# Reset pour cette nouvelle partie
ai_trainer._reset_current_game()

terrain_width = tile_size * size
terrain_height = tile_size * size
terrain_x = (width - terrain_width) // 2
terrain_y = 20

clock = pygame.time.Clock()


# Interface utilisateur améliorée
def draw_game_info(screen, turn_count, ai_delay, trainer):
    """Affiche les informations de jeu et de l'IA"""
    font = pygame.font.SysFont(None, 20)

    # Informations de base
    turn_text = font.render(f"Tour: {turn_count}", True, (255, 255, 255))
    screen.blit(turn_text, (10, height + interface_height - 80))

    speed_text = font.render(f"Vitesse IA: {ai_delay}ms", True, (200, 200, 200))
    screen.blit(speed_text, (10, height + interface_height - 60))

    # Stats de l'IA
    if trainer.global_stats.get('games_played', 0) > 0:
        winrate = trainer.global_stats['games_won'] / trainer.global_stats['games_played'] * 100
        ai_stats = font.render(f"IA: Gen.{trainer.global_stats.get('generation', 0)} - {winrate:.1f}% victoires",
                               True, (180, 180, 255))
        screen.blit(ai_stats, (10, height + interface_height - 40))

    # Instructions
    controls_font = pygame.font.SysFont(None, 16)
    controls = [
        "Clic gauche: Sélectionner unité",
        "Clic droit: Déplacer/Attaquer",
        "ESPACE: Finir tour",
        "F: Accélérer IA",
        "S: Ralentir IA"
    ]

    for i, control in enumerate(controls):
        control_text = controls_font.render(control, True, (150, 150, 150))
        screen.blit(control_text, (width - 200, height + 10 + i * 15))


def show_victory_screen(screen, message, player_score, enemy_score, turn_count):
    """Affiche l'écran de victoire avec statistiques"""
    # Fond semi-transparent
    overlay = pygame.Surface((width, height + interface_height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Message de victoire
    victory_font = pygame.font.SysFont(None, 48)
    victory_surface = victory_font.render(message, True, (255, 255, 0))
    victory_rect = victory_surface.get_rect(center=(width // 2, height // 2 - 50))
    screen.blit(victory_surface, victory_rect)

    # Statistiques de la partie
    stats_font = pygame.font.SysFont(None, 24)
    stats = [
        f"Score final: Joueur {player_score} - IA {enemy_score}",
        f"Nombre de tours: {turn_count}",
        f"Durée de partie: {turn_count * 2} actions"
    ]

    for i, stat in enumerate(stats):
        stat_surface = stats_font.render(stat, True, (255, 255, 255))
        stat_rect = stat_surface.get_rect(center=(width // 2, height // 2 + 10 + i * 30))
        screen.blit(stat_surface, stat_rect)

    # Instructions
    restart_font = pygame.font.SysFont(None, 20)
    restart_text = restart_font.render("Appuyez sur R pour rejouer ou ECHAP pour quitter", True, (200, 200, 200))
    restart_rect = restart_text.get_rect(center=(width // 2, height // 2 + 120))
    screen.blit(restart_text, restart_rect)


def reset_game():
    """Remet le jeu à zéro pour une nouvelle partie"""
    global game_map, units, objectives, selected_unit, player_turn, units_to_move
    global player_score, enemy_score, victory, victory_message, turn_count
    global ai_units_to_process, ai_processing

    game_map = generate_map(size)
    units = generate_units()
    objectives = add_objectives()
    selected_unit = None
    player_turn = True
    units_to_move = [unit for unit in units if unit.color == PLAYER_COLOR]
    player_score = 0
    enemy_score = 0
    victory = False
    victory_message = ""
    turn_count = 0
    ai_units_to_process = []
    ai_processing = False
    ai_trainer._reset_current_game()


# Boucle principale du jeu
running = True
print("\n=== JEU DÉMARRÉ ===")
print("Vous jouez les unités bleues contre l'IA rouge entraînée")
print("Objectif: Atteindre 50 points en premier")
print("Contrôles: Clic gauche = sélectionner, Clic droit = action, ESPACE = fin de tour")

while running:
    current_time = pygame.time.get_ticks()

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and victory:
                reset_game()
            elif event.key == pygame.K_SPACE and not victory:
                if player_turn:
                    # Finir le tour du joueur
                    for unit in units_to_move:
                        unit.moved = False
                        unit.attacked_this_turn = False

                    if selected_unit:
                        selected_unit.selected = False
                        selected_unit = None

                    player_turn = False
                    units_to_move = [unit for unit in units if unit.color == ENEMY_COLOR]
                    turn_count += 1
            elif event.key == pygame.K_f:
                ai_delay = max(100, ai_delay - 200)
                print(f"IA accélérée: {ai_delay}ms")
            elif event.key == pygame.K_s:
                ai_delay = min(3000, ai_delay + 200)
                print(f"IA ralentie: {ai_delay}ms")

        elif event.type == pygame.MOUSEBUTTONDOWN and not victory:
            x, y = event.pos

            # Vérifier si c'est le tour du joueur
            if player_turn:
                # Vérifier si clic sur bouton "Fin de tour"
                if end_turn_button_clicked(
                        (x, y), width, height, interface_height,
                        terrain_x, terrain_y, terrain_width, terrain_height,
                        BUTTON_WIDTH, BUTTON_HEIGHT
                ):
                    # Finir le tour du joueur
                    for unit in units_to_move:
                        unit.moved = False
                        unit.attacked_this_turn = False

                    if selected_unit:
                        selected_unit.selected = False
                        selected_unit = None

                    player_turn = False
                    units_to_move = [unit for unit in units if unit.color == ENEMY_COLOR]
                    turn_count += 1

                else:
                    # Conversion en coordonnées de grille
                    grid_x = (x - terrain_x) // tile_size
                    grid_y = (y - terrain_y) // tile_size

                    if 0 <= grid_x < size and 0 <= grid_y < size:
                        if event.button == 1:  # Clic gauche - Sélection
                            possible_units = [u for u in units if
                                              u.x == grid_x and u.y == grid_y and not u.moved and u.color == PLAYER_COLOR]

                            if selected_unit in possible_units:
                                # Cycle entre les unités sur la même case
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

                        elif event.button == 3:  # Clic droit - Action
                            if selected_unit and selected_unit.color == PLAYER_COLOR:
                                # Vérifier s'il y a une cible à attaquer
                                target_unit = [u for u in units if
                                               u.x == grid_x and u.y == grid_y and u.color != selected_unit.color]

                                if target_unit:
                                    # Attaquer
                                    for cible in target_unit:
                                        selected_unit.attack(cible, units, objectives)
                                    selected_unit.selected = False
                                    selected_unit = None
                                elif selected_unit.can_move(grid_x, grid_y, units):
                                    # Déplacer
                                    selected_unit.move(grid_x, grid_y)
                                    selected_unit.selected = False
                                    selected_unit = None

    if not victory:
        # Tour de l'IA (plus sophistiqué)
        if not player_turn:
            # Gérer les événements de fermeture même pendant le tour IA
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Initialiser les unités IA à traiter
            if not ai_processing:
                ai_units_to_process = [unit for unit in units if unit.color == ENEMY_COLOR and not unit.moved]
                ai_processing = True
                last_ai_action = current_time

            # Traiter une unité IA toutes les ai_delay millisecondes
            if ai_processing and ai_units_to_process and current_time - last_ai_action >= ai_delay:
                current_ai_unit = ai_units_to_process.pop(0)

                # Utiliser l'IA adaptative entraînée
                action, target = ia_play_adaptive(current_ai_unit, units, objectives, size, ai_trainer)

                # Enregistrer l'action pour continuer l'apprentissage
                success = target is not None
                ai_trainer.record_action(action, success)

                last_ai_action = current_time

                # Si plus d'unités à traiter, finir le tour IA
                if not ai_units_to_process:
                    # Finir le tour de l'IA
                    for unit in units_to_move:
                        unit.moved = False
                        unit.attacked_this_turn = False

                    player_turn = True
                    units_to_move = [unit for unit in units if unit.color == PLAYER_COLOR]
                    ai_processing = False

        # Calcul des scores à chaque fin de tour
        if player_turn and turn_count > 0:  # Éviter le calcul au début
            player_score_turn, enemy_score_turn = calculate_scores(units, objectives)
            player_score += player_score_turn
            enemy_score += enemy_score_turn

            # Vérification des conditions de victoire
            if player_score >= 50:
                victory = True
                victory_message = "Victoire Joueur!"
                ai_trainer.end_game('lose', enemy_score, player_score)
                print(f"\nVictoire du joueur! Score final: {player_score} - {enemy_score}")

            elif enemy_score >= 50:
                victory = True
                victory_message = "Victoire de l'IA!"
                analysis, recommendations = ai_trainer.end_game('win', enemy_score, player_score)
                print(f"\nVictoire de l'IA! Score final: {enemy_score} - {player_score}")
                print(f"Performance IA: {analysis.get('overall_rating', 'N/A')}")

            elif not any(unit.color == PLAYER_COLOR for unit in units):
                victory = True
                victory_message = "Victoire de l'IA - Élimination!"
                ai_trainer.end_game('win', enemy_score, player_score)
                print(f"\nVictoire de l'IA par élimination!")

            elif not any(unit.color == ENEMY_COLOR for unit in units):
                victory = True
                victory_message = "Victoire Joueur - Élimination!"
                ai_trainer.end_game('lose', enemy_score, player_score)
                print(f"\nVictoire du joueur par élimination!")

    # Affichage
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

    # Afficher les informations supplémentaires
    draw_game_info(screen, turn_count, ai_delay, ai_trainer)

    if victory:
        show_victory_screen(screen, victory_message, player_score, enemy_score, turn_count)

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
print("\nMerci d'avoir joué!")