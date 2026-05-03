import pygame
import random

pygame.init()

# ------------------ SETTINGS ------------------
WIDTH, HEIGHT = 420, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube Runner - Fake Gaps")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22)
BIG_FONT = pygame.font.SysFont("arial", 40)

# ------------------ COLORS ------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 120, 255)
PURPLE = (150, 0, 200)
ORANGE = (255, 140, 0)

# ------------------ LANES ------------------
LANE_COUNT = 6
LANES = [int((i + 0.5) * WIDTH / LANE_COUNT) for i in range(LANE_COUNT)]

# ------------------ PLAYER ------------------
PLAYER_SIZE = 35
GROUND_Y = HEIGHT - 100

GRAVITY = 0.8
JUMP_FORCE = -16

# ------------------ OBSTACLES ------------------
BASE_SPEED = 5
OB_WIDTH = 40
OB_HEIGHT = 40

PLAYING = 0
GAME_OVER = 1


# ------------------ RESET ------------------
def reset_game():
    lane_index = LANE_COUNT // 2

    player = {
        "x": LANES[lane_index],
        "y": GROUND_Y,
        "vy": 0,
        "jumping": False,
        "lane": lane_index
    }

    return player, [], 0, 0, 0, 0  # wall_cooldown, fake_cooldown


player, obstacles, spawn_timer, score, wall_cooldown, fake_cooldown = reset_game()
game_state = PLAYING


# ------------------ GAME LOOP ------------------
running = True
while running:
    clock.tick(60)

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == PLAYING and event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                player["lane"] = max(0, player["lane"] - 1)

            if event.key == pygame.K_RIGHT:
                player["lane"] = min(LANE_COUNT - 1, player["lane"] + 1)

            if event.key == pygame.K_UP:
                if not player["jumping"]:
                    player["vy"] = JUMP_FORCE
                    player["jumping"] = True

        elif game_state == GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player, obstacles, spawn_timer, score, wall_cooldown, fake_cooldown = reset_game()
                game_state = PLAYING
            elif event.key == pygame.K_ESCAPE:
                running = False

    if game_state == PLAYING:

        difficulty = score // 1000

        # -------- PLAYER MOVE --------
        target_x = LANES[player["lane"]]
        player["x"] += (target_x - player["x"]) * 0.25

        # -------- JUMP --------
        player["vy"] += GRAVITY
        player["y"] += player["vy"]

        if player["y"] >= GROUND_Y:
            player["y"] = GROUND_Y
            player["vy"] = 0
            player["jumping"] = False

        player_rect = pygame.Rect(
            player["x"] - PLAYER_SIZE // 2,
            player["y"],
            PLAYER_SIZE,
            PLAYER_SIZE
        )

        # -------- SPAWN --------
        spawn_timer += 1
        spawn_delay = max(18, 40 - difficulty * 3)

        if spawn_timer > spawn_delay:

            spawn_type = "normal"
            r = random.random()

            # WALL
            if difficulty >= 2 and r < 0.08 and wall_cooldown == 0:
                spawn_type = "wall"
                wall_cooldown = 2

            # FAKE GAP (with cooldown)
            elif score > 3000 and r < 0.18 and fake_cooldown == 0:
                spawn_type = "fake_gap"
                fake_cooldown = 2

            # reduce cooldowns
            if wall_cooldown > 0:
                wall_cooldown -= 1
            if fake_cooldown > 0:
                fake_cooldown -= 1

            # -------- CREATE OBSTACLES --------
            if spawn_type == "wall":
                for lane in range(LANE_COUNT):
                    x = LANES[lane]
                    obstacles.append({
                        "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                        "lane": lane,
                        "type": "wall"
                    })

            elif spawn_type == "fake_gap":
                safe_lane = random.randint(0, LANE_COUNT - 1)

                # fake row
                for lane in range(LANE_COUNT):
                    if lane != safe_lane:
                        x = LANES[lane]
                        obstacles.append({
                            "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                            "lane": lane,
                            "type": "fake"
                        })

                # real wall behind
                for lane in range(LANE_COUNT):
                    x = LANES[lane]
                    obstacles.append({
                        "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT - 120, OB_WIDTH, OB_HEIGHT),
                        "lane": lane,
                        "type": "wall"
                    })

            else:
                lane = random.randint(0, LANE_COUNT - 1)
                x = LANES[lane]

                obstacles.append({
                    "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                    "lane": lane,
                    "type": "normal"
                })

            spawn_timer = 0

        # -------- MOVE OBSTACLES --------
        speed = BASE_SPEED + difficulty * 1.2

        for ob in obstacles:
            ob["rect"].y += speed

        obstacles = [ob for ob in obstacles if ob["rect"].y < HEIGHT]

        # -------- COLLISION --------
        for ob in obstacles:
            if ob["lane"] == player["lane"]:
                if player_rect.colliderect(ob["rect"]):
                    if player["y"] > GROUND_Y - 30:
                        game_state = GAME_OVER

        score += 1

        # -------- DRAW --------
        screen.fill(WHITE)

        for lane_x in LANES:
            pygame.draw.line(screen, (200, 200, 200),
                             (lane_x, 0), (lane_x, HEIGHT), 1)

        pygame.draw.rect(screen, BLUE, player_rect)

        for ob in obstacles:
            color = RED
            if ob["type"] == "wall":
                color = PURPLE
            elif ob["type"] == "fake":
                color = ORANGE

            pygame.draw.rect(screen, color, ob["rect"])

        screen.blit(FONT.render(f"Score: {score}", True, BLACK), (10, 10))
        screen.blit(FONT.render(f"Level: {difficulty}", True, BLACK), (10, 35))

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
