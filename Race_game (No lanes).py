import pygame
import random

pygame.init()

# ------------------ SETTINGS ------------------
WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube Runner")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 40)

# ------------------ COLORS ------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 255)

# ------------------ PLAYER ------------------
PLAYER_SIZE = 40
PLAYER_SPEED = 6

# ------------------ OBSTACLES ------------------
OB_WIDTH = 60
OB_HEIGHT = 30
OB_SPEED = 5

PLAYING = 0
GAME_OVER = 1


# ------------------ RESET ------------------
def reset_game():
    player = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2,
                         HEIGHT - PLAYER_SIZE - 20,
                         PLAYER_SIZE, PLAYER_SIZE)

    obstacles = []
    spawn_timer = 0
    score = 0

    return player, obstacles, spawn_timer, score


player, obstacles, spawn_timer, score = reset_game()
game_state = PLAYING


# ------------------ GAME LOOP ------------------
running = True
while running:
    clock.tick(60)

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player, obstacles, spawn_timer, score = reset_game()
                    game_state = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    running = False

    if game_state == PLAYING:

        # -------- INPUT --------
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player.x += PLAYER_SPEED

        # Keep inside screen
        if player.left < 0:
            player.left = 0
        if player.right > WIDTH:
            player.right = WIDTH

        # -------- SPAWN OBSTACLES --------
        spawn_timer += 1
        if spawn_timer > 40:
            x = random.randint(0, WIDTH - OB_WIDTH)
            obstacle = pygame.Rect(x, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT)
            obstacles.append(obstacle)
            spawn_timer = 0

        # -------- MOVE OBSTACLES --------
        for ob in obstacles:
            ob.y += OB_SPEED

        # -------- REMOVE OFFSCREEN --------
        obstacles = [ob for ob in obstacles if ob.y < HEIGHT]

        # -------- COLLISION --------
        for ob in obstacles:
            if player.colliderect(ob):
                game_state = GAME_OVER

        # -------- SCORE --------
        score += 1

        # Increase difficulty
        OB_SPEED = 5 + score // 500

        # -------- DRAW --------
        screen.fill(WHITE)

        pygame.draw.rect(screen, BLUE, player)

        for ob in obstacles:
            pygame.draw.rect(screen, RED, ob)

        score_text = FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

    else:
        screen.fill(WHITE)

        over_text = BIG_FONT.render("GAME OVER", True, BLACK)
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        restart_text = FONT.render("Press R to Restart", True, BLACK)

        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, 250))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 320))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 360))

    pygame.display.flip()

pygame.quit()
