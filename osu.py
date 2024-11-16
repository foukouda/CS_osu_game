import pygame
import sys
import os
import csv
import cv2
import numpy as np
import random

class RhythmGame:
    def __init__(self):
        # Initialiser Pygame
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Jeu de Rythme Simplifié")
        self.clock = pygame.time.Clock()

        # Charger les sons
        self.click_sound = pygame.mixer.Sound(os.path.join('data', 'OUI_OUI.mp3'))
        self.click_sound.set_volume(1.0)  # Volume maximal
        pygame.mixer.music.set_volume(0.5)  # Réglez selon vos préférences

        # Charger la vidéo de fond
        self.video_miawmiaw_path = os.path.join('data', 'background_miawmiaw.mp4')
        self.video_capture = None
        if os.path.exists(self.video_miawmiaw_path):
            self.video_capture = cv2.VideoCapture(self.video_miawmiaw_path)

        # Définir les couleurs
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (100, 100, 100)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        # Charger les musiques et leurs patterns
        self.songs = [
            {
                'name': 'APT',
                'music_file': os.path.join('data', 'APT.mp3'),
                'pattern': self.generate_random_pattern()
            },
            {
                'name': 'MiawMiaw',
                'music_file': os.path.join('data', 'MiawMiaw.mp3'),
                'pattern': self.generate_random_pattern(),
                'background_video': self.video_miawmiaw_path
            },
        ]

        # Définir les polices
        self.font_large = pygame.font.SysFont(None, 60)
        self.font_medium = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 30)

    def generate_random_pattern(self):
        """Génère un pattern aléatoire de cercles avec des positions aléatoires."""
        pattern = []
        for i in range(1, 6):
            x = random.randint(50, self.WIDTH - 50)
            y = random.randint(50, self.HEIGHT - 50)
            pattern.append((i * 1.0, x, y))
        return pattern

    def draw_text(self, text, font, color, x, y):
        """Fonction utilitaire pour dessiner du texte centré."""
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        self.screen.blit(text_obj, text_rect)

    def enter_player_name(self):
        """Affiche un écran pour entrer le nom du joueur."""
        name = ""
        entering_name = True
        while entering_name:
            self.screen.fill(self.BLACK)
            self.draw_text("Entrez votre nom : " + name, self.font_large, self.WHITE, self.WIDTH // 2, self.HEIGHT // 2)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        entering_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
        return name

    def main_menu(self):
        """Affiche le menu principal où le joueur peut choisir une musique."""
        menu_running = True
        while menu_running:
            self.screen.fill(self.BLACK)
            self.draw_text("Sélectionnez une Musique", self.font_large, self.WHITE, self.WIDTH // 2, 100)

            # Dessiner les boutons pour chaque musique
            button_width = 300
            button_height = 50
            button_spacing = 20
            total_buttons_height = len(self.songs) * (button_height + button_spacing)
            start_y = (self.HEIGHT - total_buttons_height) // 2

            mouse_pos = pygame.mouse.get_pos()

            for index, song in enumerate(self.songs):
                button_x = (self.WIDTH - button_width) // 2
                button_y = start_y + index * (button_height + button_spacing)
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

                # Changer la couleur du contour du bouton si la souris est dessus
                color = self.GRAY if button_rect.collidepoint(mouse_pos) else self.WHITE
                pygame.draw.rect(self.screen, color, button_rect, 2)

                # Dessiner le texte du bouton
                self.draw_text(song['name'], self.font_medium, self.WHITE, self.WIDTH // 2, button_y + button_height // 2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index, song in enumerate(self.songs):
                        button_x = (self.WIDTH - button_width) // 2
                        button_y = start_y + index * (button_height + button_spacing)
                        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                        if button_rect.collidepoint(event.pos):
                            selected_song = song
                            menu_running = False
                            player_name = self.enter_player_name()
                            self.game_loop(selected_song, player_name)

            pygame.display.flip()
            self.clock.tick(60)

    def game_loop(self, selected_song, player_name):
        """Boucle principale du jeu pour une musique sélectionnée."""
        # Charger la musique
        try:
            pygame.mixer.music.load(selected_song['music_file'])
        except pygame.error as e:
            print(f"Erreur de chargement de la musique: {e}")
            return

        pygame.mixer.music.play()
        start_time = pygame.time.get_ticks()
        circle_index = 0
        total_circles = len(selected_song['pattern'])
        circle_active = False
        circle_display_time = 500  # Durée d'affichage du cercle en millisecondes
        circle_start_time = 0
        current_circle_pos = (0, 0)

        # Limiter la durée du jeu à 30 secondes
        game_duration = 30000  # en millisecondes

        # Variables pour les statistiques
        sum_precision = 0
        hits = 0
        misses = 0
        bad_clicks = 0

        # Rayon du cercle
        RADIUS = 30

        # Liste pour les animations
        animations = []

        # Flag pour indiquer si le cercle a été cliqué
        circle_clicked = False

        # Définir l'état de pause
        paused = False

        game_running = True

        while game_running:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if circle_active and not circle_clicked:
                        x, y = current_circle_pos
                        distance = ((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2) ** 0.5
                        if distance <= RADIUS:
                            precision = max(0, 100 - (distance / RADIUS) * 100)
                            sum_precision += precision
                            hits += 1
                            circle_clicked = True

                            # Déterminer la couleur de l'animation
                            if precision >= 80:
                                animation_color = self.GREEN
                            elif precision >= 50:
                                animation_color = self.BLUE
                            else:
                                animation_color = self.RED

                            # Jouer le son de clic
                            self.click_sound.play()

                            # Ajouter une animation à l'endroit du clic
                            animations.append(ClickAnimation((x, y), animation_color))
                        else:
                            bad_clicks += 1
                    else:
                        bad_clicks += 1

            if not paused:
                # Lire la vidéo de fond si présent
                if 'background_video' in selected_song and self.video_capture is not None:
                    ret, frame = self.video_capture.read()
                    if not ret:
                        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.video_capture.read()
                    frame = cv2.resize(frame, (self.WIDTH, self.HEIGHT))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = np.rot90(frame)
                    frame_surface = pygame.surfarray.make_surface(frame)
                    self.screen.blit(frame_surface, (0, 0))

                # Afficher les cercles au bon moment
                if circle_index < total_circles and elapsed_time >= selected_song['pattern'][circle_index][0] * 1000:
                    x, y = selected_song['pattern'][circle_index][1], selected_song['pattern'][circle_index][2]
                    current_circle_pos = (x, y)
                    circle_active = True
                    circle_start_time = current_time
                    circle_clicked = False
                    circle_index += 1

                # Afficher le cercle s'il est actif avec un contour blanc
                if circle_active:
                    if current_time - circle_start_time <= circle_display_time:
                        pygame.draw.circle(self.screen, self.WHITE, current_circle_pos, RADIUS + 2, 2)
                        pygame.draw.circle(self.screen, self.RED, current_circle_pos, RADIUS)
                    else:
                        circle_active = False
                        if not circle_clicked:
                            misses += 1

                # Mettre à jour et dessiner les animations
                for animation in animations[:]:
                    animation.update()
                    animation.draw(self.screen)
                    if animation.is_finished():
                        animations.remove(animation)

                # Afficher les statistiques en temps réel
                score_text = self.font_small.render(f"Hits: {hits}", True, self.WHITE)
                misses_text = self.font_small.render(f"Misses: {misses}", True, self.WHITE)
                bad_clicks_text = self.font_small.render(f"Bad Clicks: {bad_clicks}", True, self.WHITE)
                if hits > 0:
                    average_precision = sum_precision / hits
                else:
                    average_precision = 0
                precision_text = self.font_small.render(f"Précision Moyenne: {average_precision:.2f}%", True, self.WHITE)

                self.screen.blit(score_text, (10, 10))
                self.screen.blit(misses_text, (10, 40))
                self.screen.blit(bad_clicks_text, (10, 70))
                self.screen.blit(precision_text, (10, 100))

                pause_info_text = self.font_small.render("Appuyez sur 'P' pour mettre en pause", True, self.WHITE)
                self.screen.blit(pause_info_text, (self.WIDTH - pause_info_text.get_width() - 10, 10))

            else:
                # Afficher l'écran de pause
                self.screen.fill(self.GRAY)
                font = pygame.font.Font(None, 74)
                pause_text = font.render("Pause", True, self.BLACK)
                self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, self.HEIGHT // 2 - pause_text.get_height() // 2))

            pygame.display.flip()
            self.clock.tick(60)

            # Arrêter le jeu après la durée définie ou si la musique est terminée
            if elapsed_time >= game_duration or not pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                if self.video_capture is not None:
                    self.video_capture.release()
                game_running = False
                self.end_screen(player_name, hits, misses, bad_clicks, average_precision, total_circles)

    def end_screen(self, player_name, hits, misses, bad_clicks, average_precision, total_circles):
        """Affiche l'écran de fin avec le score et la précision."""
        # Calculer la précision globale en tenant compte des bad clicks et des misses
        total_possible_hits = total_circles
        accuracy = (hits / total_possible_hits) * 100 if total_possible_hits > 0 else 0

        # Enregistrer les résultats dans un fichier CSV
        with open('game_results.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([player_name, hits, misses, bad_clicks, average_precision, accuracy])

        # Récupérer le meilleur joueur
        best_player = self.get_best_player()

        end_running = True
        while end_running:
            self.screen.fill(self.BLACK)
            self.draw_text("Résultats", self.font_large, self.WHITE, self.WIDTH // 2, 150)
            self.draw_text(f"Hits: {hits}", self.font_medium, self.WHITE, self.WIDTH // 2, 250)
            self.draw_text(f"Misses: {misses}", self.font_medium, self.WHITE, self.WIDTH // 2, 320)
            self.draw_text(f"Bad Clicks: {bad_clicks}", self.font_medium, self.WHITE, self.WIDTH // 2, 390)
            self.draw_text(f"Précision Moyenne: {average_precision:.2f}%", self.font_medium, self.WHITE, self.WIDTH // 2, 460)
            self.draw_text(f"Accuracy: {accuracy:.2f}%", self.font_medium, self.WHITE, self.WIDTH // 2, 530)
            self.draw_text("Appuyez pour retourner au menu", self.font_small, self.WHITE, self.WIDTH // 2, self.HEIGHT - 50)

            if best_player:
                best_player_text = f"Meilleur Joueur: {best_player[0]} avec {best_player[1]:.2f}% de précision"
                self.draw_text(best_player_text, self.font_small, self.WHITE, self.WIDTH // 2, self.HEIGHT - 100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    end_running = False

            pygame.display.flip()
            self.clock.tick(60)

    def get_best_player(self):
        """Récupère le meilleur joueur à partir du fichier CSV."""
        best_player = None
        best_accuracy = 0

        if os.path.exists('game_results.csv'):
            with open('game_results.csv', mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    player_name, hits, misses, bad_clicks, avg_precision, accuracy = row
                    accuracy = float(accuracy)
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_player = (player_name, accuracy)

        return best_player

    def main(self):
        # Créer un fichier CSV si celui-ci n'existe pas encore
        if not os.path.exists('game_results.csv'):
            with open('game_results.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Nom du Joueur", "Hits", "Misses", "Bad Clicks", "Précision Moyenne", "Accuracy"])

        while True:
            self.main_menu()

class ClickAnimation:
    """Classe pour gérer les animations de clic."""
    def __init__(self, position, color):
        self.position = position
        self.current_radius = 30  # Rayon initial (même que le cercle cliqué)
        self.max_radius = 60      # Rayon maximum de l'animation
        self.speed = 2            # Vitesse d'expansion par frame
        self.alpha = 255          # Opacité initiale
        self.color = color        # Couleur de l'animation

        # Créer une surface transparente pour dessiner l'animation
        self.surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.surface.get_rect(center=position)

    def update(self):
        """Mettre à jour l'état de l'animation."""
        self.current_radius += self.speed
        self.alpha -= 5
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, surface):
        """Dessiner l'animation sur la surface principale."""
        if self.current_radius <= self.max_radius:
            pygame.draw.circle(
                self.surface,
                (self.color[0], self.color[1], self.color[2], self.alpha),
                (self.max_radius, self.max_radius),
                self.current_radius,
                2
            )
            surface.blit(self.surface, self.rect)

    def is_finished(self):
        """Vérifier si l'animation est terminée."""
        return self.current_radius > self.max_radius or self.alpha <= 0

if __name__ == "__main__":
    game = RhythmGame()
    game.main()
