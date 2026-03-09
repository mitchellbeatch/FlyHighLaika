import pygame
import random
import string

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# --- Window ---
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guiding Laika")

clock = pygame.time.Clock()

FONT_SIZE = 18
font = pygame.font.SysFont("monospace", FONT_SIZE, bold=True)
ui_font = pygame.font.SysFont("monospace", 28, bold=True)
big_font = pygame.font.SysFont("monospace", 48, bold=True)

CHARS = string.ascii_letters + string.digits + "@#$%^&*()"

# --- Earth ---
home = pygame.image.load("assets/earth.png").convert_alpha()
home = pygame.transform.scale(home, (1000, 500))

# --- Load Spaceship ---
spaceship_img = pygame.image.load("assets/laikaship1.png").convert_alpha()
spaceship_img = pygame.transform.scale(spaceship_img, (80, 80))

# --- Explosion Setup ---
explosion_frames = []
for i in range(1, 7):
    img = pygame.image.load(f"assets/explosion{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (120, 120))
    explosion_frames.append(img)

exploding = False
explosion_index = 0
explosion_timer = 0
EXPLOSION_SPEED = 0.08
explosion_pos = (0, 0)

# --- Music ---
pygame.mixer.music.load("sounds/flyHighLaikaLoop.wav")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# --- Rain Setup ---
columns = WIDTH // FONT_SIZE

def create_drops():
    return [float(random.randint(-HEIGHT, 0)) for _ in range(columns)]

drops = create_drops()
RAIN_SPEED = 1.8

# --- Shield System ---
max_health = 100
health = max_health

# --- Level System ---
highScore = 0
LEVEL_DURATION = 15

def reset_game():
    global drops, RAIN_SPEED, level, level_timer, health, game_over
    global exploding, explosion_index, explosion_timer

    drops = create_drops()
    RAIN_SPEED = 1.8
    level = 1
    level_timer = LEVEL_DURATION
    health = max_health
    game_over = False

    exploding = False
    explosion_index = 0
    explosion_timer = 0

reset_game()

# --- Health Bar ---
def draw_health_bar(surface, x, y, width, height, health, max_health):
    pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)

    ratio = max(0, health / max_health)
    fill_height = height * ratio

    if health > 60:
        color = (0, 255, 205)
    elif health > 30:
        color = (255, 195, 0)
    else:
        color = (255, 30, 0)

    pygame.draw.rect(
        surface,
        color,
        (x, y + height - fill_height, width, fill_height)
    )

running = True

while running:
    dt = clock.tick(60) / 1000
    screen.fill((5, 1, 9))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    ship_rect = spaceship_img.get_rect(center=(mouse_x, mouse_y))

    # --- Level Timer ---
    if not game_over and not exploding:
        level_timer -= dt
        if level_timer <= 0:
            level += 1
            level_timer = LEVEL_DURATION
            RAIN_SPEED += 0.8

    # --- Earth ---
    if level < 2:
        y = drops[i] +HEIGHT+150
        screen.blit(home, (0, y))

    # --- Rain ---
    for i in range(columns):
        char = random.choice(CHARS)

        color = (
            max(0, min(255, 100 + random.randint(-90, 40))),
            max(0, min(255, 255 + random.randint(-100, 0))),
            max(0, min(255, 230 + random.randint(-100, 15)))
        )

        text = font.render(char, True, color)
        x = i * FONT_SIZE
        y = drops[i]

        screen.blit(text, (x, y))

        if not game_over and not exploding:
            if ship_rect.collidepoint(x, y):
                health -= 0.5

        drops[i] += RAIN_SPEED
        if drops[i] > HEIGHT:
            drops[i] = random.randint(-100, 0)

    # --- Trigger Explosion ---
    if health <= 0 and not exploding and not game_over:
        exploding = True
        explosion_pos = ship_rect.center

    # --- Draw Ship ---
    if not exploding and not game_over:
        screen.blit(spaceship_img, ship_rect)

    # --- Explosion Animation ---
    if exploding:
        explosion_timer += dt
        if explosion_timer >= EXPLOSION_SPEED:
            explosion_timer = 0
            explosion_index += 1

            if explosion_index >= len(explosion_frames):
                exploding = False
                game_over = True
                explosion_index = 0
                if level > highScore:
                    highScore = level

        frame = explosion_frames[explosion_index]
        rect = frame.get_rect(center=explosion_pos)
        screen.blit(frame, rect)

    # --- Shield Bar ---
    draw_health_bar(screen, WIDTH - 40, 50, 20, 200, health, max_health)

    # --- UI ---
    timer_text = ui_font.render(
        f"Level {level} | Time: {int(level_timer)}",
        True,
        (200, 200, 200),
    )
    screen.blit(timer_text, (WIDTH - 350, 20))

    high_score_text = ui_font.render(
        f"High Score: {highScore}",
        True,
        (200, 200, 200),
    )
    screen.blit(high_score_text, (WIDTH - 350, 70))

    # --- Game Over Screen ---
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_text = big_font.render(
            "FLY HIGH LAIKA",
            True,
            (230, 90, 90),
        )
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

        if level >= highScore:
            score_text = ui_font.render(f"New High Score: {level}", True, (210, 80, 100))
        else:
            score_text = ui_font.render(f"Final Score: {level}", True, (210, 80, 100))

        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))

        button_rect = pygame.Rect(0, 0, 200, 50)
        button_rect.center = (WIDTH // 2, HEIGHT // 2 + 60)

        pygame.draw.rect(screen, (150, 150, 150), button_rect, 2)

        button_text = ui_font.render("PLAY AGAIN", True, (210, 80, 120))
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))

    pygame.display.flip()

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        pygame.mouse.set_visible(game_over)
        if game_over:
                RAIN_SPEED = .5
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                reset_game()

pygame.quit()