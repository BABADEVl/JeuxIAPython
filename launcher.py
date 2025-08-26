#!/usr/bin/env python3
"""
Script de lancement pour le jeu de stratégie
Permet de configurer et lancer le jeu avec différentes options
"""

import os
import sys
import argparse
from ai_trainer import AITrainer


def check_dependencies():
    """Vérifier que les dépendances sont installées"""
    try:
        import pygame
        print("✓ Pygame détecté")
        return True
    except ImportError:
        print("❌ Pygame non trouvé!")
        print("Installation: pip install pygame")
        return False


def check_files():
    """Vérifier que tous les fichiers nécessaires sont présents"""
    required_files = [
        'jeu.py',
        'init.py',
        'unit.py',
        'display.py',
        'ia.py',
        'ai_trainer.py'
    ]

    optional_files = [
        'assets/background.jpg',
        'assets/end_turn.png',
        'assets/player_unit.png',
        'assets/enemy_unit.png',
        'assets/player_unit_weak.png',
        'assets/enemy_unit_weak.png'
    ]

    missing_required = []
    missing_optional = []

    for file in required_files:
        if not os.path.exists(file):
            missing_required.append(file)
        else:
            print(f"✓ {file}")

    for file in optional_files:
        if not os.path.exists(file):
            missing_optional.append(file)
        else:
            print(f"✓ {file}")

    if missing_required:
        print(f"\n❌ Fichiers manquants OBLIGATOIRES:")
        for file in missing_required:
            print(f"   - {file}")
        return False

    if missing_optional:
        print(f"\n⚠️  Fichiers optionnels manquants:")
        for file in missing_optional:
            print(f"   - {file}")
        print("   Le jeu fonctionnera avec les couleurs par défaut.")

    return True


def show_ai_stats():
    """Afficher les statistiques de l'IA"""
    trainer = AITrainer()

    if trainer.global_stats['games_played'] == 0:
        print("Aucune partie jouée pour l'instant.")
        return

    trainer.print_report()


def reset_ai_stats():
    """Réinitialiser les statistiques de l'IA"""
    if os.path.exists("ai_stats.json"):
        response = input("Êtes-vous sûr de vouloir supprimer toutes les statistiques IA? (oui/non): ")
        if response.lower() in ['oui', 'o', 'y', 'yes']:
            os.remove("ai_stats.json")
            print("✓ Statistiques IA supprimées.")
        else:
            print("Opération annulée.")
    else:
        print("Aucun fichier de statistiques trouvé.")


def modify_game_config():
    """Modifier la configuration du jeu"""
    print("=== MODIFICATION CONFIGURATION ===")
    print("Fichier: init.py")

    try:
        with open('init.py', 'r') as f:
            content = f.read()

        print("Configuration actuelle:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if any(var in line for var in ['tile_size', 'size', 'width', 'height']):
                print(f"  {line}")

        print("\nOptions de modification:")
        print("1. Taille des tuiles (tile_size)")
        print("2. Taille de la grille (size)")
        print("3. Dimensions fenêtre (width/height)")
        print("4. Retour")

        choice = input("Choisir une option: ")

        if choice == "1":
            new_size = input("Nouvelle taille des tuiles (actuel: 30): ")
            if new_size.isdigit():
                content = content.replace("tile_size = 30", f"tile_size = {new_size}")
                with open('init.py', 'w') as f:
                    f.write(content)
                print(f"✓ Taille des tuiles changée à {new_size}")

        elif choice == "2":
            print("⚠️  Attention: Changer la taille de grille peut affecter l'équilibrage")
            new_size = input("Nouvelle taille de grille (actuel: 20): ")
            if new_size.isdigit():
                content = content.replace("size = 20", f"size = {new_size}")
                with open('init.py', 'w') as f:
                    f.write(content)
                print(f"✓ Taille de grille changée à {new_size}x{new_size}")

    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")


def launch_game(ai_speed="normal"):
    """Lancer le jeu principal"""
    # Modifier la vitesse de l'IA si demandé
    if ai_speed != "normal":
        try:
            import jeu
            if ai_speed == "fast":
                jeu.ai_delay = 300  # 300ms entre actions
            elif ai_speed == "slow":
                jeu.ai_delay = 2000  # 2 secondes entre actions
        except:
            pass

    # Lancer le jeu
    print("🎮 Lancement du jeu...")
    os.system("python jeu.py")


def main():
    """Menu principal du launcher"""
    parser = argparse.ArgumentParser(description="Lanceur pour le jeu de stratégie")
    parser.add_argument('--stats', action='store_true', help='Afficher les statistiques IA')
    parser.add_argument('--reset-stats', action='store_true', help='Réinitialiser les statistiques IA')
    parser.add_argument('--fast-ai', action='store_true', help='IA rapide (300ms)')
    parser.add_argument('--slow-ai', action='store_true', help='IA lente (2s)')
    parser.add_argument('--check', action='store_true', help='Vérifier les fichiers')

    args = parser.parse_args()

    # Actions directes via arguments
    if args.stats:
        show_ai_stats()
        return

    if args.reset_stats:
        reset_ai_stats()
        return

    if args.check:
        print("=== VÉRIFICATION DES FICHIERS ===")
        check_dependencies()
        check_files()
        return

    # Menu interactif si pas d'arguments
    while True:
        print("\n" + "=" * 50)
        print("🎯 JEU DE STRATÉGIE - LAUNCHER")
        print("=" * 50)
        print("1. 🎮 Lancer le jeu")
        print("2. 🎮 Lancer le jeu (IA rapide)")
        print("3. 🎮 Lancer le jeu (IA lente)")
        print("4. 📊 Voir statistiques IA")
        print("5. 🗑️  Réinitialiser statistiques IA")
        print("6. ⚙️  Modifier configuration")
        print("7. 🔍 Vérifier les fichiers")
        print("8. ❌ Quitter")

        choice = input("\nChoisir une option (1-8): ")

        if choice == "1":
            if check_dependencies() and check_files():
                ai_speed = "fast" if args.fast_ai else "slow" if args.slow_ai else "normal"
                launch_game(ai_speed)
            break

        elif choice == "2":
            if check_dependencies() and check_files():
                launch_game("fast")
            break

        elif choice == "3":
            if check_dependencies() and check_files():
                launch_game("slow")
            break

        elif choice == "4":
            show_ai_stats()

        elif choice == "5":
            reset_ai_stats()

        elif choice == "6":
            modify_game_config()

        elif choice == "7":
            print("=== VÉRIFICATION DES FICHIERS ===")
            deps_ok = check_dependencies()
            files_ok = check_files()
            if deps_ok and files_ok:
                print("\n✅ Tout est prêt pour jouer!")

        elif choice == "8":
            print("Au revoir!")
            break

        else:
            print("⚠️  Option invalide, choisir un nombre entre 1 et 8")


if __name__ == "__main__":
    main()