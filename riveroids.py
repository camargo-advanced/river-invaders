#TODO: add player lives


import pygame
import pgzrun
from random import randint
from enum import Enum

# Screen dimensions
WIDTH = 1024
HEIGHT = 768
TITLE = "Riveroids"
# Speed is in pixels per second
BG_SPEED = 90
SHIP_SPEED = 350
ENEMY_SPEED = 90
BULLET_SPEED = 900
# Max bullets on screen simultaneously
MAX_BULLETS = 3
# River borders
LEFT = 80
RIGHT = 935
# Score required to level up
NEXT_LEVEL_SCORE = 3000


class Background():
    def __init__(self, images):
        # Create 2 actors to represent the first background which will be shown once,
        # and the second background which will be repeated forever.
        self.bgs = [Actor(images[0]), Actor(images[1])]
        
        # Both images should have the same dimensions
        if self.bgs[0].height != self.bgs[1].height:
            raise TypeError("Images should have the same height.")
        if self.bgs[0].width != self.bgs[1].width:
            raise TypeError("Images should have the same width.")
        self.height = self.bgs[0].height
        self.reset()

    def reset(self):
        self.bottom = 0
        self.offset = 0
        self.first = True

    def update(self, dt):
        dy = game.bg_speed * dt
        
        # Speed boost based on user input
        if keyboard.up:
            dy = 2 * game.bg_speed * dt
        elif keyboard.down:
            dy = 1 / 2 * game.bg_speed * dt

        # Calculate space travelled between frames to update ship position
        self.offset += dy
        if self.offset >= self.height:
            self.offset = self.offset - self.height
            self.first = False

    def draw(self):
        # Draw the first background once, and the second one, forever.
        if self.first:
            screen.blit(self.bgs[0]._surf, (0, self.offset))
        else:
            screen.blit(self.bgs[1]._surf, (0, self.offset))
        screen.blit(self.bgs[1]._surf, (0, -self.height + self.offset))


class Ship(Actor):
    def __init__(self, images, **kwargs):
        super().__init__(images["regular"], **kwargs)
        self.images = images
        self.reset()
        
    def reset(self):
        self.image = self.images["regular"]
        self.x = WIDTH / 2
        self.bottom = HEIGHT - 50
        self.hit = False

    def update(self, dt):
        if self.hit:
            self.image = self.images["damaged"]
            return

        # Update ship position based on user input
        dx = SHIP_SPEED * dt
        if keyboard.right:
            self.x += dx
            self.image = self.images["right"]
        elif keyboard.left:
            self.x -= dx
            self.image = self.images["left"]
        else:
            self.image = self.images["regular"]
        self.centerx = self.x


class Enemy(Actor):
    def __init__(self, image, points=0, x_boundaries=(0,0), pos=(0,0), **kwargs):
        super().__init__(image, **kwargs)
        self.points = points
        self.x_boundaries = x_boundaries
        self.x, self.y = pos
        self.direction = 1

    def update(self, dt):
        # Update y coordinate
        dy = game.bg_speed * dt 
        # Speed boost based on user input
        if keyboard.up:
            dy = 2 * game.bg_speed * dt
        elif keyboard.down:
            dy = 1 / 2 * game.bg_speed * dt
        self.y += dy
        
        # Update x coordinate
        dx = ENEMY_SPEED * dt * self.direction
        self.x += dx

        # Apply change to object
        self.pos = (self.x, self.y)

        # Change fleet direction
        if self.x > self.x_boundaries[1] or self.x < self.x_boundaries[0]:
            self.direction = -self.direction        

class Bullet(Actor):
    def __init__(self, image, pos, **kwargs):
        super().__init__(image, pos, **kwargs)
        self.pos = pos

    def update(self, dt):
        dy = BULLET_SPEED * dt
        self.y -= dy


# Create a fleet of enemies, at left or right, at random times and forever
def create_enemies():
    # This specific enemy object is used as a template only
    enemy_index = randint(0, len(game.enemies_catalog) - 1)
    enemy = Enemy(game.enemies_catalog[enemy_index]["image"])
    
    # Calculates parameters to be used during enemy creation
    width = enemy.width
    height = enemy.height
    padding_x = enemy.width * 0.3 
    padding_y = enemy.height * 0.3
    rows, columns = 3, 2

    # Create the fleet at left or right?
    side = randint(0,1)
    if side == 0:
        x_boundaries = (LEFT + 50, 2 / 5 * WIDTH)
    else:
        x_boundaries = (3 / 5 * WIDTH, RIGHT - 50)
    y = -2 * (enemy.height + padding_y)
    
    # Create a matrix of enemies
    if game.elapsed_time > game.next_enemy_creation:
        for i in range (0, rows):
            for j in range (0, columns):
                pos = (x_boundaries[0] + i * (width + padding_x),
                       y + j * (height + padding_y))
                image = game.enemies_catalog[enemy_index]["image"]
                points = int(game.enemies_catalog[enemy_index]["points"])
                game.enemies.append(Enemy(image, points, x_boundaries, pos))
        game.next_enemy_creation = game.elapsed_time + randint(3, 5)
           
def clean_up():
    # Remove enemies that are out of sight
    # and penalizes player for not destroying them
    for enemy in game.enemies.copy():
        if enemy.y > HEIGHT + 50:
            game.enemies.remove(enemy)

    # Remove bullets that are out of sight
    for bullet in game.bullets.copy():
        if bullet.y < 50:
            game.bullets.remove(bullet)

def check_ship_collision():
    # check for colision with enemies
    index = game.ship.collidelist(game.enemies)
    if index != -1: 
        game.ship.hit = True
        game.enemies.remove(game.enemies[index])
    # check collisions with river borders
    elif game.ship.right > RIGHT or game.ship.left < LEFT:
        game.ship.hit = True

    if game.ship.hit:
        game.lives -= 1
        sounds.explosion.play()
        game.stage = GameStage.hold
        clock.schedule_unique(unhit_ship, 1.0)

def check_bullets_collision():
    # check for colision with enemies
    for bullet in game.bullets.copy():
        #collisions = bullet.collidelistall(game.enemies)
        index = bullet.collidelist(game.enemies)
        if index != -1:
            sounds.collect.play()
            game.total_score += game.enemies[index].points
            game.level_score += game.enemies[index].points
            game.enemies.remove(game.enemies[index])
            game.bullets.remove(bullet)
    
# Control keyboard actions based on keydown event
def on_key_down():
    if game.stage is GameStage.ready:
        if keyboard.space:
            start_game()
    elif game.stage is GameStage.game:
        if keyboard.space:
            if len(game.bullets) < MAX_BULLETS:
                sounds.laser.play()
                game.bullets.append(Bullet("laser-red-7.png", game.ship.pos))

# event hooks
def start_game():
    game.stage = GameStage.game

def game_ready():
    game.stage = GameStage.ready

def unhit_ship():
    game.ship.centerx = WIDTH / 2
    game.stage = GameStage.game
    game.ship.hit = False

def next_level():
    game.level_score = 0
    game.bg_speed *= 1.15
    game.stage = GameStage.game
    game.level_up_voice_played = False

def reset_game():
    game.stage = GameStage.start
    game.bullets.clear()
    game.enemies.clear()
    game.go_voice_played = False
    game.level_up_voice_played = False
    game.game_over_voice_played = False
    game.bg_speed = BG_SPEED
    game.next_enemy_creation = 1.0
    game.elapsed_time = 0.0
    game.level = 1
    game.level_score = 0
    game.total_score = 0
    game.lives = 3
    game.bg.reset()
    game.ship.reset() 
    clock.schedule_unique(game_ready, 3.0)

# Update physics
def update(dt):
    game.elapsed_time += dt
    if game.stage == GameStage.start:
        game.bg.update(dt)

    elif game.stage == GameStage.game:
        check_ship_collision()   
        check_bullets_collision() 
        game.bg.update(dt)
        create_enemies()
        for enemy in game.enemies:
            enemy.update(dt)
        for bullet in game.bullets:
            bullet.update(dt)
        game.ship.update(dt)
        clean_up()

        # Level up - increases speed of background
        if game.level_score > NEXT_LEVEL_SCORE:
            game.stage = GameStage.level_complete
            game.level += 1
            clock.schedule_unique(next_level, 1.0)

        if game.lives == 0:
            game.stage = GameStage.game_over
            clock.schedule_unique(reset_game, 1.0)

# Draw objects
def draw():
    screen.clear()
    game.bg.draw()
    game.ship.draw()       
    for enemy in game.enemies:
        enemy.draw()
    for bullet in game.bullets:
        bullet.draw()
    
    # Press SPACE to start and also play GO sound
    if game.stage == GameStage.ready:
        screen.draw.text(
            'Press SPACE to start',
            center=(WIDTH / 2, HEIGHT / 4),
            color='white',
            fontsize=70
        )
        if not game.go_voice_played: 
            sounds.go.play()
            game.go_voice_played = True
    
    # Draw score and lives
    elif game.stage == GameStage.game:
        screen.draw.text(
            f"{round(game.total_score):,}" ,
            midtop=(WIDTH / 2, 30),
            color='white',
            fontsize=70
        )
        if game.lives > 1: text = f"{game.lives} lives"
        else: text = f"{game.lives} life"
        screen.draw.text(
            text,
            center=(game.ship.centerx, HEIGHT - 30),
            color='white',
            fontsize=30
        )
        
    # Level up message and sound
    elif game.stage == GameStage.level_complete:
        screen.draw.text(
            f"Level {game.level} !",
            center=(WIDTH / 2, HEIGHT / 4),
            color='white',
            fontsize=70
        )
        if not game.level_up_voice_played: 
            sounds.level_up.play()
            game.level_up_voice_played = True
    
    # Game over
    elif game.stage == GameStage.game_over:
        screen.draw.text(
            f"{round(game.total_score):,}",
            midtop=(WIDTH / 2, 30),
            color='white',
            fontsize=110
        )
        screen.draw.text(
            "Game Over !",
            center=(WIDTH / 2, HEIGHT / 4),
            color='white',
            fontsize=70
        )
        if not game.game_over_voice_played: 
            sounds.game_over.play()
            game.game_over_voice_played = True

class GameStage(Enum):
    start = 0
    ready = 1
    game = 2
    hold = 3
    level_complete = 4
    game_over = 5

class GameState():
    stage = GameStage.start
    bullets = []
    enemies = []
    enemies_catalog = []
    go_voice_played = False
    level_up_voice_played = False
    game_over_voice_played = False
    bg_speed = BG_SPEED
    next_enemy_creation = 1.0
    elapsed_time = 0.0
    level = 1
    level_score = 0
    total_score = 0
    lives = 3
    bg = Background(["rrbg1.gif", "rrbg2.gif"])
    ship = Ship({"regular":"ship.png", "right":"shipr.png", "left":"shipl.png", "damaged":"damaged.png"})
    enemies_catalog = [
        {"image":"enemy-red.png", "points": 150}, 
        {"image":"enemy-green.png", "points": 100}, 
        {"image":"enemy-ship-yellow-maned.png", "points": 200}, 
        {"image":"enemy-ship-blue-maned.png", "points": 250}, 
        {"image":"enemy-ship-pink-maned.png", "points": 170}, 
        {"image":"meteor-brown-med.png", "points": 300}, 
    ] 

# Main program
game = GameState()
reset_game()
pgzrun.go()
