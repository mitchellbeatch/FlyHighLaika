import asyncio
import pygame
import random
import string
import sys
import os

def resource_path(relative_path):
    filename = os.path.basename(relative_path)
    if os.path.exists(filename):
        return filename
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

async def main():
    try:
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        WIDTH, HEIGHT = 960, 640
        screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32, 0, 0)
        pygame.display.set_caption("Guiding Laika")
        clock = pygame.time.Clock()
        FONT_SIZE = 18
        font = pygame.font.Font(None, FONT_SIZE + 4)
        ui_font = pygame.font.Font(None, 32)
        big_font = pygame.font.Font(None, 52)
        CHARS = string.ascii_letters + string.digits + "@#$%^&*()"
        home = pygame.image.load(resource_path("assets/earth.png"))
        home = pygame.transform.scale(home, (960, 480))
        spaceship_img = pygame.image.load(resource_path("assets/laikaship1.png"))
        spaceship_img = pygame.transform.scale(spaceship_img, (80, 80))
        explosion_frames = []
        for i in range(1, 7):
            img = pygame.image.load(resource_path(f"assets/explosion{i}.png"))
            img = pygame.transform.scale(img, (120, 120))
            explosion_frames.append(img)
        explosion_sound = pygame.mixer.Sound(resource_path("sounds/explosion1.ogg"))
        explosion_sound.set_volume(0.7)
        music = pygame.mixer.Sound(resource_path("sounds/flyHighLaika.ogg"))
        music.set_volume(0.4)
        columns = WIDTH // FONT_SIZE
        def create_drops():
            return [float(random.randint(-HEIGHT, 0)) for _ in range(columns)]
        def draw_health_bar(surface, x, y, width, height, hp, max_hp):
            pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
            ratio = max(0, hp / max_hp)
            fill_height = height * ratio
            if hp > 60:
                color = (0, 255, 205)
            elif hp > 30:
                color = (255, 195, 0)
            else:
                color = (255, 30, 0)
            pygame.draw.rect(surface, color, (x, y + height - fill_height, width, fill_height))
        RAIN_SPEED = 1.8
        drops = create_drops()
        max_health = 100
        health = max_health
        highScore = 0
        LEVEL_DURATION = 15
        exploding = False
        explosion_index = 0
        explosion_timer = 0
        EXPLOSION_SPEED = 0.08
        explosion_pos = (0, 0)
        game_over = False
        level = 1
        level_timer = LEVEL_DURATION
        button_rect = pygame.Rect(0, 0, 200, 50)
        music_started = False
        running = True
        while running:
            dt = clock.tick(60) / 1000
            screen.fill((5, 1, 9))
            mouse_x, mouse_y = pygame.mouse.get_pos()
            ship_rect = spaceship_img.get_rect(center=(mouse_x, mouse_y))
            if not music_started:
                try:
                    music.play(-1)
                    music_started = True
                except:
                    pass
            if not game_over and not exploding:
                level_timer -= dt
                if level_timer <= 0:
                    level += 1
                    level_timer = LEVEL_DURATION
                    RAIN_SPEED += 0.8
            if level < 2:
                earth_y = HEIGHT + 100 + int(drops[0])
                screen.blit(home, (0, earth_y))
            for i in range(columns):
                char = random.choice(CHARS)
                color = (
                    max(0, min(255, 100 + random.randint(-90, 40))),
                    max(0, min(255, 255 + random.randint(-100, 0))),
                    max(0, min(255, 230 + random.randint(-100, 15)))
                )
                text = font.render(char, True, color)
                x = i * FONT_SIZE
                y = int(drops[i])
                screen.blit(text, (x, y))
                if not game_over and not exploding:
                    if ship_rect.collidepoint(x, y):
                        health -= 0.5
                drops[i] += RAIN_SPEED
                if drops[i] > HEIGHT:
                    drops[i] = random.randint(-100, 0)
            if health <= 0 and not exploding and not game_over:
                explosion_sound.play()
                exploding = True
                explosion_index = 0
                explosion_timer = 0
                explosion_pos = ship_rect.center
            if not exploding and not game_over:
                screen.blit(spaceship_img, ship_rect)
            if exploding:
                frame = explosion_frames[explosion_index]
                rect = frame.get_rect(center=explosion_pos)
                screen.blit(frame, rect)
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
            draw_health_bar(screen, WIDTH - 40, 50, 20, 200, health, max_health)
            timer_text = ui_font.render(f"Level {level} | Time: {int(level_timer)}", True, (200, 200, 200))
            screen.blit(timer_text, (WIDTH - 340, 20))
            high_score_text = ui_font.render(f"High Score: {highScore}", True, (200, 200, 200))
            screen.blit(high_score_text, (WIDTH - 340, 70))
            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                title_text = big_font.render("FLY HIGH LAIKA", True, (230, 90, 90))
                screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
                if level >= highScore:
                    score_text = ui_font.render(f"New High Score: {level}", True, (210, 80, 100))
                else:
                    score_text = ui_font.render(f"Final Score: {level}", True, (210, 80, 100))
                screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
                button_rect.center = (WIDTH // 2, HEIGHT // 2 + 60)
                pygame.draw.rect(screen, (150, 150, 150), button_rect, 2)
                button_text = ui_font.render("PLAY AGAIN", True, (210, 80, 120))
                screen.blit(button_text, button_text.get_rect(center=button_rect.center))
            pygame.display.flip()
            pygame.mouse.set_visible(game_over)
            if game_over:
                RAIN_SPEED = 0.5
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game_over and button_rect.collidepoint(event.pos):
                        drops = create_drops()
                        RAIN_SPEED = 1.8
                        level = 1
                        level_timer = LEVEL_DURATION
                        health = max_health
                        game_over = False
                        exploding = False
                        explosion_index = 0
                        explosion_timer = 0
            await asyncio.sleep(0)
    except Exception as e:
        import traceback
        print("CRASH:", e)
        traceback.print_exc()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            await asyncio.sleep(0)
    pygame.quit()

asyncio.run(main())
