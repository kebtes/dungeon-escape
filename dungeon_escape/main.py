"""
Dungeon Escape - A 2D Top-Down Roguelike-Style Dungeon Adventure
Built with Python and Pygame Zero.

Technical restrictions:
- Standard library modules only (math, random).
- No direct pygame imports.
- Reusable OOP architecture (Player, Enemy, Button).
"""

import math
import random

# =============================================================================
# WINDOW CONFIGURATION
# =============================================================================
TITLE = "Dungeon Escape"
WIDTH = 800
HEIGHT = 600

# Boundary limits for the dungeon room
MIN_X = 50
MAX_X = 750
MIN_Y = 90
MAX_Y = 550

# Custom Dungeon Themed Fonts
FONT_TITLE = "dungeon_title"
FONT_UI = "dungeon_ui"

# Camera screen shake offset
shake_x = 0
shake_y = 0
shake_timer = 0.0

# Active visual sparkle particles
particles = []


# =============================================================================
# PARTICLE SYSTEM
# =============================================================================
def spawn_crystal_sparkles(x, y):
    """Spawn a burst of glowing cyan and white sparkle particles."""
    colors = [(60, 240, 255), (150, 255, 255), (255, 255, 255), (0, 190, 240)]
    for _ in range(10):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(60, 140)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        color = random.choice(colors)
        life = random.uniform(0.25, 0.45)
        # Each particle: [x, y, vx, vy, color, timer, max_life]
        particles.append([x, y, vx, vy, color, life, life])


def update_particles(dt):
    """Advance particle positions and cull expired particles."""
    global particles
    for p in particles:
        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[5] -= dt
    particles = [p for p in particles if p[5] > 0.0]


def draw_particles(ox, oy):
    """Draw alive sparkle particles fading out."""
    for p in particles:
        progress = max(0.0, p[5] / p[6])
        radius = max(1, int(3 * progress) + 1)
        screen.draw.filled_circle((int(p[0] + ox), int(p[1] + oy)), radius, p[4])


# =============================================================================
# UI BUTTON CLASS
# =============================================================================
class Button:
    """Clickable UI button for menus and end screens."""

    def __init__(self, x, y, width, height, text, bg_color=(45, 45, 65), text_color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self):
        # Draw background rectangle and distinct border
        rect = Rect(self.x, self.y, self.width, self.height)
        screen.draw.filled_rect(rect, self.bg_color)
        screen.draw.rect(rect, (130, 120, 170))
        # Draw centered text
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        screen.draw.text(self.text, center=(cx, cy), fontsize=22, color=self.text_color, fontname=FONT_UI)

    def is_clicked(self, pos):
        """Check if mouse coordinate (x, y) is inside button bounds."""
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height


# =============================================================================
# PLAYER CLASS
# =============================================================================
class Player:
    """Player character with 4-direction movement, animation, health, and cooldown."""

    def __init__(self, x, y):
        self.actor = Actor("player_idle_1", (x, y))
        self.speed = 180.0
        self.lives = 3
        self.invulnerable_timer = 0.0
        self.moving = False

        # Animation parameters
        self.idle_frames = ["player_idle_1", "player_idle_2"]
        self.walk_frames = ["player_walk_1", "player_walk_2", "player_walk_3", "player_walk_4"]
        self.anim_timer = 0.0
        self.frame_index = 0

    def move(self, dt, obstacles):
        """Handle 4-direction keyboard movement and collision with walls & obstacles."""
        dx = 0.0
        dy = 0.0

        if keyboard.left or keyboard.a:
            dx -= 1.0
        if keyboard.right or keyboard.d:
            dx += 1.0
        if keyboard.up or keyboard.w:
            dy -= 1.0
        if keyboard.down or keyboard.s:
            dy += 1.0

        # Normalize diagonal movement to maintain consistent speed
        if dx != 0.0 and dy != 0.0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

        self.moving = (dx != 0.0 or dy != 0.0)

        # Move X axis with collision check
        old_x = self.actor.x
        self.actor.x += dx * self.speed * dt
        # Clamp to dungeon room boundaries
        self.actor.x = max(MIN_X, min(MAX_X, self.actor.x))
        for obs in obstacles:
            if self.actor.colliderect(obs):
                self.actor.x = old_x
                break

        # Move Y axis with collision check
        old_y = self.actor.y
        self.actor.y += dy * self.speed * dt
        # Clamp to dungeon room boundaries
        self.actor.y = max(MIN_Y, min(MAX_Y, self.actor.y))
        for obs in obstacles:
            if self.actor.colliderect(obs):
                self.actor.y = old_y
                break

    def update(self, dt):
        """Update invulnerability cooldown timer and cyclic animation frames."""
        # Decrement damage cooldown
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt

        # Animate sprite cycle
        self.anim_timer += dt
        frames = self.walk_frames if self.moving else self.idle_frames
        duration = 0.12 if self.moving else 0.35

        if self.anim_timer >= duration:
            self.anim_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.actor.image = frames[self.frame_index]

    def take_damage(self, enemy_pos=None):
        """Apply damage, activate screen shake, and apply physical knockback."""
        global shake_timer

        if self.invulnerable_timer <= 0.0:
            self.lives -= 1
            self.invulnerable_timer = 1.0  # 1 second invulnerability
            shake_timer = 0.22  # Trigger camera impact shake
            play_sound("damage")

            # Apply physical knockback away from the enemy
            if enemy_pos is not None:
                kx = self.actor.x - enemy_pos[0]
                ky = self.actor.y - enemy_pos[1]
                dist = math.hypot(kx, ky)
                if dist > 0.1:
                    self.actor.x += (kx / dist) * 34.0
                    self.actor.y += (ky / dist) * 34.0
                    self.actor.x = max(MIN_X, min(MAX_X, self.actor.x))
                    self.actor.y = max(MIN_Y, min(MAX_Y, self.actor.y))
            return True
        return False

    def draw(self, ox=0, oy=0):
        """Draw player sprite, flickering during invulnerability feedback."""
        old_pos = self.actor.pos
        self.actor.x += ox
        self.actor.y += oy

        if self.invulnerable_timer > 0.0:
            # Flicker visibility every 0.1 second
            if int(self.invulnerable_timer * 10) % 2 == 0:
                self.actor.draw()
        else:
            self.actor.draw()

        self.actor.pos = old_pos


# =============================================================================
# ENEMY CLASS (With 2D Pursuit Following AI & Patrol Modes)
# =============================================================================
class Enemy:
    """Configurable enemy supporting autonomous patrol and balanced 2D player tracking."""

    def __init__(self, name, axis, min_coord, max_coord, speed, chase_speed, detection_range, idle_frames, walk_frames, area_bounds=None):
        self.name = name
        self.axis = axis  # 'x' for horizontal, 'y' for vertical
        self.min_coord = min_coord
        self.max_coord = max_coord
        self.speed = speed
        self.chase_speed = chase_speed
        self.detection_range = detection_range
        self.direction = 1

        # Territorial boundary limits ensuring enemy stays strictly within its own area
        self.area_min_x = area_bounds[0] if area_bounds else MIN_X
        self.area_max_x = area_bounds[1] if area_bounds else MAX_X
        self.area_min_y = area_bounds[2] if area_bounds else MIN_Y
        self.area_max_y = area_bounds[3] if area_bounds else MAX_Y

        self.idle_frames = idle_frames
        self.walk_frames = walk_frames
        self.anim_timer = 0.0
        self.frame_index = 0
        self.frame_duration = 0.15

        self.pause_timer = 0.0
        self.is_aggro = False

        self.actor = Actor(walk_frames[0], (0, 0))

    def set_position(self, x, y, area_bounds=None):
        self.actor.x = x
        self.actor.y = y
        if area_bounds:
            self.area_min_x, self.area_max_x, self.area_min_y, self.area_max_y = area_bounds

    def set_patrol_bounds(self, min_c, max_c):
        self.min_coord = min_c
        self.max_coord = max_c

    def update(self, dt, target_player, obstacles):
        """Update enemy: actively hunt and follow player in 2D if in range; else patrol."""
        # Calculate full 2D distance to player
        dx = target_player.actor.x - self.actor.x
        dy = target_player.actor.y - self.actor.y
        dist = math.hypot(dx, dy)

        # 1. ACTIVE 2D PURSUIT (CHASE MODE WITHIN ASSIGNED AREA)
        if dist < self.detection_range:
            self.is_aggro = True
            if dist > 2.0:
                nx = dx / dist
                ny = dy / dist

                # Move X toward player, strictly constrained within its own territorial area
                old_x = self.actor.x
                self.actor.x += nx * self.chase_speed * dt
                self.actor.x = max(self.area_min_x, min(self.area_max_x, self.actor.x))
                if "Ghost" not in self.name:
                    for obs in obstacles:
                        if self.actor.colliderect(obs):
                            self.actor.x = old_x
                            break

                # Move Y toward player, strictly constrained within its own territorial area
                old_y = self.actor.y
                self.actor.y += ny * self.chase_speed * dt
                self.actor.y = max(self.area_min_y, min(self.area_max_y, self.actor.y))
                if "Ghost" not in self.name:
                    for obs in obstacles:
                        if self.actor.colliderect(obs):
                            self.actor.y = old_y
                            break

            self._animate_walk(dt)
            return

        # 2. PATROL MODE (Player is beyond detection range)
        self.is_aggro = False

        # Slime squish-pause at patrol ends
        if "Slime" in self.name and self.pause_timer > 0.0:
            self.pause_timer -= dt
            self.actor.image = self.walk_frames[0]
            return

        if self.axis == 'x':
            self.actor.x += self.direction * self.speed * dt
            if self.actor.x >= self.max_coord:
                self.actor.x = self.max_coord
                self.direction = -1
                if "Slime" in self.name:
                    self.pause_timer = 0.5
            elif self.actor.x <= self.min_coord:
                self.actor.x = self.min_coord
                self.direction = 1
                if "Slime" in self.name:
                    self.pause_timer = 0.5
        else:
            self.actor.y += self.direction * self.speed * dt
            if self.actor.y >= self.max_coord:
                self.actor.y = self.max_coord
                self.direction = -1
            elif self.actor.y <= self.min_coord:
                self.actor.y = self.min_coord
                self.direction = 1

        self._animate_walk(dt)

    def _animate_walk(self, dt):
        """Advance cyclic walking animation."""
        self.anim_timer += dt
        if self.anim_timer >= self.frame_duration:
            self.anim_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
            self.actor.image = self.walk_frames[self.frame_index]

    def check_collision(self, target_player):
        """Check collision with player and apply damage with knockback."""
        if self.actor.colliderect(target_player.actor):
            target_player.take_damage(self.actor.pos)

    def draw(self, ox=0, oy=0):
        old_pos = self.actor.pos
        self.actor.x += ox
        self.actor.y += oy
        self.actor.draw()

        # Visual exclamation mark above enemy head when pursuing the player
        if self.is_aggro:
            screen.draw.text("!", (self.actor.x - 3, self.actor.top - 20), fontsize=24, color=(255, 60, 60), owidth=1, ocolor=(0, 0, 0))

        self.actor.pos = old_pos


# =============================================================================
# GAME STATE & GLOBALS
# =============================================================================
game_state = "menu"  # "menu", "playing", "won", "lost"
sound_enabled = True
status_message = ""
status_timer = 0.0

# Game entities
player = None
enemies = []
crystals = []
portal = None
obstacles = []

# Menu & UI Buttons
btn_start = Button(300, 260, 200, 48, "Start Game", (55, 60, 85))
btn_sound = Button(300, 330, 200, 48, "Sound: ON", (45, 50, 70))
btn_exit = Button(300, 400, 200, 48, "Exit", (70, 40, 45))

# End screen buttons
btn_play_again = Button(280, 360, 240, 46, "Play Again", (45, 80, 55))
btn_try_again = Button(280, 360, 240, 46, "Try Again", (90, 45, 45))
btn_main_menu = Button(280, 430, 240, 46, "Main Menu", (50, 50, 70))


# =============================================================================
# AUDIO HELPERS
# =============================================================================
def play_sound(sound_name):
    """Play a sound effect if audio is enabled."""
    if not sound_enabled:
        return
    try:
        snd = getattr(sounds, sound_name)
        snd.play()
    except Exception:
        pass


def play_music():
    """Start background music looping if audio is enabled."""
    if not sound_enabled:
        return
    try:
        music.play("dungeon_theme")
    except Exception:
        pass


def stop_music():
    """Stop background music."""
    try:
        music.stop()
    except Exception:
        pass


def toggle_sound():
    """Toggle sound effects and music on/off."""
    global sound_enabled
    sound_enabled = not sound_enabled
    btn_sound.text = "Sound: ON" if sound_enabled else "Sound: OFF"

    if sound_enabled:
        if game_state == "playing":
            play_music()
    else:
        stop_music()


# =============================================================================
# PROCEDURAL SAFE POSITION GENERATION
# =============================================================================
def is_far(pos1, pos2, min_d):
    """Return True if euclidean distance between pos1 and pos2 >= min_d."""
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]) >= min_d


def get_random_player_pos(pillar_coords, portal_coord):
    """Generate a random starting position for player avoiding pillars and portal."""
    for _ in range(100):
        rx = random.randint(MIN_X + 40, MAX_X - 40)
        ry = random.randint(MIN_Y + 40, MAX_Y - 40)
        if all(is_far((rx, ry), p, 70) for p in pillar_coords) and is_far((rx, ry), portal_coord, 80):
            return (rx, ry)
    return (120, 310)


def get_random_enemy_pos(player_pos, placed_enemies, pillar_coords):
    """Generate a random enemy position with a guaranteed 200+ px buffer from the player."""
    for _ in range(200):
        rx = random.randint(MIN_X + 40, MAX_X - 40)
        ry = random.randint(MIN_Y + 40, MAX_Y - 40)
        # Ensure safe buffer from player
        if not is_far((rx, ry), player_pos, 200):
            continue
        # Ensure not inside stone pillars
        if any(not is_far((rx, ry), p, 70) for p in pillar_coords):
            continue
        # Ensure enemies do not spawn on top of each other
        if any(not is_far((rx, ry), e, 80) for e in placed_enemies):
            continue
        return (rx, ry)
    # Safe fallback if room is tight
    fallback_x = MIN_X + 80 if player_pos[0] > (WIDTH // 2) else MAX_X - 80
    return (fallback_x, random.randint(MIN_Y + 60, MAX_Y - 60))


# =============================================================================
# GAME INITIALIZATION
# =============================================================================
def start_game():
    """Initialize or reset all entities with randomized, safe-distance spawns."""
    global player, enemies, crystals, portal, obstacles, game_state, status_message, status_timer, particles, shake_timer

    particles.clear()
    shake_timer = 0.0

    # 1. Dungeon obstacles (two central pillars)
    obstacles = [
        Actor("pillar", (260, 310)),
        Actor("pillar", (540, 310))
    ]
    pillar_coords = [(260, 310), (540, 310)]
    portal_coord = (400, 100)

    # 2. Exit portal starts locked at top-center
    portal = Actor("portal_locked", portal_coord)

    # 3. Spawn Player at a random safe room coordinate
    px, py = get_random_player_pos(pillar_coords, portal_coord)
    player = Player(px, py)

    # 4. Create 4 enemies with gentle, relaxed speeds (substantially slower)
    # Enemy 1: Green Slime (Slow ground bouncer)
    slime = Enemy(
        name="Slime",
        axis="x",
        min_coord=130,
        max_coord=360,
        speed=60.0,
        chase_speed=88.0,
        detection_range=175.0,
        idle_frames=["slime_idle_1", "slime_idle_2"],
        walk_frames=["slime_walk_1", "slime_walk_2"]
    )

    # Enemy 2: Skeleton Warrior (Corridor patroller)
    skeleton1 = Enemy(
        name="Skeleton",
        axis="y",
        min_coord=150,
        max_coord=450,
        speed=68.0,
        chase_speed=100.0,
        detection_range=195.0,
        idle_frames=["skeleton_idle_1", "skeleton_idle_2"],
        walk_frames=["skeleton_walk_1", "skeleton_walk_2", "skeleton_walk_3", "skeleton_walk_4"]
    )

    # Enemy 3: Dungeon Ghost (Gentle floating phantom)
    ghost = Enemy(
        name="Ghost",
        axis="x",
        min_coord=220,
        max_coord=580,
        speed=58.0,
        chase_speed=86.0,
        detection_range=185.0,
        idle_frames=["ghost_idle_1", "ghost_idle_2"],
        walk_frames=["ghost_walk_1", "ghost_walk_2"]
    )

    # Enemy 4: Skeleton Guardian (Portal guardian)
    skeleton2 = Enemy(
        name="Skeleton Guardian",
        axis="x",
        min_coord=280,
        max_coord=520,
        speed=70.0,
        chase_speed=105.0,
        detection_range=195.0,
        idle_frames=["skeleton_idle_1", "skeleton_idle_2"],
        walk_frames=["skeleton_walk_1", "skeleton_walk_2", "skeleton_walk_3", "skeleton_walk_4"]
    )

    all_enemies = [slime, skeleton1, ghost, skeleton2]
    placed_enemy_coords = []

    # Assign each enemy to a random room coordinate guaranteed >= 200px away from the player
    for en in all_enemies:
        ex, ey = get_random_enemy_pos((player.actor.x, player.actor.y), placed_enemy_coords, pillar_coords)
        
        # Define the enemy's dedicated territorial area (strictly stays within this area)
        area_radius = 160
        area_box = (
            max(MIN_X + 10, ex - area_radius),
            min(MAX_X - 10, ex + area_radius),
            max(MIN_Y + 10, ey - area_radius),
            min(MAX_Y - 10, ey + area_radius)
        )
        en.set_position(ex, ey, area_box)
        placed_enemy_coords.append((ex, ey))

        # Dynamically center their patrol bounds inside their assigned territory
        if en.axis == 'x':
            patrol_half = random.randint(80, 130)
            en.set_patrol_bounds(max(en.area_min_x, ex - patrol_half), min(en.area_max_x, ex + patrol_half))
        else:
            patrol_half = random.randint(80, 130)
            en.set_patrol_bounds(max(en.area_min_y, ey - patrol_half), min(en.area_max_y, ey + patrol_half))

    enemies = all_enemies

    # 5. Place five collectible crystals distributed throughout the room
    crystal_coords = [
        (130, 150),  # Top-left
        (150, 490),  # Bottom-left
        (360, 340),  # Center-left
        (680, 140),  # Top-right
        (680, 500)   # Bottom-right
    ]
    crystals = [Actor("crystal", pos) for pos in crystal_coords]

    status_message = "Find all 5 crystals to unlock the escape portal!"
    status_timer = 4.0
    game_state = "playing"
    play_music()


def set_status(msg, duration=3.0):
    """Display a temporary HUD notification banner."""
    global status_message, status_timer
    status_message = msg
    status_timer = duration


# =============================================================================
# PYGAME ZERO EVENT HANDLERS
# =============================================================================
def on_mouse_down(pos):
    """Handle mouse click interactions for menus and end screens."""
    global game_state

    if game_state == "menu":
        if btn_start.is_clicked(pos):
            start_game()
        elif btn_sound.is_clicked(pos):
            toggle_sound()
        elif btn_exit.is_clicked(pos):
            stop_music()
            exit()

    elif game_state == "won":
        if btn_play_again.is_clicked(pos):
            start_game()
        elif btn_main_menu.is_clicked(pos):
            game_state = "menu"

    elif game_state == "lost":
        if btn_try_again.is_clicked(pos):
            start_game()
        elif btn_main_menu.is_clicked(pos):
            game_state = "menu"


def on_key_down(key):
    """Keyboard shortcuts for convenience."""
    global game_state
    if game_state == "menu" and key == keys.SPACE:
        start_game()


# =============================================================================
# PYGAME ZERO MAIN LOOP
# =============================================================================
def update(dt):
    """Update game logic, entities, collisions, and state transitions."""
    global game_state, status_timer, status_message, shake_timer, shake_x, shake_y

    if game_state != "playing":
        return

    # Update camera shake
    if shake_timer > 0.0:
        shake_timer -= dt
        shake_x = random.randint(-4, 4)
        shake_y = random.randint(-4, 4)
    else:
        shake_x = 0
        shake_y = 0

    # Update particles
    update_particles(dt)

    # Update HUD status message timer
    if status_timer > 0.0:
        status_timer -= dt
        if status_timer <= 0.0:
            status_message = ""

    # 1. Update Player movement and animation
    player.move(dt, obstacles)
    player.update(dt)

    # 2. Check if player has lost all lives
    if player.lives <= 0:
        game_state = "lost"
        stop_music()
        play_sound("game_over")
        return

    # 3. Update Enemies with smart 2D hunting AI and check player damage collision
    for enemy in enemies:
        enemy.update(dt, player, obstacles)
        enemy.check_collision(player)

    # Check again if damage killed the player
    if player.lives <= 0:
        game_state = "lost"
        stop_music()
        play_sound("game_over")
        return

    # 4. Check Crystal collections
    for crystal in list(crystals):
        if player.actor.colliderect(crystal):
            crystals.remove(crystal)
            spawn_crystal_sparkles(crystal.x, crystal.y)
            play_sound("collect")
            remaining = len(crystals)
            if remaining == 0:
                # All crystals collected -> unlock the portal
                portal.image = "portal_active"
                play_sound("portal")
                set_status("PORTAL UNLOCKED! Escape through the portal at the top!", 5.0)
            else:
                set_status(f"Crystal collected! {5 - remaining}/5 found.", 2.0)

    # 5. Check Exit Portal collision
    if player.actor.colliderect(portal):
        if len(crystals) == 0:
            # Player wins!
            game_state = "won"
            stop_music()
            play_sound("victory")
        else:
            set_status("The portal is locked! You must collect all 5 crystals.", 1.5)


def draw():
    """Render screen based on current game state."""
    screen.fill((16, 14, 22))

    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_gameplay()
    elif game_state == "won":
        draw_won_screen()
    elif game_state == "lost":
        draw_lost_screen()


# =============================================================================
# DRAWING ROUTINES
# =============================================================================
def draw_menu():
    """Render the Main Menu."""
    screen.draw.filled_rect(Rect(50, 50, WIDTH - 100, HEIGHT - 100), (24, 22, 34))
    screen.draw.rect(Rect(50, 50, WIDTH - 100, HEIGHT - 100), (80, 70, 110))

    # Title & Subtitle
    screen.draw.text("DUNGEON ESCAPE", center=(WIDTH // 2, 130), fontsize=48, color=(240, 220, 140), owidth=1.5, ocolor=(20, 10, 30), fontname=FONT_TITLE)
    screen.draw.text("Find the crystals. Escape the dungeon.", center=(WIDTH // 2, 185), fontsize=20, color=(160, 175, 205), fontname=FONT_UI)

    # Buttons
    btn_start.draw()
    btn_sound.draw()
    btn_exit.draw()

    # Controls hint
    screen.draw.text("Controls: WASD or Arrow Keys to move", center=(WIDTH // 2, 510), fontsize=18, color=(120, 125, 145), fontname=FONT_UI)


def draw_gameplay():
    """Render dungeon room, tiles, entities, sparkles, and HUD with camera shake."""
    ox = shake_x
    oy = shake_y

    # 1. Tile dungeon floor
    tile_size = 64
    for y in range(80, 560, tile_size):
        for x in range(40, 760, tile_size):
            screen.blit("dungeon_floor", (x + ox, y + oy))

    # 2. Draw room boundary borders
    screen.draw.rect(Rect(40 + ox, 80 + oy, 720, 480), (70, 65, 90))
    screen.draw.rect(Rect(41 + ox, 81 + oy, 718, 478), (35, 30, 45))

    # 3. Draw obstacles (pillars)
    for obs in obstacles:
        old_pos = obs.pos
        obs.x += ox
        obs.y += oy
        obs.draw()
        obs.pos = old_pos

    # 4. Draw portal
    old_p = portal.pos
    portal.x += ox
    portal.y += oy
    portal.draw()
    portal.pos = old_p

    # 5. Draw crystals
    for crystal in crystals:
        old_c = crystal.pos
        crystal.x += ox
        crystal.y += oy
        crystal.draw()
        crystal.pos = old_c

    # 6. Draw sparkle particles
    draw_particles(ox, oy)

    # 7. Draw enemies
    for enemy in enemies:
        enemy.draw(ox, oy)

    # 8. Draw player
    player.draw(ox, oy)

    # 9. Top HUD Bar (Static, unaffected by screen shake)
    screen.draw.filled_rect(Rect(0, 0, WIDTH, 75), (20, 18, 28))
    screen.draw.line((0, 75), (WIDTH, 75), (60, 55, 80))

    # Lives display
    screen.draw.text(f"LIVES: {player.lives}/3", (40, 25), fontsize=24, color=(255, 60, 80), fontname=FONT_UI)
    # Visual health blocks
    for i in range(player.lives):
        screen.draw.filled_rect(Rect(180 + i * 24, 28, 16, 16), (255, 50, 70))
        screen.draw.rect(Rect(180 + i * 24, 28, 16, 16), (255, 180, 190))

    # Crystals collected counter
    collected = 5 - len(crystals)
    crystal_color = (60, 240, 255) if collected < 5 else (120, 255, 140)
    screen.draw.text(f"CRYSTALS: {collected}/5", center=(WIDTH // 2, 38), fontsize=24, color=crystal_color, fontname=FONT_UI)

    # Audio status indicator
    sound_txt = "AUDIO: ON" if sound_enabled else "AUDIO: OFF"
    screen.draw.text(sound_txt, topright=(WIDTH - 40, 28), fontsize=18, color=(140, 150, 175), fontname=FONT_UI)

    # Dynamic status message banner
    if status_message:
        screen.draw.text(status_message, center=(WIDTH // 2, 105), fontsize=20, color=(255, 230, 110), owidth=1, ocolor=(0, 0, 0), fontname=FONT_UI)


def draw_won_screen():
    """Render Victory Screen."""
    screen.draw.filled_rect(Rect(120, 100, 560, 400), (22, 35, 28))
    screen.draw.rect(Rect(120, 100, 560, 400), (60, 180, 90))

    screen.draw.text("DUNGEON ESCAPED!", center=(WIDTH // 2, 180), fontsize=42, color=(120, 255, 160), owidth=1.5, ocolor=(10, 40, 20), fontname=FONT_TITLE)
    screen.draw.text("Congratulations! You collected all 5 crystals", center=(WIDTH // 2, 240), fontsize=20, color=(220, 245, 230), fontname=FONT_UI)
    screen.draw.text("and safely escaped through the magical portal!", center=(WIDTH // 2, 275), fontsize=18, color=(170, 210, 190), fontname=FONT_UI)

    btn_play_again.draw()
    btn_main_menu.draw()


def draw_lost_screen():
    """Render Defeat / Game Over Screen."""
    screen.draw.filled_rect(Rect(120, 100, 560, 400), (35, 18, 22))
    screen.draw.rect(Rect(120, 100, 560, 400), (190, 50, 60))

    screen.draw.text("GAME OVER", center=(WIDTH // 2, 180), fontsize=48, color=(255, 70, 70), owidth=1.5, ocolor=(40, 10, 10), fontname=FONT_TITLE)
    screen.draw.text("You were defeated by the dungeon creatures.", center=(WIDTH // 2, 240), fontsize=20, color=(240, 190, 190), fontname=FONT_UI)
    screen.draw.text("Try to avoid the patrolling enemies!", center=(WIDTH // 2, 275), fontsize=18, color=(190, 160, 160), fontname=FONT_UI)

    btn_try_again.draw()
    btn_main_menu.draw()
