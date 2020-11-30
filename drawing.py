import pygame
from settings import *
from map import mini_map
from collections import deque
from random import randrange
import sys
import os

####------Colours------####
BLACK     = (  0,   0,   0)
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0,  64)
DARKGREY  = ( 64,  64,  64)
DARKRED   = ( 64,   0,   0)
WHITE     = (255, 255, 255)
RED = (255,0,0)
GREEN = (0,200,0)
BRIGHT_RED = (255,0,0)
BRIGHT_GREEN = (0,255,0)
####-------------------####

block_color = (53,115,255)


WIDTH    = 1360
HEIGHT   = 768

dirname = os.path.dirname(__file__)

class Drawing:
    def __init__(self, sc, sc_map, player, clock):
        self.sc = sc
        self.sc_map = sc_map
        self.player = player
        self.clock = clock
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_win = pygame.font.Font(os.path.join(dirname,'font/font.ttf'), 144)
        self.textures = {1: pygame.image.load(os.path.join(dirname,'img/wall6.png')).convert(),
                         2: pygame.image.load(os.path.join(dirname,'img/wall5.png')).convert(),
                         3: pygame.image.load(os.path.join(dirname,'img/wall3.png')).convert(),
                         4: pygame.image.load(os.path.join(dirname,'img/wall7.png')).convert(),
                         'S': pygame.image.load(os.path.join(dirname,'img/sky0.png')).convert(),
                         }
        # menu
        self.menu_trigger = True
        self.menu_picture = pygame.image.load(os.path.join(dirname,'img/wall7.png')).convert()
        # weapon parameters
        self.weapon_base_sprite = pygame.image.load(os.path.join(dirname,'sprites/weapons/shotgun/base/0.png')).convert_alpha()
        self.weapon_shot_animation = deque([pygame.image.load(os.path.join(dirname,f'sprites/weapons/shotgun/shot/{i}.png'))
                                 .convert_alpha() for i in range(20)])
        self.weapon_rect = self.weapon_base_sprite.get_rect()
        self.weapon_pos = (HALF_WIDTH - self.weapon_rect.width // 2, HEIGHT - self.weapon_rect.height)
        self.shot_length = len(self.weapon_shot_animation)
        self.shot_length_count = 0
        self.shot_animation_trigger = True
        self.shot_animation_speed = 3
        self.shot_animation_count = 0
        self.shot_sound = pygame.mixer.Sound(os.path.join(dirname,'sound/shotgun.wav'))
        # shot SFX
        self.sfx = deque([pygame.image.load(os.path.join(dirname,f'sprites/weapons/sfx/{i}.png')).convert_alpha() for i in range(9)])
        self.sfx_length_count = 0
        self.sfx_length = len(self.sfx)

    def background(self):
        sky_offset = -10 * math.degrees(self.player.angle) % WIDTH
        self.sc.blit(self.textures['S'], (sky_offset, 0))
        self.sc.blit(self.textures['S'], (sky_offset - WIDTH, 0))
        self.sc.blit(self.textures['S'], (sky_offset + WIDTH, 0))
        pygame.draw.rect(self.sc, DARKGRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))


    def world(self, world_objects):
        for obj in sorted(world_objects, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, object_pos = obj
                self.sc.blit(object, object_pos)



    def win(self):
        render = self.font_win.render('YOU WIN!!!', 1, (randrange(40, 120), 0, 0))
        rect = pygame.Rect(0, 0, 1000, 300)
        rect.center = HALF_WIDTH, HALF_HEIGHT
        pygame.draw.rect(self.sc, BLACK, rect, border_radius=50)
        self.sc.blit(render, (rect.centerx - 430, rect.centery - 140))
        pygame.display.flip()
        self.clock.tick(15)

    def text_objects(self,text, font, color=BLACK):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()  

    def message(self, message,  font_size, x, y, color):
        largeText = pygame.font.SysFont("comicsansms",font_size, color)
        TextSurf, TextRect = self.text_objects(message, largeText, color)
        TextRect.center = (x,y)
        self.sc.blit(TextSurf, TextRect)

    def mini_map(self):
        self.sc_map.fill(BLACK)
        map_x, map_y = self.player.x // MAP_SCALE, self.player.y // MAP_SCALE
        pygame.draw.line(self.sc_map, YELLOW, (map_x, map_y), (map_x + 8 * math.cos(self.player.angle),
                                                               map_y + 8 * math.sin(self.player.angle)), 2)
        pygame.draw.circle(self.sc_map, RED, (int(map_x), int(map_y)), 4)
        for x, y in mini_map:
            pygame.draw.rect(self.sc_map, DARKBROWN, (x, y, MAP_TILE, MAP_TILE))
        self.sc.blit(self.sc_map, MAP_POS)

    def player_weapon(self, shot_projections):
        if self.player.shot:
            if not self.shot_length_count:
                self.shot_sound.play()
            self.shot_projection = min(shot_projections)[1] // 2
            self.bullet_sfx()
            shot_sprite = self.weapon_shot_animation[0]
            self.sc.blit(shot_sprite, self.weapon_pos)
            self.shot_animation_count += 1
            if self.shot_animation_count == self.shot_animation_speed:
                self.shot_animation_count = 0
                self.shot_length_count += 1
                self.shot_animation_trigger = False
            if self.shot_length_count == self.shot_length:
                self.player.shot = False

                self.shot_length_count = 0
                self.sfx_length_count = 0
                self.shot_animation_trigger = True
        else:
           self.sc.blit(self.weapon_base_sprite, self.weapon_pos)

    def bullet_sfx(self):
        if self.sfx_length_count < self.sfx_length:
            sfx = pygame.transform.scale(self.sfx[0], (self.shot_projection, self.shot_projection))
            sfx_rect = sfx.get_rect()
            self.sc.blit(sfx, (HALF_WIDTH - sfx_rect.width // 2, HALF_HEIGHT - sfx_rect.height // 2))
            self.sfx_length_count += 1
            self.sfx.rotate(-1)

    def hud(self):
            self.message(" w to move up, s to move down, a to move left, d to move right.", 30,(WIDTH/2-50),HEIGHT-70, WHITE)

    def menu(self):
        x = 0
        #pygame.mixer.music.load(os.path.join(dirname,'sound/win.mp3'))
        #pygame.mixer.music.play()
        button_font = pygame.font.Font(os.path.join(dirname,'font/font.ttf'), 72)
        label_font = pygame.font.Font(os.path.join(dirname,'font/font1.otf'), 400)
        start = button_font.render('START', 1, pygame.Color('lightgray'))
        button_start = pygame.Rect(0, 0, 400, 150)
        button_start.center = HALF_WIDTH, HALF_HEIGHT
        exit = button_font.render('EXIT', 1, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, 400, 150)
        button_exit.center = HALF_WIDTH, HALF_HEIGHT + 200

        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            x += 1

            pygame.draw.rect(self.sc, BLACK, button_start, border_radius=25, width=10)
            self.sc.blit(start, (button_start.centerx - 130, button_start.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25, width=10)
            self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))


            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if button_start.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_start, border_radius=25)
                self.sc.blit(start, (button_start.centerx - 130, button_start.centery - 70))
                if mouse_click[0]:
                    self.menu_trigger = False
            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25)
                self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(20)






