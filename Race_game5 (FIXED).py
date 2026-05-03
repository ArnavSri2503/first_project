import pygame
import random

pygame.init()

# ------------------ SETTINGS ------------------
WIDTH, HEIGHT = 420, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cube Runner - Neo Merge")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22)
BIG_FONT = pygame.font.SysFont("arial", 40)
SMALL_FONT = pygame.font.SysFont("arial", 16)

# ------------------ COLORS ------------------
BLACK = (10, 10, 20)
WHITE = (240, 240, 240)
RED = (220, 50, 50)
BLUE = (60, 140, 255)
PURPLE = (160, 0, 200)
ORANGE = (255, 140, 0)
GREEN = (0, 220, 120)
CYAN = (0, 220, 255)
GRAY = (50, 50, 70)

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


# ------------------ VISUAL HELPERS ------------------
def glow(surface, color, rect, offset=(0, 0), layers=2):
    for i in range(layers):
        size = 4 + i * 4
        alpha = max(10, 38 - i * 12)
        g = rect.inflate(size, size)
        s = pygame.Surface((g.width, g.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=8)
        surface.blit(s, (g.x + offset[0], g.y + offset[1]))


def draw_text_center(surface, font, text, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img, (x - img.get_width() // 2, y))


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp_color(a, b, t):
    t = clamp(t, 0.0, 1.0)
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def get_trail_color(difficulty, health_ratio):
    # Difficulty pushes color from cyan -> blue -> purple.
    diff_t = clamp(difficulty / 7.0, 0.0, 1.0)
    if diff_t < 0.5:
        base = lerp_color((0, 255, 255), (60, 140, 255), diff_t / 0.5)
    else:
        base = lerp_color((60, 140, 255), (170, 60, 255), (diff_t - 0.5) / 0.5)

    # Low health blends the current hue toward red.
    danger_t = clamp((0.45 - health_ratio) / 0.45, 0.0, 1.0)
    return lerp_color(base, (255, 60, 60), danger_t)


# ------------------ RESET ------------------
def reset_game():
    lane_index = LANE_COUNT // 2
    player = {
        "x": LANES[lane_index],
        "y": GROUND_Y,
        "vy": 0,
        "jumping": False,
        "lane": lane_index,
    }

    return {
        "player": player,
        "obstacles": [],
        "spawn_timer": 0,
        "score": 0,
        "wall_cd": 0,
        "fake_cd": 0,
        "boss_mode": False,
        "boss_timer": 0,
        "boss_phase": 0,
        "boss_done": False,
        "shake_timer": 0,
        "shake_intensity": 0,
        "flash_timer": 0,
        "health": 4.0,
        "max_health": 4.0,
        "last_heal_score": 0,
        "invuln_timer": 0,
        "player_trail": [],
        "impact_particles": [],
        "boss_banner_timer": 0,
        "trail_particles": [],
    }


state = reset_game()
game_state = PLAYING

# ------------------ BACKGROUND ------------------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)] for _ in range(90)]

running = True
paused = False
while running:
    clock.tick(60)

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
        if event.type == pygame.QUIT:
            running = False

        if game_state == PLAYING and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                state["player"]["lane"] = max(0, state["player"]["lane"] - 1)
            if event.key == pygame.K_RIGHT:
                state["player"]["lane"] = min(LANE_COUNT - 1, state["player"]["lane"] + 1)
            if event.key == pygame.K_UP and not state["player"]["jumping"]:
                state["player"]["vy"] = JUMP_FORCE
                state["player"]["jumping"] = True

        elif game_state == GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                state = reset_game()
                game_state = PLAYING
            elif event.key == pygame.K_ESCAPE:
                running = False

    # -------- UPDATE --------
    if game_state == PLAYING and not paused:
        difficulty = state["score"] // 1000
        player = state["player"]
        obstacles = state["obstacles"]

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

        state["player_trail"].append(player_rect.copy())
        if len(state["player_trail"]) > 6:
            state["player_trail"].pop(0)

        # -------- BOSS TRIGGER --------
        if state["score"] >= 5000 and not state["boss_mode"] and not state["boss_done"]:
            state["boss_mode"] = True
            state["boss_timer"] = 0
            state["boss_phase"] = 0
            state["boss_banner_timer"] = 120
            obstacles.clear()

        # -------- SPAWN --------
        state["spawn_timer"] += 1
        spawn_delay = max(18, 40 - difficulty * 3)

        if state["boss_mode"]:
            state["boss_timer"] += 1

            if state["boss_timer"] % 40 == 0:
                state["boss_phase"] += 1
                state["shake_timer"] = 10
                state["shake_intensity"] = 8
                state["flash_timer"] = 6

                if state["boss_phase"] % 3 == 0:
                    gap = random.randint(0, LANE_COUNT - 1)
                    for lane in range(LANE_COUNT):
                        if lane != gap:
                            x = LANES[lane]
                            obstacles.append({
                                "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                                "type": "wall",
                            })
                elif state["boss_phase"] % 3 == 1:
                    for i in range(3):
                        lane = (i + state["boss_phase"]) % LANE_COUNT
                        x = LANES[lane]
                        obstacles.append({
                            "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT - i * 80, OB_WIDTH, OB_HEIGHT),
                            "type": "normal",
                        })
                else:
                    safe = random.randint(0, LANE_COUNT - 1)
                    for lane in range(LANE_COUNT):
                        if lane != safe:
                            x = LANES[lane]
                            obstacles.append({
                                "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                                "type": "fake",
                            })
                    for lane in range(LANE_COUNT):
                        x = LANES[lane]
                        obstacles.append({
                            "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT - 120, OB_WIDTH, OB_HEIGHT),
                            "type": "wall",
                        })

            if state["boss_timer"] > 800:
                state["boss_mode"] = False
                state["boss_done"] = True
                state["boss_timer"] = 0
                state["boss_phase"] = 0

        elif state["spawn_timer"] > spawn_delay:
            r = random.random()
            spawn_type = "normal"

            # Make moving blocks a core obstacle type, roughly as common as normal reds.
            moving_chance = 0.26

            # Keep wall/fake-gap patterns from appearing back-to-back or with only one spawn between them.
            pattern_locked = state["wall_cd"] > 0 or state["fake_cd"] > 0

            if difficulty >= 2 and r < 0.08 and not pattern_locked:
                spawn_type = "wall"
                state["wall_cd"] = 3
                state["fake_cd"] = max(state["fake_cd"], 3)
            elif state["score"] > 3000 and r < 0.18 and not pattern_locked:
                spawn_type = "fake_gap"
                state["fake_cd"] = 3
                state["wall_cd"] = max(state["wall_cd"], 3)
            elif difficulty >= 1 and r < moving_chance:
                spawn_type = "moving"

            if state["wall_cd"] > 0:
                state["wall_cd"] -= 1
            if state["fake_cd"] > 0:
                state["fake_cd"] -= 1

            if spawn_type == "wall":
                for lane in range(LANE_COUNT):
                    x = LANES[lane]
                    obstacles.append({
                        "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                        "type": "wall",
                    })
            elif spawn_type == "fake_gap":
                safe = random.randint(0, LANE_COUNT - 1)
                for lane in range(LANE_COUNT):
                    if lane != safe:
                        x = LANES[lane]
                        obstacles.append({
                            "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                            "type": "fake",
                        })
                for lane in range(LANE_COUNT):
                    x = LANES[lane]
                    obstacles.append({
                        "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT - 120, OB_WIDTH, OB_HEIGHT),
                        "type": "wall",
                    })
            elif spawn_type == "moving":
                lane = random.randint(0, LANE_COUNT - 1)
                x = LANES[lane]
                obstacles.append({
                    "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                    "type": "moving",
                    "dir": random.choice([-1, 1]),
                })
            else:
                lane = random.randint(0, LANE_COUNT - 1)
                x = LANES[lane]
                obstacles.append({
                    "rect": pygame.Rect(x - OB_WIDTH // 2, -OB_HEIGHT, OB_WIDTH, OB_HEIGHT),
                    "type": "normal",
                })

            state["spawn_timer"] = 0

        # -------- MOVE OBSTACLES --------
        speed = BASE_SPEED + difficulty * 1.2

        for ob in obstacles:
            ob["rect"].y += speed
            if ob.get("type") == "moving":
                ob["rect"].x += ob["dir"] * 3
                if ob["rect"].left < 0 or ob["rect"].right > WIDTH:
                    ob["dir"] *= -1

                # Add trail for moving enemies
                if "trail" not in ob:
                    ob["trail"] = []
                ob["trail"].append((ob["rect"].x, ob["rect"].y, ob["rect"].width, ob["rect"].height))
                if len(ob["trail"]) > 5:
                    ob["trail"].pop(0)

        state["obstacles"] = [ob for ob in obstacles if ob["rect"].y < HEIGHT]
        obstacles = state["obstacles"]

        # -------- COLLISION --------
        if state["invuln_timer"] > 0:
            state["invuln_timer"] -= 1

        hit_index = None
        for i, ob in enumerate(obstacles):
            if player_rect.colliderect(ob["rect"]) and state["invuln_timer"] == 0:
                if player["y"] < GROUND_Y - 25:
                    continue

                damage = 1 if ob["type"] != "wall" else 2
                state["health"] -= damage
                state["health"] = max(0, state["health"])

                state["shake_timer"] = 15
                state["shake_intensity"] = 12
                state["flash_timer"] = 10
                state["invuln_timer"] = 30

                for _ in range(14):
                    state["impact_particles"].append({
                        "x": ob["rect"].centerx,
                        "y": ob["rect"].centery,
                        "vx": random.uniform(-3.5, 3.5),
                        "vy": random.uniform(-4.0, 1.0),
                        "life": random.randint(14, 28),
                        "color": RED if ob["type"] == "normal" else PURPLE if ob["type"] == "wall" else ORANGE if ob["type"] == "fake" else GREEN,
                    })

                hit_index = i
                if state["health"] <= 0:
                    game_state = GAME_OVER
                break

        if hit_index is not None and hit_index < len(obstacles):
            obstacles.pop(hit_index)

        # -------- SCORE & HEALTH REGEN --------
        state["score"] += 1
        if state["score"] - state["last_heal_score"] >= 400:
            if state["health"] < state["max_health"]:
                state["health"] = min(state["max_health"], state["health"] + 0.2)
            state["last_heal_score"] = state["score"]

        # -------- PARTICLES --------
        new_particles = []
        for p in state["impact_particles"]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15
            p["life"] -= 1
            if p["life"] > 0:
                new_particles.append(p)
        state["impact_particles"] = new_particles

        if state["boss_banner_timer"] > 0:
            state["boss_banner_timer"] -= 1

    # -------- SCREEN SHAKE --------
    offset_x = 0
    offset_y = 0
    if state["shake_timer"] > 0:
        offset_x = random.randint(-state["shake_intensity"], state["shake_intensity"])
        offset_y = random.randint(-state["shake_intensity"], state["shake_intensity"])
        state["shake_timer"] -= 1

    # -------- DRAW --------
    screen.fill(BLACK)

    # Background stars
    bg_speed = 1.5 if game_state == PLAYING else 0.5
    for s in stars:
        s[1] += s[2] * bg_speed
        if s[1] > HEIGHT:
            s[1] = 0
            s[0] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, (170, 180, 255), (int(s[0] + offset_x * 0.25), int(s[1] + offset_y * 0.25)), s[2])

    # Lane glow pulse
    pulse = (pygame.time.get_ticks() % 1000) / 1000.0
    lane_color = (0, int(150 + 90 * pulse), 255)
    for lane_x in LANES:
        pygame.draw.line(screen, lane_color, (lane_x + offset_x, 0), (lane_x + offset_x, HEIGHT), 2)

    if game_state == PLAYING:
        player = state["player"]
        difficulty = state["score"] // 1000
        player_rect = pygame.Rect(player["x"] - PLAYER_SIZE // 2, player["y"], PLAYER_SIZE, PLAYER_SIZE)

        # Player trail (TRON style - stronger, filled)
        health_ratio = state["health"] / state["max_health"]
        trail_color = get_trail_color(difficulty, health_ratio)
        prev_rect = None
        moved_enough = False
        if len(state["player_trail"]) >= 2:
            prev_rect = state["player_trail"][-2]
            moved_enough = abs(player_rect.centerx - prev_rect.centerx) > 1 or abs(player_rect.centery - prev_rect.centery) > 1

        for i, t in enumerate(state["player_trail"]):
            alpha = max(80, 220 - (len(state["player_trail"]) - i) * 20)
            pygame.draw.rect(screen, (*trail_color, alpha), (t.x + offset_x, t.y + offset_y, t.width, t.height), border_radius=6)

        # Convert tail into particles only while the trail is actually moving.
        if len(state["player_trail"]) >= 2 and moved_enough:
            tail = state["player_trail"][0]
            dx = player_rect.centerx - prev_rect.centerx
            dy = player_rect.centery - prev_rect.centery
            emit_vx = -dx * 0.35
            emit_vy = -dy * 0.35
            for _ in range(1):
                state["trail_particles"].append({
                    "x": tail.centerx,
                    "y": tail.centery,
                    "vx": emit_vx + random.uniform(-0.9, 0.9),
                    "vy": emit_vy + random.uniform(-0.8, 0.4),
                    "life": random.randint(10, 20),
                    "color": trail_color,
                })

        # Player
        if state["invuln_timer"] % 6 < 3:
            glow(screen, BLUE, player_rect, (offset_x, offset_y), layers=3)
            pygame.draw.rect(screen, BLUE, player_rect.move(offset_x, offset_y), border_radius=6)

        # Obstacles
        for ob in state["obstacles"]:
            color = RED
            if ob["type"] == "wall":
                color = PURPLE
            elif ob["type"] == "fake":
                color = ORANGE
            elif ob["type"] == "moving":
                color = GREEN

            # Trail for moving enemies (direct draw)
            if ob.get("type") == "moving" and "trail" in ob:
                for i, t in enumerate(ob["trail"]):
                    tx, ty, tw, th = t
                    alpha = max(50, 170 - (len(ob["trail"]) - i) * 22)
                    trail_color = (0, 255, 180, alpha)
                    pygame.draw.rect(screen, trail_color, (tx + offset_x, ty + offset_y, tw, th), border_radius=6)

            glow(screen, color, ob["rect"], (offset_x, offset_y), layers=2)
            pygame.draw.rect(screen, color, ob["rect"].move(offset_x, offset_y), border_radius=6)

        # Impact particles
        for p in state["impact_particles"]:
            pygame.draw.circle(screen, p["color"], (int(p["x"] + offset_x), int(p["y"] + offset_y)), 3)

        # Trail particles (direct draw, no full-screen surfaces)
        new_tp = []
        for p in state["trail_particles"]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.05
            p["life"] -= 1
            if p["life"] > 0:
                new_tp.append(p)
                alpha = int(255 * (p["life"] / 20))
                start = (int(p["x"] + offset_x), int(p["y"] + offset_y))
                end = (
                    int(p["x"] - p["vx"] * 3.0 + offset_x),
                    int(p["y"] - p["vy"] * 3.0 + offset_y),
                )
                pygame.draw.line(screen, (*p["color"], alpha), start, end, 3)
                pygame.draw.circle(screen, (*p["color"], alpha), start, 2)
        state["trail_particles"] = new_tp
        if len(state["trail_particles"]) > 60:
            state["trail_particles"] = state["trail_particles"][-60:]

        # HUD
        screen.blit(FONT.render(f"Score: {state['score']}", True, WHITE), (10, 10))
        screen.blit(FONT.render(f"Level: {difficulty}", True, WHITE), (10, 35))

        if state["boss_mode"]:
            boss_text = FONT.render("BOSS MODE!", True, (255, 80, 120))
            glow_rect = boss_text.get_rect(center=(WIDTH // 2, 22))
            glow(screen, (255, 80, 120), glow_rect.inflate(12, 8), (0, 0), layers=2)
            screen.blit(boss_text, (WIDTH // 2 - boss_text.get_width() // 2, 10))

        if state["boss_banner_timer"] > 0:
            banner = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
            banner.fill((255, 0, 80, 45))
            screen.blit(banner, (0, HEIGHT // 2 - 40))
            draw_text_center(screen, BIG_FONT, "WARNING", WHITE, WIDTH // 2, HEIGHT // 2 - 28)
            draw_text_center(screen, SMALL_FONT, "Neo boss pattern incoming", WHITE, WIDTH // 2, HEIGHT // 2 + 10)

        # Health bar
        bar_width = 120
        bar_height = 14
        x = WIDTH - bar_width - 10
        y = 10
        pygame.draw.rect(screen, GRAY, (x, y, bar_width, bar_height), border_radius=6)
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2, border_radius=6)
        fill_width = int((state["health"] / state["max_health"]) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(screen, RED, (x, y, fill_width, bar_height), border_radius=6)

        # Flash
        if state["flash_timer"] > 0:
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.fill((255, 255, 255))
            flash.set_alpha(110)
            screen.blit(flash, (0, 0))
            state["flash_timer"] -= 1

    else:
        draw_text_center(screen, BIG_FONT, "GAME OVER", WHITE, WIDTH // 2, 250)
        draw_text_center(screen, FONT, f"Score: {state['score']}", WHITE, WIDTH // 2, 320)
        draw_text_center(screen, FONT, "Press R to Restart", WHITE, WIDTH // 2, 360)
        draw_text_center(screen, SMALL_FONT, "Esc to Quit", (180, 180, 210), WIDTH // 2, 392)

    # Pause overlay
    if paused:
        pause_text = BIG_FONT.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 20))

    pygame.display.flip()

pygame.quit()
