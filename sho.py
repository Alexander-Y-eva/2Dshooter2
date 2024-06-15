import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Shooter game by Alex Y")

# Font for Game Over
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)
        self.health = 100

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_d]:
            self.rect.x += 5
        if keys[pygame.K_w]:
            self.rect.y -= 5
        if keys[pygame.K_s]:
            self.rect.y += 5

        # Prevent the player from moving off screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 50)
        self.rect.y = random.randint(0, 50)
        self.health = 100
        self.attack_timer = 0

    def update(self):
        # Simple AI: move towards the player
        if self.rect.x < player.rect.x:
            self.rect.x += 1
        if self.rect.x > player.rect.x:
            self.rect.x -= 1
        if self.rect.y < player.rect.y:
            self.rect.y += 1
        if self.rect.y > player.rect.y:
            self.rect.y -= 1

        # Attack the player if close enough
        if self.rect.colliderect(player.rect) and self.attack_timer <= 0:
            player.health -= 10
            self.attack_timer = 30  # Cooldown for enemy attacks

        if self.attack_timer > 0:
            self.attack_timer -= 1

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        angle = math.atan2(target_y - y, target_x - x)
        self.speed_x = math.cos(angle) * 10
        self.speed_y = math.sin(angle) * 10

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Function to draw health bar
def draw_health_bar(surface, x, y, percentage, width=50, height=5):
    fill = (percentage / 100) * width
    border_color = BLACK
    fill_color = GREEN if percentage > 50 else RED

    border_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)

    pygame.draw.rect(surface, border_color, border_rect, 2)
    pygame.draw.rect(surface, fill_color, fill_rect)

# Function to display text
def display_text(surface, text, font, color, position):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=position)
    surface.blit(text_obj, text_rect)

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create enemies
def create_enemies(num_enemies):
    for _ in range(num_enemies):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

initial_enemies = 5
create_enemies(initial_enemies)

# Main game loop
running = True
game_over = False
you_win = False
round_number = 1
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not you_win:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y)
                all_sprites.add(bullet)
                bullets.add(bullet)
        elif event.type == pygame.MOUSEBUTTONDOWN and (game_over or you_win):
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                if game_over and restart_button.collidepoint(mouse_x, mouse_y):
                    # Restart the game
                    player.health = 100
                    player.rect.center = (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)  # Reset player position
                    for enemy in enemies:
                        enemy.kill()
                    for bullet in bullets:
                        bullet.kill()
                    create_enemies(initial_enemies)
                    game_over = False
                    round_number = 1
                elif you_win and next_round_button.collidepoint(mouse_x, mouse_y):
                    # Next round
                    for enemy in enemies:
                        enemy.kill()
                    for bullet in bullets:
                        bullet.kill()
                    round_number += 1
                    create_enemies(initial_enemies * round_number)
                    you_win = False

    if not game_over and not you_win:
        # Update
        all_sprites.update()

        # Check for bullet collisions with enemies
        for bullet in bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                enemy.health -= 10
                bullet.kill()
                if enemy.health <= 0:
                    enemy.kill()

        # Check if all enemies are dead
        if len(enemies) == 0:
            you_win = True

        # Check if player is dead
        if player.health <= 0:
            game_over = True

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Draw health bars
    draw_health_bar(screen, 10, 10, player.health)  # Player health bar at the top
    for enemy in enemies:
        draw_health_bar(screen, enemy.rect.centerx - 25, enemy.rect.y - 15, enemy.health, width=50, height=5)

    # Display Game Over screen
    if game_over:
        display_text(screen, "Game Over", font, RED, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50)
        pygame.draw.rect(screen, BLACK, restart_button)
        display_text(screen, "Restart", small_font, WHITE, restart_button.center)

    # Display You Win screen
    if you_win:
        display_text(screen, "You Win", font, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        next_round_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50)
        pygame.draw.rect(screen, BLACK, next_round_button)
        display_text(screen, "Next Round", small_font, WHITE, next_round_button.center)

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
