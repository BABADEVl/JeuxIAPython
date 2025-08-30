import pygame
import random
import time
import heapq

# --- Initialisation ---
pygame.init()
CELL_SIZE = 30
GRID_SIZE = 20
UI_HEIGHT = 100
WIDTH = CELL_SIZE * GRID_SIZE
HEIGHT = CELL_SIZE * GRID_SIZE + UI_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bataille des Objectifs")
clock = pygame.time.Clock()

# --- Couleurs ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (200, 200, 200)
BLUE = (0, 0, 255)
LIGHT_BLUE = (100, 100, 255)
RED = (255, 0, 0)
LIGHT_RED = (255, 100, 100)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# --- Classes ---
class Unit:
    def __init__(self, x, y, color, faction):
        self.x = x
        self.y = y
        self.color = color
        self.faction = faction
        self.pv = 2
        self.moved = False
        self.attacked_this_turn = False
        self.visited_objectives = []

    def rect(self):
        return pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

# --- Création des unités ---
player_units = [Unit(0, random.randint(0, GRID_SIZE-1), BLUE, "player") for _ in range(5)]
enemy_units = [Unit(GRID_SIZE-1, random.randint(0, GRID_SIZE-1), RED, "enemy") for _ in range(5)]
all_units = player_units + enemy_units

# --- Objectifs ---
objectives = []
center_zone = range(GRID_SIZE//2 - 3, GRID_SIZE//2 + 4)
while len(objectives) < 4:
    x, y = random.choice(center_zone), random.choice(center_zone)
    if (x,y) not in [(o[0], o[1]) for o in objectives]:
        if len(objectives) == 0:
            objectives.append((x,y,"major"))
        else:
            objectives.append((x,y,"minor"))

# --- Scores ---
player_score, enemy_score = 0, 0
player_objectives = set()
enemy_objectives = set()

# --- Sélection ---
selected_unit = None
turn = "player"
font = pygame.font.SysFont(None, 24)

# --- Fonctions ---
def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, LIGHT_GREY, rect, 1)

def draw_units():
    for unit in all_units:
        color = unit.color
        if unit.faction == "player":
            color = LIGHT_BLUE if not unit.moved else BLUE
        else:
            color = LIGHT_RED if not unit.moved else RED
        pygame.draw.rect(screen, color, unit.rect())
        if selected_unit == unit:
            pygame.draw.rect(screen, GREEN, unit.rect(), 3)

def draw_objectives():
    for x, y, typ in objectives:
        col = YELLOW if typ == "major" else ORANGE
        pygame.draw.rect(screen, col, (x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))

def draw_ui():
    global turn, player_score, enemy_score
    pygame.draw.rect(screen, BLACK, (0, GRID_SIZE*CELL_SIZE, WIDTH, UI_HEIGHT))
    # Texte
    txt = font.render(f"Tour: {turn}", True, WHITE)
    screen.blit(txt, (10, GRID_SIZE*CELL_SIZE+10))
    ps = font.render(f"Score Joueur: {player_score}", True, WHITE)
    screen.blit(ps, (10, GRID_SIZE*CELL_SIZE+40))
    es = font.render(f"Score Ennemi: {enemy_score}", True, WHITE)
    screen.blit(es, (WIDTH-200, GRID_SIZE*CELL_SIZE+40))
    # Bouton Terminé
    pygame.draw.rect(screen, LIGHT_GREY, (WIDTH//2-50, GRID_SIZE*CELL_SIZE+30, 100, 40))
    bt = font.render("Terminé", True, BLACK)
    screen.blit(bt, (WIDTH//2-30, GRID_SIZE*CELL_SIZE+40))

def get_unit_at(x,y,faction=None):
    for u in all_units:
        if u.x == x and u.y == y:
            if faction is None or u.faction == faction:
                return u
    return None

def neighbors(x,y):
    return [(x+dx,y+dy) for dx in [-1,0,1] for dy in [-1,0,1] if not (dx==0 and dy==0)]

def is_valid(x,y):
    return 0<=x<GRID_SIZE and 0<=y<GRID_SIZE and get_unit_at(x,y) is None

def attack(attacker,target):
    if target.attacked_this_turn:
        target.pv -= 1
    target.attacked_this_turn = True
    if target.pv <= 0:
        all_units.remove(target)
        if target in player_units: player_units.remove(target)
        if target in enemy_units: enemy_units.remove(target)
    else:
        dx, dy = target.x - attacker.x, target.y - attacker.y
        newx, newy = target.x+dx, target.y+dy
        if not is_valid(newx,newy):
            all_units.remove(target)
            if target in player_units: player_units.remove(target)
            if target in enemy_units: enemy_units.remove(target)
        else:
            target.x, target.y = newx, newy
    attacker.moved = True

def distance(a,b):
    return abs(a[0]-b[0])+abs(a[1]-b[1])

def ai_turn():
    global turn, enemy_score
    for unit in enemy_units:
        if unit.moved: continue
        # 1. Attaquer si possible
        for nx,ny in neighbors(unit.x, unit.y):
            target = get_unit_at(nx,ny,"player")
            if target:
                attack(unit,target)
                break
        else:
            # 2. Aller vers objectif ou joueur
            goals = [(x,y) for x,y,t in objectives] + [(u.x,u.y) for u in player_units]
            goals.sort(key=lambda g: distance((unit.x,unit.y), g))
            if goals:
                gx,gy = goals[0]
                best = None
                bestd = 999
                for nx,ny in neighbors(unit.x,unit.y):
                    if is_valid(nx,ny):
                        d = distance((nx,ny),(gx,gy))
                        if d < bestd or (d==bestd and random.random()<0.3):
                            best = (nx,ny)
                            bestd = d
                if best:
                    unit.x, unit.y = best
                    unit.moved = True
        update_scores()
        draw()
        pygame.display.flip()
        pygame.time.wait(500)
    for u in enemy_units:
        u.moved=False
    for u in all_units:
        u.attacked_this_turn=False
    turn = "player"

def update_scores():
    global player_score, enemy_score
    for unit in player_units:
        for ox,oy,typ in objectives:
            if unit.x==ox and unit.y==oy:
                if (ox,oy) not in unit.visited_objectives:
                    unit.visited_objectives.append((ox,oy))
                    if typ=="major": player_score+=3
                    else: player_score+=1
    for unit in enemy_units:
        for ox,oy,typ in objectives:
            if unit.x==ox and unit.y==oy:
                if (ox,oy) not in unit.visited_objectives:
                    unit.visited_objectives.append((ox,oy))
                    if typ=="major": enemy_score+=3
                    else: enemy_score+=1

def draw():
    screen.fill(BLACK)
    draw_grid()
    draw_objectives()
    draw_units()
    draw_ui()

# --- Boucle principale ---
running=True
while running:
    draw()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            if my < GRID_SIZE*CELL_SIZE: # zone de jeu
                gx,gy = mx//CELL_SIZE, my//CELL_SIZE
                if event.button==1: # clic gauche
                    unit = get_unit_at(gx,gy,"player")
                    if unit:
                        selected_unit = unit
                elif event.button==3 and selected_unit and not selected_unit.moved:
                    target = get_unit_at(gx,gy,"enemy")
                    if target and abs(target.x-selected_unit.x)<=1 and abs(target.y-selected_unit.y)<=1:
                        attack(selected_unit,target)
                    elif is_valid(gx,gy) and abs(gx-selected_unit.x)<=1 and abs(gy-selected_unit.y)<=1:
                        selected_unit.x, selected_unit.y = gx,gy
                        selected_unit.moved=True
                    update_scores()
            else: # zone UI
                if WIDTH//2-50 <= mx <= WIDTH//2+50 and GRID_SIZE*CELL_SIZE+30 <= my <= GRID_SIZE*CELL_SIZE+70:
                    if turn=="player":
                        for u in player_units: u.moved=False
                        for u in all_units: u.attacked_this_turn=False
                        turn="enemy"
                        ai_turn()
pygame.quit()
