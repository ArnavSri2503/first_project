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
BLACK = (10, 10, 20)
WHITE = (245, 245, 245)
RED = (220, 50, 50)
BLUE = (50, 140, 255)
PURPLE = (150, 0, 200)
ORANGE = (255, 140, 0)
GREEN = (0, 200, 100)

# ------------------ LANES ------------------
LANE_COUNT = 6
LANES = [int((i + 0.5) * WIDTH / LANE_COUNT) for i in range(LANE_COUNT)]

# ------------------ PARTICLES ------------------
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.dx = random.uniform(-5, 5)
        self.dy = random.uniform(-5, 5)
        self.life = random.randint(20, 40)
        self.size = random.randint(2, 6)
        self.color = color

    def update(self, speed=1.0):
        self.x += self.dx * speed
        self.y += self.dy * speed
        self.life -= 1
        self.size *= 0.9

    def draw(self, screen, off):
        if self.life > 0 and self.size > 0:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x + off[0]), int(self.y + off[1])),
                int(self.size)
            )

particles = []

# ⭐ STAR BACKGROUND
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)] for _ in range(80)]

# ------------------ PLAYER ------------------
PLAYER_SIZE = 35
GROUND_Y = HEIGHT - 100
GRAVITY = 0.8
JUMP_FORCE = -16

# ------------------ GAME ------------------
BASE_SPEED = 5

PLAYING = 0
GAME_OVER = 1

paused = False  # ⏸ PAUSE STATE

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

    return (
        player, [], 0, 0,
        0, 0,
        False, 0, 0,
        False,
        0, 0, 0,
        4, 4, 0,
        0, 0
    )

player, obstacles, spawn_timer, score, wall_cd, fake_cd, \
boss_mode, boss_timer, boss_phase, boss_done, \
shake_timer, shake_intensity, flash_timer, \
health, max_health, last_heal_score, \
invuln_timer, slow_timer = reset_game()

game_state = PLAYING

# ------------------ LOOP ------------------
running = True
while running:
    clock.tick(60)

    # ================= EVENTS =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # PAUSE TOGGLE
            if event.key == pygame.K_SPACE and game_state == PLAYING:
                paused = not paused

            if game_state == PLAYING and not paused:
                if event.key == pygame.K_LEFT:
                    player["lane"] = max(0, player["lane"] - 1)

                if event.key == pygame.K_RIGHT:
                    player["lane"] = min(LANE_COUNT - 1, player["lane"] + 1)

                if event.key == pygame.K_UP and not player["jumping"]:
                    player["vy"] = JUMP_FORCE
                    player["jumping"] = True

            elif game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    player, obstacles, spawn_timer, score, wall_cd, fake_cd, \
                    boss_mode, boss_timer, boss_phase, boss_done, \
                    shake_timer, shake_intensity, flash_timer, \
                    health, max_health, last_heal_score, \
                    invuln_timer, slow_timer = reset_game()

                    particles.clear()
                    paused = False
                    game_state = PLAYING

    # ================= GAME UPDATE =================
    if game_state == PLAYING and not paused:

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

        player_rect = pygame.Rect(player["x"] - PLAYER_SIZE//2, player["y"], PLAYER_SIZE, PLAYER_SIZE)

        # -------- BOSS MODE --------
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
                flash_timer = 6

                if boss_phase % 3 == 0:
                    gap = random.randint(0, LANE_COUNT - 1)
                    for lane in range(LANE_COUNT):
                        if lane != gap:
                            obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -40, 40, 40), "type": "wall"})

                elif boss_phase % 3 == 1:
                    for i in range(3):
                        lane = (i + boss_phase) % LANE_COUNT
                        obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -40 - i*80, 40, 40), "type": "normal"})

                else:
                    safe = random.randint(0, LANE_COUNT - 1)
                    for lane in range(LANE_COUNT):
                        if lane != safe:
                            obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -40, 40, 40), "type": "fake"})
                    for lane in range(LANE_COUNT):
                        obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -160, 40, 40), "type": "wall"})

            if boss_timer > 800:
                boss_mode = False
                boss_done = True

        elif spawn_timer > spawn_delay:
            r = random.random()

            if difficulty >= 1 and r < 0.20:
                spawn_type = "moving"
            elif difficulty >= 2 and r < 0.35 and wall_cd == 0:
                spawn_type = "wall"
                wall_cd = 2
            elif score > 3000 and r < 0.55 and fake_cd == 0:
                spawn_type = "fake_gap"
                fake_cd = 2
            else:
                spawn_type = "normal"

            if wall_cd > 0: wall_cd -= 1
            if fake_cd > 0: fake_cd -= 1

            if spawn_type == "fake_gap":
                safe = random.randint(0, LANE_COUNT - 1)

                for lane in range(LANE_COUNT):
                    if lane != safe:
                        obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -40, 40, 40), "type": "fake"})

                for lane in range(LANE_COUNT):
                    obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -160, 40, 40), "type": "wall"})

            elif spawn_type == "wall":
                for lane in range(LANE_COUNT):
                    obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -40, 40, 40), "type": "wall"})

            elif spawn_type == "moving":
                lane = random.randint(0, LANE_COUNT - 1)
                obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -40, 40, 40), "type": "moving", "dir": random.choice([-1,1])})

            else:
                lane = random.randint(0, LANE_COUNT - 1)
                obstacles.append({"rect": pygame.Rect(LANES[lane]-20, -40, 40, 40), "type": "normal"})

            spawn_timer = 0

        # -------- SPEED --------
        speed = BASE_SPEED if slow_timer > 0 else BASE_SPEED + difficulty * 1.2
        if slow_timer > 0:
            slow_timer -= 1

        # -------- MOVE --------
        for ob in obstacles:
            ob["rect"].y += speed
            if ob.get("type") == "moving":
                ob["rect"].x += ob["dir"] * 3
                if ob["rect"].left < 0 or ob["rect"].right > WIDTH:
                    ob["dir"] *= -1

        obstacles = [o for o in obstacles if o["rect"].y < HEIGHT]

        # -------- COLLISION --------
        if invuln_timer > 0:
            invuln_timer -= 1

        for ob in obstacles:
            if player_rect.colliderect(ob["rect"]) and invuln_timer == 0:

                if player["y"] < GROUND_Y - 25:
                    continue

                health -= 1

                shake_timer = 15
                flash_timer = 10
                invuln_timer = 30
                slow_timer = 60

                for _ in range(12):
                    particles.append(Particle(player["x"], player["y"], RED))

                obstacles.remove(ob)

                if health <= 0:
                    game_state = GAME_OVER
                break

        score += 1

        # -------- SHAKE --------
        offset_x = random.randint(-10, 10) if shake_timer > 0 else 0
        offset_y = random.randint(-10, 10) if shake_timer > 0 else 0
        if shake_timer > 0:
            shake_timer -= 1

    # ================= DRAW =================
    screen.fill(BLACK)

    # stars
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0
        pygame.draw.circle(screen, (180,180,255), (star[0], star[1]), star[2])

    # particles
    for p in particles[:]:
        p.update(0.5)
        p.draw(screen, (offset_x, offset_y))
        if p.life <= 0:
            particles.remove(p)

    # lanes
    for lane_x in LANES:
        pygame.draw.line(screen, (0,80,255),(lane_x,0),(lane_x,HEIGHT),6)
        pygame.draw.line(screen, (0,200,255),(lane_x,0),(lane_x,HEIGHT),1)

    if game_state == PLAYING:

        # player
        if invuln_timer % 6 < 3:
            pygame.draw.rect(screen, BLUE, player_rect.move(offset_x, offset_y))

        # obstacles
        for ob in obstacles:
            color = RED
            if ob["type"] == "wall": color = PURPLE
            elif ob["type"] == "fake": color = ORANGE
            elif ob["type"] == "moving": color = GREEN
            pygame.draw.rect(screen, color, ob["rect"].move(offset_x, offset_y))

        # UI
        difficulty = score // 1000
        screen.blit(FONT.render(f"Score: {score}", True, WHITE), (10,10))
        screen.blit(FONT.render(f"Level: {difficulty}", True, WHITE), (10,35))

        if boss_mode:
            screen.blit(FONT.render("BOSS MODE!", True, (255,50,50)), (WIDTH//2 - 70,10))

        # health bar
        pygame.draw.rect(screen, (80,80,80), (WIDTH-130,10,120,15))
        pygame.draw.rect(screen, RED, (WIDTH-130,10,int((health/max_health)*120),15))
        pygame.draw.rect(screen, WHITE, (WIDTH-130,10,120,15),2)

        # pause overlay
        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            overlay.fill((0,0,0))
            screen.blit(overlay,(0,0))
            screen.blit(BIG_FONT.render("PAUSED", True, WHITE), (120,300))
            screen.blit(FONT.render("Press SPACE", True, WHITE), (140,350))

    else:
        screen.fill(BLACK)
        screen.blit(BIG_FONT.render("GAME OVER", True, WHITE), (100,250))
        screen.blit(FONT.render(f"Score: {score}", True, WHITE), (140,320))
        screen.blit(FONT.render("Press R", True, WHITE), (160,360))

    # flash
    if flash_timer > 0:
        flash = pygame.Surface((WIDTH, HEIGHT))
        flash.fill((255,255,255))
        flash.set_alpha(120)
        screen.blit(flash,(0,0))
        flash_timer -= 1

    pygame.display.flip()

pygame.quit()
