import pygame
import random
import time

# --- Initialisation ---
pygame.init()
TAILLE_CASE = 30
GRID_SIZE = 20
SCREEN_WIDTH = TAILLE_CASE * GRID_SIZE
SCREEN_HEIGHT = TAILLE_CASE * GRID_SIZE + 100  # espace pour UI
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bataille des Objectifs")  # titre modifié
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --- Couleurs ---
GRIS = (200, 200, 200)
BLEU = (0, 0, 255)
BLEU_CLAIR = (100, 100, 255)
ROUGE = (255, 0, 0)
ROUGE_CLAIR = (255, 100, 100)
VERT = (0, 255, 0)
JAUNE = (255, 255, 0)
ORANGE = (255, 165, 0)
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

# --- Classes ---
class Unit:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.pv = 2
        self.deplace = False
        self.attaquee_ce_tour = False
        self.objectifs_visites = set()

class Objectif:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type = type_  # 'mineur' ou 'majeur'

# --- Initialisation des unités ---
player_units = [Unit(0, random.randint(0, GRID_SIZE-1), 'player') for _ in range(5)]
enemy_units = [Unit(GRID_SIZE-1, random.randint(0, GRID_SIZE-1), 'enemy') for _ in range(5)]

# --- Initialisation des objectifs ---
objectifs = []
positions = set()
while len(objectifs) < 4:
    x = random.randint(GRID_SIZE//2-3, GRID_SIZE//2+3)
    y = random.randint(GRID_SIZE//2-3, GRID_SIZE//2+3)
    if (x, y) not in positions:
        positions.add((x, y))
        type_ = 'majeur' if len(objectifs) == 0 else 'mineur'
        objectifs.append(Objectif(x, y, type_))

# --- Scores ---
score_player = 0
score_enemy = 0
player_occupied_major = set()
player_occupied_minor = set()
enemy_occupied_major = set()
enemy_occupied_minor = set()

# --- Tour ---
tour = 'player'
selected_unit = None

# --- Fonctions ---
def draw_grid():
    screen.fill(NOIR)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x*TAILLE_CASE, y*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
            pygame.draw.rect(screen, GRIS, rect)
            pygame.draw.rect(screen, NOIR, rect, 1)
    # Dessin des objectifs
    for obj in objectifs:
        color = JAUNE if obj.type=='majeur' else ORANGE
        rect = pygame.Rect(obj.x*TAILLE_CASE, obj.y*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, VERT, rect, 2)
    # Dessin des unités
    for u in player_units:
        rect = pygame.Rect(u.x*TAILLE_CASE, u.y*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
        color = BLEU if u.deplace else BLEU_CLAIR
        pygame.draw.rect(screen, color, rect)
        if selected_unit == u:
            pygame.draw.rect(screen, VERT, rect, 3)
        text = font.render("U", True, BLANC)
        screen.blit(text, (u.x*TAILLE_CASE+10, u.y*TAILLE_CASE+5))
    for u in enemy_units:
        rect = pygame.Rect(u.x*TAILLE_CASE, u.y*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
        color = ROUGE if u.deplace else ROUGE_CLAIR
        pygame.draw.rect(screen, color, rect)
        text = font.render("U", True, BLANC)
        screen.blit(text, (u.x*TAILLE_CASE+10, u.y*TAILLE_CASE+5))
    # Interface
    pygame.draw.rect(screen, GRIS, (0, GRID_SIZE*TAILLE_CASE, SCREEN_WIDTH, 100))
    txt_tour = font.render(f"Tour: {tour.capitalize()}", True, NOIR)
    screen.blit(txt_tour, (10, GRID_SIZE*TAILLE_CASE + 10))
    txt_score = font.render(f"Joueur: {score_player}  Ennemi: {score_enemy}", True, NOIR)
    screen.blit(txt_score, (SCREEN_WIDTH//2 - 80, GRID_SIZE*TAILLE_CASE + 10))
    pygame.display.flip()

def unit_at(pos, team=None):
    x, y = pos
    for u in (player_units + enemy_units):
        if u.x == x and u.y == y and (team is None or u.team == team):
            return u
    return None

def move_unit(unit, x, y):
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and unit_at((x, y)) is None:
        unit.x = x
        unit.y = y
        unit.deplace = True
        check_objectif(unit)

def check_objectif(unit):
    global score_player, score_enemy
    for obj in objectifs:
        if unit.x == obj.x and unit.y == obj.y:
            if unit.team == 'player':
                if obj.type=='majeur' and (obj.x,obj.y) not in player_occupied_major:
                    score_player += 3
                    player_occupied_major.add((obj.x,obj.y))
                elif obj.type=='mineur' and (obj.x,obj.y) not in player_occupied_minor:
                    score_player += 1
                    player_occupied_minor.add((obj.x,obj.y))
            else:
                if obj.type=='majeur' and (obj.x,obj.y) not in enemy_occupied_major:
                    score_enemy += 3
                    enemy_occupied_major.add((obj.x,obj.y))
                elif obj.type=='mineur' and (obj.x,obj.y) not in enemy_occupied_minor:
                    score_enemy += 1
                    enemy_occupied_minor.add((obj.x,obj.y))

# --- Boucle principale ---
running = True
while running:
    draw_grid()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and tour == 'player':
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // TAILLE_CASE, my // TAILLE_CASE
            if event.button == 1:  # clic gauche
                u = unit_at((gx, gy), 'player')
                if u:
                    selected_unit = u
            elif event.button == 3:  # clic droit
                if selected_unit and not selected_unit.deplace:
                    target = unit_at((gx, gy), 'enemy')
                    if target and abs(target.x-selected_unit.x)<=1 and abs(target.y-selected_unit.y)<=1:
                        target.pv -= 1
                        selected_unit.deplace = True
                        if target.pv <=0:
                            enemy_units.remove(target)
                    else:
                        move_unit(selected_unit, gx, gy)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Fin de tour joueur
                for u in player_units:
                    u.deplace = False
                    u.attaquee_ce_tour = False
                tour = 'enemy'
    # --- IA ennemie simplifiée ---
    if tour == 'enemy':
        for u in enemy_units:
            if not u.deplace:
                # Attaque si unité voisine
                target = None
                for pu in player_units:
                    if abs(pu.x-u.x)<=1 and abs(pu.y-u.y)<=1:
                        target = pu
                        break
                if target:
                    target.pv -= 1
                    u.deplace = True
                    if target.pv <= 0:
                        player_units.remove(target)
                else:
                    # Déplacement aléatoire vers le centre
                    dx = GRID_SIZE//2 - u.x
                    dy = GRID_SIZE//2 - u.y
                    nx = u.x + (1 if dx>0 else -1 if dx<0 else 0)
                    ny = u.y + (1 if dy>0 else -1 if dy<0 else 0)
                    if unit_at((nx, ny)) is None:
                        u.x = nx
                        u.y = ny
                        u.deplace = True
                        check_objectif(u)
        for u in enemy_units:
            u.deplace = False
            u.attaquee_ce_tour = False
        tour = 'player'
    # --- Vérification victoire ---
    if score_player >=50 or not enemy_units:
        print("Victoire Joueur !")
        time.sleep(2)
        running = False
    elif score_enemy >=50 or not player_units:
        print("Victoire Ennemi !")
        time.sleep(2)
        running = False
    clock.tick(30)

pygame.quit()
