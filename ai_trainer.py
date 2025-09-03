import json
import os
import time
import random
from collections import defaultdict
from ia import ia_play


class AITrainer:
    """Système d'entraînement et d'optimisation de l'IA avec évolution des stratégies"""

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
            'turn_count': 0,
            'strategy_weights_used': {}
        }
        self.global_stats = self.load_stats()

        # Poids de stratégies évolutifs
        self.strategy_weights = self.global_stats.get('strategy_weights', {
            'aggressive': 0.3,
            'defensive': 0.3,
            'objective_focused': 0.4,
            'exploration': 0.1,
            'group_play': 0.2
        })

        # Historique des performances par stratégie
        self.strategy_performance = self.global_stats.get('strategy_performance', {})

    def load_stats(self):
        """Charger les statistiques globales depuis le fichier"""
        default_stats = {
            'games_played': 0,
            'games_won': 0,
            'total_actions': defaultdict(int),
            'successful_actions': defaultdict(int),
            'action_success_rate': defaultdict(float),
            'average_score': 0,
            'best_score': 0,
            'strategy_effectiveness': defaultdict(list),
            'learning_progress': [],
            'strategy_weights': {
                'aggressive': 0.3,
                'defensive': 0.3,
                'objective_focused': 0.4,
                'exploration': 0.1,
                'group_play': 0.2
            },
            'strategy_performance': {},
            'generation': 0,
            'evolution_history': []
        }

        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)

                    for key in default_stats:
                        if key in data:
                            if isinstance(default_stats[key], defaultdict):
                                default_stats[key] = defaultdict(
                                    type(list(default_stats[key].values())[0]) if default_stats[key] else int,
                                    data[key])
                            else:
                                default_stats[key] = data[key]

                    return default_stats
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                print(f"Fichier de statistiques corrompu ({e}), création d'un nouveau fichier")

        return default_stats

    def save_stats(self):
        """Sauvegarder les statistiques"""
        try:
            data_to_save = {}
            for key, value in self.global_stats.items():
                if isinstance(value, defaultdict):
                    data_to_save[key] = dict(value)
                else:
                    data_to_save[key] = value

            # Sauvegarder les poids de stratégie actuels
            data_to_save['strategy_weights'] = self.strategy_weights
            data_to_save['strategy_performance'] = self.strategy_performance

            with open(self.stats_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des stats: {e}")

    def evolve_strategy_weights(self):
        """Faire évoluer les poids de stratégie basés sur les performances"""
        if len(self.global_stats['learning_progress']) < 5:
            return

        # Calculer les performances récentes
        recent_games = self.global_stats['learning_progress'][-10:]
        recent_win_rate = sum(1 for game in recent_games if game.get('win_rate', 0) > 0.5) / len(recent_games)
        recent_avg_score = sum(game.get('score', 0) for game in recent_games) / len(recent_games)

        # Mutation des poids basée sur les performances
        mutation_rate = 0.1 if recent_win_rate < 0.4 else 0.05

        new_weights = {}
        for strategy, weight in self.strategy_weights.items():
            # Mutation aléatoire
            mutation = random.uniform(-mutation_rate, mutation_rate)
            new_weight = max(0.05, min(0.8, weight + mutation))
            new_weights[strategy] = new_weight

        # Si les performances sont mauvaises, augmenter l'exploration
        if recent_win_rate < 0.3:
            new_weights['exploration'] = min(0.5, new_weights['exploration'] + 0.1)
            new_weights['aggressive'] = max(0.1, new_weights['aggressive'] - 0.05)

        # Si trop défensif et peu de victoires, augmenter l'agressivité
        if recent_win_rate < 0.4 and new_weights['defensive'] > 0.4:
            new_weights['aggressive'] = min(0.6, new_weights['aggressive'] + 0.1)
            new_weights['defensive'] = max(0.1, new_weights['defensive'] - 0.05)

        self.strategy_weights = new_weights

        # Enregistrer l'évolution
        generation = self.global_stats.get('generation', 0) + 1
        self.global_stats['generation'] = generation

        evolution_entry = {
            'generation': generation,
            'weights': new_weights.copy(),
            'performance': {
                'win_rate': recent_win_rate,
                'avg_score': recent_avg_score
            },
            'timestamp': time.time()
        }

        if 'evolution_history' not in self.global_stats:
            self.global_stats['evolution_history'] = []

        self.global_stats['evolution_history'].append(evolution_entry)

        # Garder seulement les 50 dernières évolutions
        if len(self.global_stats['evolution_history']) > 50:
            self.global_stats['evolution_history'] = self.global_stats['evolution_history'][-50:]

        print(f"\n=== ÉVOLUTION GÉNÉRATION {generation} ===")
        print("Nouveaux poids de stratégie:")
        for strategy, weight in new_weights.items():
            print(f"  {strategy}: {weight:.3f}")
        print(f"Performance récente: {recent_win_rate:.1%} victoires, {recent_avg_score:.1f} points")

    def get_strategy_decision(self, action_type):
        """Décider si une action doit être prise basée sur les poids de stratégie"""
        # Mapper les actions aux stratégies
        action_strategy_map = {
            'attack': 'aggressive',
            'attack_weak': 'aggressive',
            'push_kill': 'aggressive',
            'flee': 'defensive',
            'group': 'group_play',
            'protect_ally': 'defensive',
            'move_major': 'objective_focused',
            'move_minor': 'objective_focused',
            'protect_objective': 'objective_focused',
            'explore': 'exploration'
        }

        strategy = action_strategy_map.get(action_type, 'exploration')
        weight = self.strategy_weights.get(strategy, 0.3)

        # Ajouter un peu de randomness
        random_factor = random.uniform(0.8, 1.2)
        final_probability = weight * random_factor

        return random.random() < final_probability

    def record_action(self, action_type, success=None, context=None):
        """Enregistrer une action de l'IA"""
        self.current_game_stats['actions_taken'][action_type] += 1

        if success is True:
            self.current_game_stats['successful_actions'][action_type] += 1
        elif success is False:
            self.current_game_stats['failed_actions'][action_type] += 1

        # Enregistrer les poids de stratégie utilisés
        self.current_game_stats['strategy_weights_used'] = self.strategy_weights.copy()

        if context:
            self.current_game_stats[f'{action_type}_context'] = context

    def record_game_event(self, event_type, value=1):
        """Enregistrer des événements de jeu"""
        if event_type in ['units_killed', 'units_lost', 'score_gained', 'turn_count']:
            self.current_game_stats[event_type] += value
        elif event_type.startswith('objective_'):
            obj_type = event_type.split('_')[1]
            self.current_game_stats['objectives_captured'][obj_type] += value

    def end_game(self, result, final_score, enemy_score):
        """Terminer une partie et analyser les performances"""
        self.current_game_stats['game_result'] = result
        self.current_game_stats['final_score'] = final_score
        self.current_game_stats['enemy_score'] = enemy_score

        # Mettre à jour les statistiques globales
        self._update_global_stats()

        # Analyser les performances
        performance_analysis = self._analyze_performance()

        # Faire évoluer les stratégies tous les 5 jeux
        if self.global_stats['games_played'] % 5 == 0:
            self.evolve_strategy_weights()

        # Sauvegarder
        self.save_stats()

        # Recommandations d'amélioration
        recommendations = self._generate_recommendations()

        # Réinitialiser pour la prochaine partie
        self._reset_current_game()

        return performance_analysis, recommendations

    def _update_global_stats(self):
        """Mettre à jour les statistiques globales"""
        if 'games_played' not in self.global_stats:
            self.global_stats['games_played'] = 0
        if 'games_won' not in self.global_stats:
            self.global_stats['games_won'] = 0
        if 'average_score' not in self.global_stats:
            self.global_stats['average_score'] = 0
        if 'best_score' not in self.global_stats:
            self.global_stats['best_score'] = 0
        if 'learning_progress' not in self.global_stats:
            self.global_stats['learning_progress'] = []

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
            'strategy_weights': self.current_game_stats['strategy_weights_used'].copy(),
            'timestamp': time.time()
        })

        # Garder seulement les 100 dernières parties
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

        # Efficacité
        total_actions = sum(stats['actions_taken'].values())
        total_success = sum(stats['successful_actions'].values())
        if total_actions > 0:
            analysis['efficiency'] = (total_success / total_actions) * 100

        # Agressivité
        attack_actions = stats['actions_taken'].get('attack', 0) + stats['actions_taken'].get('attack_weak', 0)
        defensive_actions = stats['actions_taken'].get('flee', 0) + stats['actions_taken'].get('group', 0)
        if attack_actions + defensive_actions > 0:
            analysis['aggressiveness'] = (attack_actions / (attack_actions + defensive_actions)) * 100

        # Focus objectifs
        objective_actions = (stats['actions_taken'].get('move_major', 0) +
                             stats['actions_taken'].get('move_minor', 0) +
                             stats['actions_taken'].get('protect_objective', 0))
        if total_actions > 0:
            analysis['objective_focus'] = (objective_actions / total_actions) * 100

        # Survie
        units_lost = stats['units_lost']
        analysis['survival'] = max(0, 100 - (units_lost * 20))

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

        if stats['units_lost'] > 2:
            recommendations.append("Améliorer la survie des unités - éviter les combats risqués")

        if stats['objectives_captured']['major'] == 0:
            recommendations.append("Se concentrer davantage sur les objectifs majeurs (3 points)")

        if stats['actions_taken'].get('attack', 0) < 2:
            recommendations.append("Être plus agressif - attaquer plus souvent")

        if self.global_stats['action_success_rate'].get('flee', 1) < 0.5:
            recommendations.append("Améliorer la stratégie de fuite - choisir de meilleures positions")

        if self.global_stats['games_played'] > 5:
            recent_wins = sum(1 for game in self.global_stats['learning_progress'][-5:]
                              if game.get('win_rate', 0) > 0.5)
            if recent_wins < 2:
                recommendations.append("Revoir la stratégie globale - taux de victoire faible")

        return recommendations

    def get_action_priorities(self):
        """Obtenir les priorités d'actions basées sur l'apprentissage et les stratégies"""
        priorities = {}

        # Basé sur les taux de succès historiques
        for action, success_rate in self.global_stats['action_success_rate'].items():
            priorities[action] = success_rate

        # Ajuster selon les poids de stratégie
        strategy_adjustments = {
            'attack': self.strategy_weights.get('aggressive', 0.3),
            'attack_weak': self.strategy_weights.get('aggressive', 0.3),
            'flee': self.strategy_weights.get('defensive', 0.3),
            'group': self.strategy_weights.get('group_play', 0.2),
            'move_major': self.strategy_weights.get('objective_focused', 0.4),
            'move_minor': self.strategy_weights.get('objective_focused', 0.4)
        }

        for action, weight in strategy_adjustments.items():
            if action in priorities:
                priorities[action] = (priorities[action] + weight) / 2
            else:
                priorities[action] = weight

        return priorities

    def should_explore(self, action):
        """Déterminer si l'IA devrait explorer une action"""
        exploration_rate = self.strategy_weights.get('exploration', 0.1)
        return random.random() < exploration_rate

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
            'turn_count': 0,
            'strategy_weights_used': {}
        }

    def print_report(self):
        """Afficher un rapport des performances"""
        stats = self.global_stats
        print("\n" + "=" * 60)
        print("RAPPORT D'ENTRAÎNEMENT IA - ÉVOLUTION DES STRATÉGIES")
        print("=" * 60)
        print(f"Parties jouées: {stats['games_played']}")
        print(f"Victoires: {stats['games_won']} ({stats['games_won'] / max(1, stats['games_played']) * 100:.1f}%)")
        print(f"Score moyen: {stats['average_score']:.1f}")
        print(f"Meilleur score: {stats['best_score']}")
        print(f"Génération actuelle: {stats.get('generation', 0)}")

        print(f"\nPOIDS DE STRATÉGIE ACTUELS:")
        for strategy, weight in self.strategy_weights.items():
            print(f"  {strategy}: {weight:.3f}")

        print("\nTAUX DE SUCCÈS PAR ACTION:")
        for action, rate in sorted(stats['action_success_rate'].items(), key=lambda x: x[1], reverse=True):
            total = stats['total_actions'].get(action, 0)
            print(f"  {action}: {rate * 100:.1f}% (sur {total} tentatives)")

        if len(stats['learning_progress']) >= 2:
            recent_winrate = stats['learning_progress'][-1]['win_rate']
            old_winrate = stats['learning_progress'][0]['win_rate']
            improvement = (recent_winrate - old_winrate) * 100
            print(f"\nPROGRÈS: {improvement:+.1f}% de taux de victoire")

        if 'evolution_history' in stats and stats['evolution_history']:
            print(f"\nÉVOLUTION RÉCENTE:")
            for entry in stats['evolution_history'][-3:]:
                gen = entry['generation']
                perf = entry['performance']
                print(f"  Génération {gen}: {perf['win_rate']:.1%} victoires, {perf['avg_score']:.1f} points")


def create_self_training_session(num_games=50):
    """Créer une session d'entraînement automatique"""
    print("=== SESSION D'ENTRAÎNEMENT AUTOMATIQUE ===")
    print(f"Nombre de parties: {num_games}")
    print("L'IA va jouer contre elle-même et évoluer...\n")

    # Cette fonction serait appelée depuis un script séparé
    # qui lance des parties automatiques
    pass