import pygame
import random

pygame.init()

# ------------------ SETTINGS ------------------
WIDTH, HEIGHT = 420, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube Runner - Juice & Health")
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
GREEN = (0, 200, 100)

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
    player = {"x": LANES[lane_index], "y": GROUND_Y, "vy": 0, "jumping": False, "lane": lane_index}
    return (
        player, [], 0, 0,      # spawn_timer, score
        0, 0,                  # wall_cd, fake_cd
        False, 0, 0,           # boss_mode, boss_timer, boss_phase
        False,                 # boss_done
        0, 0, 0,               # shake_timer, shake_intensity, flash_timer
        4, 4, 0,               # health, max_health, last_heal_score
        0, 0                   # invuln_timer, slow_timer
    )

player, obstacles, spawn_timer, score, wall_cd, fake_cd, \
boss_mode, boss_timer, boss_phase, boss_done, \
shake_timer, shake_intensity, flash_timer, \
health, max_health, last_heal_score, \
invuln_timer, slow_timer = reset_game()

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
            if event.key == pygame.K_UP and not player["jumping"]:
                player["vy"] = JUMP_FORCE
                player["jumping"] = True
        elif game_state == GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player, obstacles, spawn_timer, score, wall_cd, fake_cd, \
                boss_mode, boss_timer, boss_phase, boss_done, \
                shake_timer, shake_intensity, flash_timer, \
                health, max_health, last_heal_score, \
                invuln_timer, slow_timer = reset_game()
                game_state = PLAYING
            elif event.key == pygame.K_ESCAPE:
                running = False

    if game_state == PLAYING:
        difficulty = score // 1000

        # -------- PLAYER --------
        target_x = LANES[player["lane"]]
        player["x"] += (target_x - player["x"]) * 0.25
        player["vy"] += GRAVITY
        player["y"] += player["vy"]
        if player["y"] >= GROUND_Y:
            player["y"] = GROUND_Y
            player["vy"] = 0
            player["jumping"] = False
        player_rect = pygame.Rect(player["x"] - PLAYER_SIZE // 2, player["y"], PLAYER_SIZE, PLAYER_SIZE)

        # -------- BOSS TRIGGER --------
        if score >= 5000 and not boss_mode and not boss_done:
            boss_mode = True
            boss_timer = 0
            boss_phase = 0
            obstacles.clear()

        # -------- SPAWN --------
        spawn_timer += 1
        spawn_delay = max(18, 40 - difficulty * 3)

        if boss_mode:
            boss_timer += 1
            if boss_timer % 40 == 0:
                boss_phase += 1
                shake_timer = 10
                shake_intensity = 8
                flash_timer = 6
                # Pattern 1
                if boss_phase % 3 == 0:
                    gap = random.randint(0, LANE_COUNT - 1)
                    for lane in range(LANE_COUNT):
                        if lane != gap:
                            x = LANES[lane]
                            obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT), "type": "wall"})
                # Pattern 2
                elif boss_phase % 3 == 1:
                    for i in range(3):
                        lane = (i + boss_phase) % LANE_COUNT
                        x = LANES[lane]
                        obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT - i*80, OB_WIDTH, OB_HEIGHT), "type": "normal"})
                # Pattern 3
                else:
                    safe = random.randint(0, LANE_COUNT - 1)
                    for lane in range(LANE_COUNT):
                        if lane != safe:
                            x = LANES[lane]
                            obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT), "type": "fake"})
                    for lane in range(LANE_COUNT):
                        x = LANES[lane]
                        obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT - 120, OB_WIDTH, OB_HEIGHT), "type": "wall"})
            if boss_timer > 800:
                boss_mode = False
                boss_done = True
                boss_timer = 0
                boss_phase = 0

        elif spawn_timer > spawn_delay:
            r = random.random()
            spawn_type = "normal"
            if difficulty >= 2 and r < 0.08 and wall_cd == 0:
                spawn_type = "wall"
                wall_cd = 2
            elif score > 3000 and r < 0.18 and fake_cd == 0:
                spawn_type = "fake_gap"
                fake_cd = 2
            elif difficulty >= 1 and r < 0.12:
                spawn_type = "moving"

            if wall_cd > 0: wall_cd -= 1
            if fake_cd > 0: fake_cd -= 1

            if spawn_type == "wall":
                for lane in range(LANE_COUNT):
                    x = LANES[lane]
                    obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT), "type": "wall"})
            elif spawn_type == "fake_gap":
                safe = random.randint(0, LANE_COUNT - 1)
                for lane in range(LANE_COUNT):
                    if lane != safe:
                        x = LANES[lane]
                        obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT), "type": "fake"})
                for lane in range(LANE_COUNT):
                    x = LANES[lane]
                    obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT - 120, OB_WIDTH, OB_HEIGHT), "type": "wall"})
            elif spawn_type == "moving":
                lane = random.randint(0, LANE_COUNT - 1)
                x = LANES[lane]
                obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT), "type": "moving", "dir": random.choice([-1,1])})
            else:
                lane = random.randint(0, LANE_COUNT - 1)
                x = LANES[lane]
                obstacles.append({"rect": pygame.Rect(x - OB_WIDTH//2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT), "type": "normal"})
            spawn_timer = 0

        # -------- MOVE OBSTACLES --------
        if slow_timer > 0:
            speed = BASE_SPEED
            slow_timer -= 1
        else:
            speed = BASE_SPEED + difficulty * 1.2

        for ob in obstacles:
            ob["rect"].y += speed
            if ob.get("type") == "moving":
                ob["rect"].x += ob["dir"] * 3
                if ob["rect"].left < 0 or ob["rect"].right > WIDTH:
                    ob["dir"] *= -1
        obstacles = [ob for ob in obstacles if ob["rect"].y < HEIGHT]

        # -------- COLLISION --------
        if invuln_timer > 0:
            invuln_timer -= 1

        for ob in obstacles:
            if player_rect.colliderect(ob["rect"]) and invuln_timer == 0:

                # ✅ JUMP TO AVOID DAMAGE
                if player["y"] < GROUND_Y - 25:
                    continue  # Player jumped over it

                damage = 1 if ob["type"] != "wall" else 2
                health -= damage

                shake_timer = 15
                shake_intensity = 12
                flash_timer = 10
                invuln_timer = 30
                slow_timer = 60

                obstacles.remove(ob)

                if health <= 0:
                    game_state = GAME_OVER
                break

        # -------- SCORE & HEALTH REGEN --------
        score += 1
        if score - last_heal_score >= 400:
            if health < max_health:
                health += 0.2
            last_heal_score = score

        # -------- SCREEN SHAKE --------
        offset_x, offset_y = 0, 0
        if shake_timer > 0:
            offset_x = random.randint(-shake_intensity, shake_intensity)
            offset_y = random.randint(-shake_intensity, shake_intensity)
            shake_timer -= 1

        # -------- DRAW --------
        screen.fill(WHITE)
        for lane_x in LANES:
            pygame.draw.line(screen, (200,200,200),(lane_x+offset_x,0+offset_y),(lane_x+offset_x,HEIGHT+offset_y),1)

        # Player blink if invincible
        if invuln_timer % 6 < 3:
            pygame.draw.rect(screen, BLUE, player_rect.move(offset_x, offset_y))

        for ob in obstacles:
            color = RED
            if ob["type"] == "wall": color = PURPLE
            elif ob["type"] == "fake": color = ORANGE
            elif ob["type"] == "moving": color = GREEN
            pygame.draw.rect(screen, color, ob["rect"].move(offset_x, offset_y))

        # Score / Level
        screen.blit(FONT.render(f"Score: {score}", True, BLACK), (10,10))
        screen.blit(FONT.render(f"Level: {difficulty}", True, BLACK), (10,35))
        if boss_mode:
            screen.blit(FONT.render("BOSS MODE!", True, (200,0,0)), (WIDTH//2 - 60,10))

        # -------- HEALTH BAR --------
        bar_width = 120
        bar_height = 15
        x = WIDTH - bar_width - 10
        y = 10
        pygame.draw.rect(screen, (180,180,180), (x,y,bar_width,bar_height))
        fill_width = int((health/max_health)*bar_width)
        pygame.draw.rect(screen, RED, (x,y,fill_width,bar_height))
        pygame.draw.rect(screen, BLACK, (x,y,bar_width,bar_height),2)

        # -------- FLASH --------
        if flash_timer > 0:
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.fill((255,255,255))
            flash.set_alpha(120)
            screen.blit(flash,(0,0))
            flash_timer -=1

    else:
        screen.fill(WHITE)
        over = BIG_FONT.render("GAME OVER", True, BLACK)
        sc = FONT.render(f"Score: {score}", True, BLACK)
        rs = FONT.render("Press R to Restart", True, BLACK)
        screen.blit(over, (WIDTH//2 - over.get_width()//2, 250))
        screen.blit(sc, (WIDTH//2 - sc.get_width()//2, 320))
        screen.blit(rs, (WIDTH//2 - rs.get_width()//2, 360))

    pygame.display.flip()

pygame.quit()
