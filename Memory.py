import pygame
import os
import sys
import random
import copy
from math import sin, cos

# DEFINE CONSTANTS
BLACK = (1,21,28)
PURPLE = (119,11,48)
RED = (181,47,42)
ORANGE = (220,91,43)
YELLOW = (252,159,6)

WIN_SIZE = (900, 480)
CENTER = (WIN_SIZE[0]/2, WIN_SIZE[1]/2)

BOARD_SIZE = (WIN_SIZE[0] - 80, WIN_SIZE[1] - 40)
CARD_POINTS = []

for y in range(30, WIN_SIZE[1] - 20, BOARD_SIZE[1]/4):
    for x in range(12,WIN_SIZE[0] - 60, BOARD_SIZE[0]/12):
        CARD_POINTS.append([x, y])

FRAME_RATE = 120
GAME_NAME = 'MEMORY v0.1'

# PATH TO EACH PICTURES
CARD_FRONT = os.path.join('.', 'data', 'images', 'card_front.png')
CARD_BACK = os.path.join('.', 'data', 'images', 'card_back.png')
CARD_SUITS = os.path.join('.', 'data', 'images', 'card_suits25x30.png')
WOODEN_TOP = os.path.join('.', 'data', 'images', 'wooden_top.png')

# CLIPS FOR EACH SUIT
CLIP_CLUBS = (0, 0, 12, 15)
CLIP_DIAMONDS = (13, 0, 12, 15)
CLIP_HEARTS = (0, 15, 13, 15)
CLIP_SPADES = (13, 15, 12, 15)

# PATH TO FONT USED FOR GAME
FONT_DIR = os.path.join ('.', 'data', 'font', 'Comfortaa-Regular.ttf')

class Card(pygame.sprite.Sprite):

    blocked = False

    done_throwing = True
    done_shuffling = True
    shuffling = False
    got_dest = True
    front_up = True

    speed = 0

    elapsed = 0

    def __init__(self, font, suit='clubs', clip=CLIP_CLUBS, pos=[WIN_SIZE[0]/2, WIN_SIZE[1]/2], number='2'):

        super(Card, self).__init__()

        self.suit = suit
        self.number = number
        self.pos = pos
        self.end_dest = [0, 0]

        self.gatherx = random.randint(45,85)
        self.gathery = random.randint(45,85)

        self.elapsed = random.randint(0, 200) / 100.
        self.sinspeedx = random.randint(500, 750) / 1000.
        self.sinspeedy = random.randint(1000, 1500) / 1000.

        self.card_front = pygame.image.load(CARD_FRONT).convert_alpha()
        self.card_back = pygame.image.load(CARD_BACK).convert_alpha()
        self.card_suits = pygame.image.load(CARD_SUITS).convert_alpha()

        self.symbol = self.card_suits.subsurface(clip)
        self.rot_symbol = pygame.transform.rotate(self.symbol, 180)
        self.blitted_number= font.render(number, 0, BLACK).convert_alpha()
        self.rot_blitted_number= pygame.transform.rotate(self.blitted_number, 180)

        self.card_front.blit(self.symbol, (2, 15, 12, 12))
        self.card_front.blit(self.rot_symbol, (43, 70, 12, 12))

        if self.blitted_number in ('10','J', 'Q', 'K'):
            self.card_front.blit(self.blitted_number, (5, 2))
            self.card_front.blit(self.rot_blitted_number, (46, 85))
        else:
            self.card_front.blit(self.blitted_number, (4, 2))
            self.card_front.blit(self.rot_blitted_number, (45, 85))

        self.rect = self.card_front.get_rect()
        self.rect.x, self.rect.y = self.pos[0], self.pos[1]

        self.set_front()

    def set_front(self):
        if not self.blocked:
            self.image = self.card_front
            self.front_up = True

    def set_back(self):
        if not self.blocked:
            self.image = self.card_back
            self.front_up = False

    def set_end_dest(self, end_dest):
        self.end_dest = end_dest

    def shuffle(self):
        self.done_shuffling = False
        self.done_throwing = True

        self.pos[0] -= self.gather_speed[0]
        self.pos[1] -= self.gather_speed[1]

        if not (self.gather_speed[0] or self.gather_speed[1]):
            self.done_shuffling = True
            self.done_throwing = False
            self.shuffling = False

    def throw(self):
        self.pos[0] -= self.throw_speed[0]
        self.pos[1] -= self.throw_speed[1]

        if .11 > self.throw_speed[0] > -.11 or .11 > self.throw_speed[1] > -.11:
            self.pos = copy.copy(self.end_dest)
            self.done_throwing = True

    def get_dist_center(self):
        # Get distance to thing so all cards go to it
        x_dist = int(self.pos[0]) - CENTER[0]
        y_dist = int(self.pos[1]) - CENTER[1]
        vx = x_dist / self.gatherx
        vy = y_dist / self.gathery
        return [vx, vy]

    def get_dist_end(self):
        # Get distance to thing so all cards go to it
        x_dist = float(self.pos[0]) - self.end_dest[0]
        y_dist = float(self.pos[1]) - self.end_dest[1]
        vx = x_dist / 10
        vy = y_dist / 10
        return [vx, vy]

    def update(self):
        if self.shuffling:
            self.gather_speed = self.get_dist_center()
            self.shuffle()
        if self.done_shuffling and not self.done_throwing:
            self.throw_speed = self.get_dist_end()
            self.throw()

        # for sinusoidal movement of the cards
        self.elapsed += .1
        self.pos[0] = (.125 * sin(self.elapsed * -self.sinspeedx)) + self.pos[0]
        self.pos[1] = (.125 * sin(self.elapsed) * self.sinspeedy) + self.pos[1]

        self.rect.x, self.rect.y = self.pos[0], self.pos[1]

class Deck():

    cards_up = 0

    def __init__(self, font, clock):

        self.card_list = pygame.sprite.Group()

        self.clock = clock
        self.timer = 0

        self.font = font

        # CREATE ALL CLUBS CARDS
        for i in range(0, 4):
            if not i:
                clip = CLIP_CLUBS
                suit = 'clubs'
            elif i == 1:
                clip = CLIP_DIAMONDS
                suit = 'diamonds'
            elif i == 2:
                clip = CLIP_HEARTS
                suit = 'hearts'
            elif i == 3:
                clip = CLIP_SPADES
                suit = 'spades'

            for n in range(1, 14):
                if n == 1:
                    letter = 'A'
                elif n == 11:
                    letter = 'J'
                elif n == 12:
                    letter = 'Q'
                elif n == 13:
                    letter = 'K'
                else:
                    letter = str(n)

                card = Card(self.font, suit, clip, pos=copy.copy(list(CENTER)), number=letter)
                self.card_list.add(card)
        for card in enumerate(self.card_list):
            card[1].shuffling = True
            card[1].set_end_dest(copy.copy(CARD_POINTS[card[0]]))

    def flip(self, m_pos):
        for card in self.card_list:
            if card.rect.collidepoint(m_pos):
                    card.set_front()

    def shuffle(self):
        card_list = []
        for card in self.card_list:
            card_list.append(card)
        random.shuffle(card_list)
        self.card_list.empty()
        for card in card_list:
            self.card_list.add(card)

        for card in enumerate(self.card_list):
            card[1].shuffling = True
            card[1].set_end_dest(copy.copy(CARD_POINTS[card[0]]))
            card[1].set_back()

    def update(self):
        self.cards_up = sum(True for card in self.card_list if card.front_up)
        if self.cards_up == 2:
            self.timer += self.clock.get_time()
            for card in self.card_list:
                card.blocked = True
            up_cards = []
            for card in self.card_list:
                if card.front_up:
                    up_cards.append(card)

            if self.timer > 500:
                for card in self.card_list:
                    card.blocked = False
                if up_cards[0].number == up_cards[1].number:
                    up_cards[0].kill()
                    up_cards[1].kill()

                else:
                    up_cards[0].set_back()
                    up_cards[1].set_back()
                self.timer = 0

    def draw(self):
        pass


class Game():
    '''
    This is the main game class that
    handles player interaction, game
    logic and display
    '''

    def __init__(self):

        # INIT AND SETUP PYGAME
        pygame.init()
        self.surface = pygame.display.set_mode(WIN_SIZE)
        pygame.display.set_caption(GAME_NAME)

        # SETUP FONT
        self.font = pygame.font.Font(FONT_DIR, 15)

        # AN FPS CLOCK TO KEEP TRACK OF FRAMERATE
        self.fps_clock = pygame.time.Clock()

        # SETUP GROUPS
        self.all_sprites_list = pygame.sprite.Group()

    def level_init(self):

        # EMPTY ALL GROUPS
        self.all_sprites_list.empty()

        # CREATE ALL NECESSARY GAME OBJECTS
        self.wooden_top = pygame.image.load(WOODEN_TOP).convert()
        self.deck = Deck(self.font, self.fps_clock)

        for card in self.deck.card_list:
            self.all_sprites_list.add(card)

    def handle_events(self):

        # HANDLE KEYBOARD EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    self.deck.flip(pygame.mouse.get_pos())

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_SPACE:
                    self.deck.shuffle()

                elif event.key == pygame.K_p:
                    self.level_init()

    def update(self):

        self.deck.update()
        self.all_sprites_list.update()

    def collisions(self):

        pass

    def clear_screen(self):

        self.surface.blit(self.wooden_top, (0,0))

    def draw(self):

        self.all_sprites_list.draw(self.surface)

    def mainLoop(self):

        self.level_init()

        while True:

            # HANDLE KEYBOARD EVENTS
            self.handle_events()

            # HANDLE GAME LOGIC
            self.update()
            self.collisions()

            # CLEAR SCREEN
            self.clear_screen()

            # DISPLAY TO SCREEN
            self.draw()

            pygame.display.update()
            self.fps_clock.tick(FRAME_RATE)

game = Game()
game.mainLoop()
