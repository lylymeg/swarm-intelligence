import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Colony Foraging Simulation (Swarm Intelligence)")
clock = pygame.time.Clock()

# Couleurs (Thème Sombre & Néon)
DARK_BG = (12, 15, 22)
NEST_COLOR = (255, 150, 0)      # Orange doré pour la fourmilière
FOOD_COLOR = (0, 255, 157)      # Vert néon pour la nourriture
ANT_COLOR = (180, 190, 210)     # Gris clair pour les fourmis
TRAIL_COLOR = (255, 100, 50, 40)# Trace de phéromone
WHITE = (255, 255, 255)
GRAY = (120, 130, 150)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 15)

# Position de la fourmilière
nest = {"x": WIDTH // 2, "y": HEIGHT // 2, "radius": 22}

# Liste des sources de nourriture
foods = [
    {"x": 150, "y": 120, "amount": 500},
    {"x": 750, "y": 500, "amount": 500}
]

# Grille de phéromones (pour guider les fourmis vers la nourriture)
GRID_SCALE = 8
GRID_COLS = WIDTH // GRID_SCALE
GRID_ROWS = HEIGHT // GRID_SCALE
pheromone_grid = [[0.0 for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

class Ant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_food = False
        self.speed = 2.2
        self.patience = 0

    def update(self):
        # 1. Gestion des états (Cherche de la nourriture vs Retour au nid)
        if not self.has_food:
            # Chercher de la nourriture (sentir les phéromones ou errer)
            grid_c = int(self.x / GRID_SCALE)
            grid_r = int(self.y / GRID_SCALE)

            # Détection des phéromones voisines
            best_angle = self.angle
            max_phes = 0
            if 0 <= grid_c < GRID_COLS and 0 <= grid_r < GRID_ROWS:
                for da in [-0.5, 0.0, 0.5]:
                    test_a = self.angle + da
                    tc = int((self.x + math.cos(test_a) * 20) / GRID_SCALE)
                    tr = int((self.y + math.sin(test_a) * 20) / GRID_SCALE)
                    if 0 <= tc < GRID_COLS and 0 <= tr < GRID_ROWS:
                        if pheromone_grid[tc][tr] > max_phes:
                            max_phes = pheromone_grid[tc][tr]
                            best_angle = test_a

            self.angle = best_angle + random.uniform(-0.35, 0.35)
        else:
            # Rentrer directement vers la fourmilière
            dx = nest["x"] - self.x
            dy = nest["y"] - self.y
            target_angle = math.atan2(dy, dx)
            
            # Ajuster progressivement l'angle vers le nid
            angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += max(-0.15, min(0.15, angle_diff)) + random.uniform(-0.1, 0.1)

            # Déposer du phéromone en rentrant
            gc = int(self.x / GRID_SCALE)
            gr = int(self.y / GRID_SCALE)
            if 0 <= gc < GRID_COLS and 0 <= gr < GRID_ROWS:
                pheromone_grid[gc][gr] = min(100.0, pheromone_grid[gc][gr] + 15.0)

        # Mouvement
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Rebond sur les bords de l'écran
        if self.x < 20 or self.x > WIDTH - 20:
            self.angle = math.pi - self.angle
            self.x = max(20, min(WIDTH - 20, self.x))
        if self.y < 70 or self.y > HEIGHT - 20:
            self.angle = -self.angle
            self.y = max(70, min(HEIGHT - 20, self.y))

        # Vérifier si la fourmi atteint la fourmilière avec de la nourriture
        if self.has_food and math.hypot(self.x - nest["x"], self.y - nest["y"]) < nest["radius"]:
            self.has_food = False
            self.angle += math.pi  # Faire demi-tour

        # Vérifier si la fourmi atteint une source de nourriture
        for f in foods:
            if f["amount"] > 0 and math.hypot(self.x - f["x"], self.y - f["y"]) < 20:
                self.has_food = True
                f["amount"] -= 1
                self.angle += math.pi  # Faire demi-tour

ants = [Ant(nest["x"], nest["y"]) for _ in range(150)]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Clic gauche : Ajouter une nouvelle source de nourriture
            if mouse_pos[1] > 80:
                foods.append({"x": mouse_pos[0], "y": mouse_pos[1], "amount": 400})
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Réinitialiser la simulation
                foods = [{"x": 150, "y": 120, "amount": 500}, {"x": 750, "y": 500, "amount": 500}]
                pheromone_grid = [[0.0 for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

    # Évaporation progressive des phéromones
    for c in range(GRID_COLS):
        for r in range(GRID_ROWS):
            pheromone_grid[c][r] *= 0.985
            if pheromone_grid[c][r] < 0.1:
                pheromone_grid[c][r] = 0.0

    # Mise à jour des fourmis
    for ant in ants:
        ant.update()

    screen.fill(DARK_BG)

    # 1. Dessiner les traces de phéromones (autoroutes invisibles des fourmis)
    for c in range(GRID_COLS):
        for r in range(GRID_ROWS):
            if pheromone_grid[c][r] > 0.5:
                alpha = min(150, int(pheromone_grid[c][r] * 10))
                color_surf = pygame.Surface((GRID_SCALE, GRID_SCALE), pygame.SRCALPHA)
                color_surf.fill((255, 120, 50, alpha))
                screen.blit(color_surf, (c * GRID_SCALE, r * GRID_SCALE))

    # 2. Dessiner la Fourmilière (Nid)
    pygame.draw.circle(screen, NEST_COLOR, (nest["x"], nest["y"]), nest["radius"])
    pygame.draw.circle(screen, WHITE, (nest["x"], nest["y"]), nest["radius"], 2)

    # 3. Dessiner les sources de nourriture
    for f in foods:
        if f["amount"] > 0:
            sz = max(8, int(math.sqrt(f["amount"]) * 0.8))
            pygame.draw.circle(screen, FOOD_COLOR, (f["x"], f["y"]), sz)
            pygame.draw.circle(screen, WHITE, (f["x"], f["y"]), sz, 2)

    # 4. Dessiner les fourmis
    for ant in ants:
        color = FOOD_COLOR if ant.has_food else ANT_COLOR
        pygame.draw.circle(screen, color, (int(ant.x), int(ant.y)), 2)

    # 5. En-tête HUD et Instructions
    title_txt = font_medium.render("SIMULATION DE COLONIE DE FOURMIS (SWARM INTELLIGENCE)", True, WHITE)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 15))

    inst_txt = font_small.render("CLIC GAUCHE : Déposer de la nourriture | R : Réinitialiser la colonie", True, GRAY)
    screen.blit(inst_txt, (WIDTH // 2 - inst_txt.get_width() // 2, 45))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()