import json
import os
import time
from collections import defaultdict
import random
from ia import ia_play


class AITrainer:
    """Système d'entraînement et d'optimisation de l'IA"""

    def __init__(self, stats_file="ai_stats.json"):
        self.stats_file = stats_file
        self.current_game_stats = {
            'actions_taken': defaultdict(int),
            'successful_actions': defaultdict(int),
            'failed_actions': defaultdict(int),
            'game_result': None,
            'score_gained': 0,
            'units_killed': 0,
            'units_lost': 0,
            'objectives_captured': defaultdict(int),
            'turn_count': 0
        }
        self.global_stats = self.load_stats()

    def load_stats(self):
        """Charger les statistiques globales depuis le fichier"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Statistiques par défaut
        return {
            'games_played': 0,
            'games_won': 0,
            'total_actions': defaultdict(int),
            'successful_actions': defaultdict(int),
            'action_success_rate': defaultdict(float),
            'average_score': 0,
            'best_score': 0,
            'strategy_effectiveness': defaultdict(list),
            'learning_progress': []
        }

    def save_stats(self):
        """Sauvegarder les statistiques"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.global_stats, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des stats: {e}")

    def record_action(self, action_type, success=None, context=None):
        """Enregistrer une action de l'IA"""
        self.current_game_stats['actions_taken'][action_type] += 1

        if success is True:
            self.current_game_stats['successful_actions'][action_type] += 1
        elif success is False:
            self.current_game_stats['failed_actions'][action_type] += 1

        # Enregistrer le contexte pour l'apprentissage
        if context:
            self.current_game_stats[f'{action_type}_context'] = context

    def record_game_event(self, event_type, value=1):
        """Enregistrer des événements de jeu"""
        if event_type in ['units_killed', 'units_lost', 'score_gained', 'turn_count']:
            self.current_game_stats[event_type] += value
        elif event_type.startswith('objective_'):
            obj_type = event_type.split('_')[1]  # major ou minor
            self.current_game_stats['objectives_captured'][obj_type] += value

    def end_game(self, result, final_score, enemy_score):
        """Terminer une partie et analyser les performances"""
        self.current_game_stats['game_result'] = result  # 'win', 'lose', 'draw'
        self.current_game_stats['final_score'] = final_score
        self.current_game_stats['enemy_score'] = enemy_score

        # Mettre à jour les statistiques globales
        self._update_global_stats()

        # Analyser les performances
        performance_analysis = self._analyze_performance()

        # Sauvegarder
        self.save_stats()

        # Recommandations d'amélioration
        recommendations = self._generate_recommendations()

        # Réinitialiser pour la prochaine partie
        self._reset_current_game()

        return performance_analysis, recommendations

    def _update_global_stats(self):
        """Mettre à jour les statistiques globales"""
        self.global_stats['games_played'] += 1

        if self.current_game_stats['game_result'] == 'win':
            self.global_stats['games_won'] += 1

        # Actions
        for action, count in self.current_game_stats['actions_taken'].items():
            self.global_stats['total_actions'][action] += count

        for action, count in self.current_game_stats['successful_actions'].items():
            self.global_stats['successful_actions'][action] += count

        # Taux de succès
        for action in self.global_stats['total_actions']:
            total = self.global_stats['total_actions'][action]
            success = self.global_stats['successful_actions'].get(action, 0)
            if total > 0:
                self.global_stats['action_success_rate'][action] = success / total

        # Scores
        current_score = self.current_game_stats['final_score']
        games_played = self.global_stats['games_played']

        if games_played == 1:
            self.global_stats['average_score'] = current_score
        else:
            # Moyenne mobile
            old_avg = self.global_stats['average_score']
            self.global_stats['average_score'] = (old_avg * (games_played - 1) + current_score) / games_played

        if current_score > self.global_stats['best_score']:
            self.global_stats['best_score'] = current_score

        # Progression d'apprentissage
        win_rate = self.global_stats['games_won'] / games_played
        self.global_stats['learning_progress'].append({
            'game': games_played,
            'win_rate': win_rate,
            'score': current_score,
            'timestamp': time.time()
        })

        # Garder seulement les 100 dernières parties pour la progression
        if len(self.global_stats['learning_progress']) > 100:
            self.global_stats['learning_progress'] = self.global_stats['learning_progress'][-100:]

    def _analyze_performance(self):
        """Analyser les performances de la partie"""
        stats = self.current_game_stats
        analysis = {
            'efficiency': 0,
            'aggressiveness': 0,
            'objective_focus': 0,
            'survival': 0,
            'overall_rating': 'C'
        }

        # Efficacité (ratio actions réussies/tentées)
        total_actions = sum(stats['actions_taken'].values())
        total_success = sum(stats['successful_actions'].values())
        if total_actions > 0:
            analysis['efficiency'] = (total_success / total_actions) * 100

        # Agressivité (attaques vs mouvements défensifs)
        attack_actions = stats['actions_taken'].get('attack', 0) + stats['actions_taken'].get('attack_weak', 0)
        defensive_actions = stats['actions_taken'].get('flee', 0) + stats['actions_taken'].get('group', 0)
        if attack_actions + defensive_actions > 0:
            analysis['aggressiveness'] = (attack_actions / (attack_actions + defensive_actions)) * 100

        # Focus objectifs (actions liées aux objectifs vs autres)
        objective_actions = (stats['actions_taken'].get('move_major', 0) +
                             stats['actions_taken'].get('move_minor', 0) +
                             stats['actions_taken'].get('protect_objective', 0))
        if total_actions > 0:
            analysis['objective_focus'] = (objective_actions / total_actions) * 100

        # Survie (ratio unités conservées)
        units_lost = stats['units_lost']
        analysis['survival'] = max(0, 100 - (units_lost * 20))  # -20% par unité perdue

        # Note globale
        overall_score = (analysis['efficiency'] + analysis['objective_focus'] + analysis['survival']) / 3
        if overall_score >= 80:
            analysis['overall_rating'] = 'A'
        elif overall_score >= 60:
            analysis['overall_rating'] = 'B'
        elif overall_score >= 40:
            analysis['overall_rating'] = 'C'
        else:
            analysis['overall_rating'] = 'D'

        return analysis

    def _generate_recommendations(self):
        """Générer des recommandations d'amélioration"""
        recommendations = []
        stats = self.current_game_stats

        # Analyser les faiblesses
        if stats['units_lost'] > 2:
            recommendations.append("Améliorer la survie des unités - éviter les combats risqués")

        if stats['objectives_captured']['major'] == 0:
            recommendations.append("Se concentrer davantage sur les objectifs majeurs (3 points)")

        if stats['actions_taken'].get('attack', 0) < 2:
            recommendations.append("Être plus agressif - attaquer plus souvent")

        # Recommandations basées sur les statistiques globales
        if self.global_stats['action_success_rate'].get('flee', 1) < 0.5:
            recommendations.append("Améliorer la stratégie de fuite - choisir de meilleures positions")

        if self.global_stats['games_played'] > 5:
            recent_wins = sum(1 for game in self.global_stats['learning_progress'][-5:]
                              if game.get('win_rate', 0) > 0.5)
            if recent_wins < 2:
                recommendations.append("Revoir la stratégie globale - taux de victoire faible")

        return recommendations

    def get_action_priorities(self):
        """Obtenir les priorités d'actions basées sur l'apprentissage"""
        priorities = {}

        for action, success_rate in self.global_stats['action_success_rate'].items():
            # Plus le taux de succès est élevé, plus l'action est prioritaire
            priorities[action] = success_rate

        # Actions qui manquent de données (explorer)
        for action in ['attack', 'move_major', 'move_minor', 'flee', 'group']:
            if action not in priorities and random.random() < 0.1:  # 10% d'exploration
                priorities[action] = 0.5  # Priorité moyenne pour exploration

        return priorities

    def should_explore(self, action):
        """Déterminer si l'IA devrait explorer une action moins utilisée"""
        total_games = self.global_stats['games_played']
        action_count = self.global_stats['total_actions'].get(action, 0)

        # Plus de chance d'explorer si l'action est peu utilisée
        if total_games > 0:
            exploration_chance = max(0.05, 0.3 - (action_count / total_games))
            return random.random() < exploration_chance

        return random.random() < 0.2  # 20% d'exploration par défaut

    def _reset_current_game(self):
        """Réinitialiser les statistiques de la partie courante"""
        self.current_game_stats = {
            'actions_taken': defaultdict(int),
            'successful_actions': defaultdict(int),
            'failed_actions': defaultdict(int),
            'game_result': None,
            'score_gained': 0,
            'units_killed': 0,
            'units_lost': 0,
            'objectives_captured': defaultdict(int),
            'turn_count': 0
        }

    def print_report(self):
        """Afficher un rapport des performances"""
        stats = self.global_stats
        print("\n" + "=" * 50)
        print("RAPPORT D'ENTRAÎNEMENT IA")
        print("=" * 50)
        print(f"Parties jouées: {stats['games_played']}")
        print(f"Victoires: {stats['games_won']} ({stats['games_won'] / max(1, stats['games_played']) * 100:.1f}%)")
        print(f"Score moyen: {stats['average_score']:.1f}")
        print(f"Meilleur score: {stats['best_score']}")

        print("\nTAUX DE SUCCÈS PAR ACTION:")
        for action, rate in sorted(stats['action_success_rate'].items(), key=lambda x: x[1], reverse=True):
            total = stats['total_actions'].get(action, 0)
            print(f"  {action}: {rate * 100:.1f}% (sur {total} tentatives)")

        if len(stats['learning_progress']) >= 2:
            recent_winrate = stats['learning_progress'][-1]['win_rate']
            old_winrate = stats['learning_progress'][0]['win_rate']
            improvement = (recent_winrate - old_winrate) * 100
            print(f"\nPROGRÈS: {improvement:+.1f}% de taux de victoire")


# Exemple d'utilisation dans le jeu
def integrate_trainer_to_game():
    """Exemple d'intégration du trainer dans le jeu principal"""
    trainer = AITrainer()

    # En début de partie
    trainer._reset_current_game()

    # Pendant le jeu (dans ia.py)
    def ia_play_with_training(unit, units, objectives, size, trainer=None):
        action, target = ia_play(unit, units, objectives, size)  # Fonction IA existante

        if trainer:
            # Enregistrer l'action
            success = target is not None  # Simple heuristique
            trainer.record_action(action, success)

        return action, target

    # En fin de partie
    # result = 'win' si IA gagne, 'lose' sinon
    # analysis, recommendations = trainer.end_game(result, ai_score, player_score)

    return trainer