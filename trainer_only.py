"""
Script dédié à l'entraînement de l'IA sans interface graphique
Utilise pour préparer l'IA avant de défier votre professeur !
"""

import pygame
import random
import time
from init import *
from unit import Unit
from display import generate_map, generate_units, add_objectives, calculate_scores
from ia import ia_play_adaptive
from ai_trainer import AITrainer

pygame.init()
pygame.display.set_mode((100, 100))  # Fenêtre minimale pour pygame


def simulate_game_fast(trainer, game_id):
    """Simule une partie complète rapidement (sans affichage)"""

    # Initialisation
    game_map = generate_map(size)
    units = generate_units()
    objectives = add_objectives()

    player_score = 0
    enemy_score = 0
    turn_count = 0
    player_turn = True

    # Reset du trainer pour cette partie
    trainer._reset_current_game()

    max_turns = 300  # Limite pour éviter les parties infinies

    while turn_count < max_turns:
        # Jouer toutes les unités du joueur actuel
        if player_turn:
            # IA Bleue (joueur simulé)
            blue_units = [u for u in units if u.color == PLAYER_COLOR and not u.moved]
            for unit in blue_units:
                # Utiliser une variante de l'IA adaptative pour le joueur bleu
                temp_weights = trainer.strategy_weights.copy()
                temp_weights['defensive'] *= 1.5  # Plus défensif
                temp_weights['aggressive'] *= 0.7  # Moins agressif

                temp_trainer = type('obj', (object,), {
                    'strategy_weights': temp_weights,
                    'should_explore': lambda self, action: random.random() < 0.05
                })()

                ia_play_adaptive(unit, units, objectives, size, temp_trainer)
        else:
            # IA Rouge (celle qu'on entraîne)
            red_units = [u for u in units if u.color == ENEMY_COLOR and not u.moved]
            for unit in red_units:
                action, target = ia_play_adaptive(unit, units, objectives, size, trainer)

                # Enregistrer l'action pour l'apprentissage
                success = target is not None
                trainer.record_action(action, success)

        # Reset du statut "moved"
        for unit in units:
            if (unit.color == PLAYER_COLOR and player_turn) or (unit.color == ENEMY_COLOR and not player_turn):
                unit.moved = False
                unit.attacked_this_turn = False

        player_turn = not player_turn
        turn_count += 1

        # Calcul des scores
        player_score, enemy_score = calculate_scores(units, objectives)

        # Vérifications de fin de partie
        if player_score >= 50:
            # Joueur (bleu) gagne
            trainer.end_game('lose', enemy_score, player_score)
            return 'blue_win', turn_count, player_score, enemy_score

        elif enemy_score >= 50:
            # IA (rouge) gagne
            trainer.end_game('win', enemy_score, player_score)
            return 'red_win', turn_count, player_score, enemy_score

        elif not any(unit.color == PLAYER_COLOR for unit in units):
            trainer.end_game('win', enemy_score, player_score)
            return 'red_win', turn_count, player_score, enemy_score

        elif not any(unit.color == ENEMY_COLOR for unit in units):
            trainer.end_game('lose', enemy_score, player_score)
            return 'blue_win', turn_count, player_score, enemy_score

    # Partie trop longue, victoire au score
    if enemy_score >= player_score:
        trainer.end_game('win', enemy_score, player_score)
        return 'red_win', turn_count, player_score, enemy_score
    else:
        trainer.end_game('lose', enemy_score, player_score)
        return 'blue_win', turn_count, player_score, enemy_score


def run_training_batch(num_games, trainer):
    """Lance un lot d'entraînement"""

    print(f"\n🏃‍♂️ Lancement de {num_games} parties d'entraînement...")

    results = {
        'red_wins': 0,
        'blue_wins': 0,
        'total_turns': 0,
        'total_score': 0,
        'start_time': time.time()
    }

    for i in range(num_games):
        result, turns, player_score, enemy_score = simulate_game_fast(trainer, i + 1)

        results['total_turns'] += turns
        results['total_score'] += enemy_score

        if result == 'red_win':
            results['red_wins'] += 1
        else:
            results['blue_wins'] += 1

        # Affichage progression
        if (i + 1) % 10 == 0:
            elapsed = time.time() - results['start_time']
            speed = (i + 1) / elapsed
            red_winrate = results['red_wins'] / (i + 1) * 100

            print(f"  Progression: {i + 1:3d}/{num_games} | "
                  f"IA: {red_winrate:5.1f}% victoires | "
                  f"Vitesse: {speed:.1f} parties/sec")

    return results


def main_training():
    """Programme principal d'entraînement"""

    print("🎯 ENTRAÎNEMENT INTENSIF DE L'IA")
    print("=" * 50)
    print("Ce programme va entraîner votre IA pour battre votre prof d'informatique!")
    print("")

    trainer = AITrainer()

    # Afficher l'état actuel
    if trainer.global_stats['games_played'] > 0:
        print(f"📊 État actuel de l'IA:")
        print(f"   - Parties jouées: {trainer.global_stats['games_played']}")
        print(
            f"   - Taux de victoire: {trainer.global_stats['games_won'] / trainer.global_stats['games_played'] * 100:.1f}%")
        print(f"   - Génération: {trainer.global_stats.get('generation', 0)}")
        print("")

    # Menu d'entraînement
    while True:
        print("Options d'entraînement:")
        print("1. 🚀 Entraînement rapide (100 parties)")
        print("2. 💪 Entraînement intensif (500 parties)")
        print("3. 🏆 Entraînement champion (1000 parties)")
        print("4. 🔧 Entraînement personnalisé")
        print("5. 📊 Voir statistiques détaillées")
        print("6. 🎮 Tester l'IA contre vous")
        print("7. ❌ Quitter")

        choice = input("\nChoisir une option (1-7): ").strip()

        if choice == '1':
            results = run_training_batch(100, trainer)
            print_training_results(results, 100)

        elif choice == '2':
            results = run_training_batch(500, trainer)
            print_training_results(results, 500)

        elif choice == '3':
            results = run_training_batch(1000, trainer)
            print_training_results(results, 1000)

        elif choice == '4':
            try:
                num = int(input("Nombre de parties à jouer: "))
                if num > 0:
                    results = run_training_batch(num, trainer)
                    print_training_results(results, num)
                else:
                    print("❌ Nombre invalide")
            except ValueError:
                print("❌ Veuillez entrer un nombre")

        elif choice == '5':
            trainer.print_report()

        elif choice == '6':
            print("🎮 Lancement du jeu contre l'IA...")
            pygame.quit()
            import subprocess
            subprocess.run(["python", "jeu.py"])
            break

        elif choice == '7':
            break

        else:
            print("❌ Option invalide")

    pygame.quit()

    # Rapport final
    final_stats = trainer.global_stats
    print(f"\n🏁 ENTRAÎNEMENT TERMINÉ!")
    print(f"📈 Statistiques finales:")
    print(f"   - Total parties: {final_stats['games_played']}")
    print(f"   - Victoires IA: {final_stats['games_won']}")
    print(f"   - Taux victoire: {final_stats['games_won'] / final_stats['games_played'] * 100:.1f}%")
    print(f"   - Génération: {final_stats.get('generation', 0)}")
    print(f"   - Score moyen: {final_stats['average_score']:.1f}")

    if final_stats['games_won'] / final_stats['games_played'] > 0.6:
        print("🏆 Votre IA est prête à défier votre professeur!")
    elif final_stats['games_won'] / final_stats['games_played'] > 0.4:
        print("⚡ L'IA progresse bien, quelques parties d'entraînement en plus seraient utiles")
    else:
        print("💪 L'IA a encore besoin d'entraînement pour être compétitive")


def print_training_results(results, num_games):
    """Affiche les résultats d'une session d'entraînement"""

    elapsed = time.time() - results['start_time']
    red_winrate = results['red_wins'] / num_games * 100
    avg_turns = results['total_turns'] / num_games
    avg_score = results['total_score'] / num_games

    print(f"\n📊 RÉSULTATS D'ENTRAÎNEMENT")
    print(f"=" * 40)
    print(f"⏱️  Durée: {elapsed:.1f} secondes")
    print(f"🎮 Parties jouées: {num_games}")
    print(f"🔴 Victoires IA: {results['red_wins']} ({red_winrate:.1f}%)")
    print(f"🔵 Victoires adversaire: {results['blue_wins']}")
    print(f"📊 Tours moyen/partie: {avg_turns:.1f}")
    print(f"🎯 Score IA moyen: {avg_score:.1f}")
    print(f"⚡ Vitesse: {num_games / elapsed:.1f} parties/seconde")

    if red_winrate >= 70:
        print("🏆 Excellent! L'IA est très forte!")
    elif red_winrate >= 55:
        print("💪 Bon niveau! L'IA progresse bien!")
    elif red_winrate >= 40:
        print("📈 En progrès, continuez l'entraînement")
    else:
        print("🔄 L'IA a besoin de plus d'entraînement")


if __name__ == "__main__":
    main_training()