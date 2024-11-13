import pygame
import random
import time
import math

# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre de jeu
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("osu! Version - Cibles et Sliders Améliorés")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Paramètres de la cible et du piège
TARGET_APPEAR_DURATION = 1.5  # Durée avant que la cible disparaisse

# Score et erreurs
score = 0
errors = 0

# Police pour afficher le score et les erreurs
font = pygame.font.Font(None, 36)

# Variables pour gérer le slider
is_dragging_slider = False

# Classe pour les cibles
class Target:
    def __init__(self):
        self.radius = random.randint(30, 70)
        self.x = random.randint(self.radius, SCREEN_WIDTH - self.radius)
        self.y = random.randint(self.radius, SCREEN_HEIGHT - self.radius)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.spawn_time = time.time()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def is_clicked(self, mouse_pos):
        distance = math.sqrt((self.x - mouse_pos[0]) ** 2 + (self.y - mouse_pos[1]) ** 2)
        return distance <= self.radius

# Classe pour les sliders courbés
class CurvedSlider:
    def __init__(self):
        self.start_x, self.start_y = random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 100)
        self.end_x, self.end_y = random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 100)
        self.control_x, self.control_y = random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 100)
        self.radius = 20
        self.spawn_time = time.time()
        self.is_active = False

    def draw(self, screen):
        # Dessiner la courbe de Bézier entre les points de départ et d'arrivée
        points = self.bezier_curve_points()
        pygame.draw.lines(screen, BLUE, False, points, 5)
        # Dessiner le point de départ en cercle et le point d'arrivée en carré
        pygame.draw.circle(screen, GREEN if self.is_active else BLUE, (self.start_x, self.start_y), self.radius)
        pygame.draw.rect(screen, YELLOW, (self.end_x - self.radius, self.end_y - self.radius, self.radius * 2, self.radius * 2))

    def bezier_curve_points(self):
        points = []
        for t in range(0, 101):
            t /= 100
            x = (1 - t) ** 2 * self.start_x + 2 * (1 - t) * t * self.control_x + t ** 2 * self.end_x
            y = (1 - t) ** 2 * self.start_y + 2 * (1 - t) * t * self.control_y
            points.append((x, y))
        return points

    def is_clicked(self, mouse_pos):
        distance = math.sqrt((self.start_x - mouse_pos[0]) ** 2 + (self.start_y - mouse_pos[1]) ** 2)
        return distance <= self.radius

    def is_reached(self, mouse_pos):
        distance = math.sqrt((self.end_x - mouse_pos[0]) ** 2 + (self.end_y - mouse_pos[1]) ** 2)
        return distance <= self.radius

# Liste des cibles et sliders actifs
targets = []
sliders = []
object_spawn_time = time.time()

# Boucle principale du jeu
running = True
while running:
    screen.fill(BLACK)  # Fond noir

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            hit = False

            # Vérification des cibles
            for target in targets:
                if target.is_clicked(mouse_pos):
                    score += 1
                    targets.remove(target)
                    hit = True
                    break

            # Vérification des sliders
            if not hit:
                for slider in sliders:
                    if slider.is_clicked(mouse_pos):
                        slider.is_active = True
                        is_dragging_slider = True
                        hit = True
                        break

            # Si aucun hit sur cibles ou sliders, ajouter une erreur
            if not hit:
                errors += 1

        elif event.type == pygame.MOUSEBUTTONUP:
            # Arrêter le glissement du slider
            is_dragging_slider = False
            for slider in sliders:
                if slider.is_active:
                    slider.is_active = False
                    if not slider.is_reached(pygame.mouse.get_pos()):
                        errors += 1
                    else:
                        score += 1
                    sliders.remove(slider)
                    break

        elif event.type == pygame.MOUSEMOTION and is_dragging_slider:
            # Vérifier si le slider atteint la fin
            for slider in sliders:
                if slider.is_active and slider.is_reached(event.pos):
                    slider.is_active = False
                    sliders.remove(slider)
                    score += 1
                    is_dragging_slider = False
                    break

    # Apparition d'une nouvelle cible ou slider
    if time.time() - object_spawn_time >= TARGET_APPEAR_DURATION:
        if random.choice([True, False]):  # 50% de chance pour un cercle ou un slider
            targets.append(Target())
        else:
            sliders.append(CurvedSlider())
        object_spawn_time = time.time()

    # Affichage des cibles
    current_time = time.time()
    for target in targets[:]:
        if current_time - target.spawn_time >= TARGET_APPEAR_DURATION:
            targets.remove(target)
        else:
            target.draw(screen)

    # Affichage des sliders
    for slider in sliders[:]:
        if current_time - slider.spawn_time >= TARGET_APPEAR_DURATION * 2:
            sliders.remove(slider)
        else:
            slider.draw(screen)

    # Affichage du score et des erreurs
    score_text = font.render(f"Score: {score}", True, GREEN)
    error_text = font.render(f"Erreurs: {errors}", True, RED)
    screen.blit(score_text, (10, 10))
    screen.blit(error_text, (10, 50))

    # Rafraîchissement de l'écran
    pygame.display.flip()

# Quitter pygame
pygame.quit()
