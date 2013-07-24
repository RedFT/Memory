import pygame
import sys
import os
import random
import copy
from math import sin

# DEFINE CONSTANTS
BLACK = (1,21,28)
PURPLE = (119,11,48)
RED = (181,47,42)
ORANGE = (220,91,43)
YELLOW = (252,159,6)

WIN_SIZE = (900, 480)
CENTER = (WIN_SIZE[0]/2, WIN_SIZE[1]/2)

BOARD_SIZE = (WIN_SIZE[0] - 80, WIN_SIZE[1] - 40)

CARD_POINTS = [] # used to define where to place cards

FRAME_RATE = 120
GAME_NAME = 'MEMORY v0.2' # caption of the game

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

# PATH TO MUSIC AND SFX
BG_MUSIC = os.path.join('.', 'data', 'sounds', 'LearningToWalk.ogg')
SFX_REMOVE = os.path.join('.', 'data', 'sounds', 'RemoveCards.ogg')
SFX_THROW = os.path.join('.', 'data', 'sounds', 'ThrowCard.ogg')

# PATH TO FONT USED FOR GAME
FONT_DIR = os.path.join ('.', 'data', 'font', 'Comfortaa-Regular.ttf')


class Card(pygame.sprite.Sprite):
    """
    This class is used to create
    each card in the game

    Parameters: font, suit='clubs', clip=CLIP_CLUBS, pos=[WIN_SIZE[0]/2, WIN_SIZE[1]/2], number='2'
    """

    # 'blocked' KEEPS PLAYER FROM FLIPPING CARDS
    blocked = False

    done_throwing = True
    done_shuffling = True
    shuffling = False
    got_dest = True
    front_up = True
    sin_move = True

    end_dest = [0, 0]

    speed = 0

    elapsed = 0

    def __init__(self, font, suit='clubs', clip=CLIP_CLUBS, pos=[WIN_SIZE[0]/2, WIN_SIZE[1]/2], number='2'):

        super(Card, self).__init__()

        # LOAD THE SOUND USED WHEN THROWING A CARD
        # AND SET TO A LOW VOLUME (0.1)
        self.sfx_throw = pygame.mixer.Sound(SFX_THROW)
        self.sfx_throw.set_volume(0.1)

        self.suit = suit
        self.number = number
        self.pos = pos

        # USE RANDOM NUMBER FOR SPEED WHEN CARDS
        # COME TOGETHER
        self.gatherx = random.randint(45,85)
        self.gathery = random.randint(45,85)

        # MAKE CARDS MOVE AND SHAKE AT DIFFERENT SPEEDS
        self.elapsed = random.randint(0, 200) / 100.
        self.sinspeedx = random.randint(50, 75) / 100.
        self.sinspeedy = random.randint(100, 150) / 100.

        # LOAD IMAGES FOR CARDS
        self.card_front = pygame.image.load(CARD_FRONT).convert_alpha()
        self.card_back = pygame.image.load(CARD_BACK).convert_alpha()
        self.card_suits = pygame.image.load(CARD_SUITS).convert_alpha()

        # DRAW NUMBERS AND SUIT TO FACE OF CARD
        self.symbol = self.card_suits.subsurface(clip)
        self.rot_symbol = pygame.transform.rotate(self.symbol, 180)
        self.blitted_number= font.render(number, 0, BLACK).convert_alpha()
        self.rot_blitted_number= pygame.transform.rotate(self.blitted_number, 180)

        self.card_front.blit(self.symbol, (2, 15, 12, 12))
        self.card_front.blit(self.rot_symbol, (43, 70, 12, 12))


        # FOR CARDS NUMBERED 10-K USE SPECIAL COORDINATES
        # ON CARD SURFACE
        if self.blitted_number in ('10','J', 'Q', 'K'):
            self.card_front.blit(self.blitted_number, (0, 2))
            self.card_front.blit(self.rot_blitted_number, (46, 82))
        else:
            self.card_front.blit(self.blitted_number, (4, 2))
            self.card_front.blit(self.rot_blitted_number, (45, 82))

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

        self.gather_speed = self.get_needed_speed(CENTER, self.gatherx, self.gathery)

        self.pos[0] -= self.gather_speed[0]
        self.pos[1] -= self.gather_speed[1]

        if .1 > self.gather_speed[0] > -.1 and .1 > self.gather_speed[1] > -.1:

            # IF WE PLAY THE THROW SOUND IN throw()
            # IT WOULD PLAY EACH TIME throw() IS CALLED
            # SO WE PUT IT HERE AT THE END OF shuffle()
            # SO THAT IT'S PLAYED ONLY ONCE
            self.sfx_throw.play()
            self.done_shuffling = True
            self.done_throwing = False
            self.shuffling = False

    def throw(self):


        self.throw_speed = self.get_needed_speed(self.end_dest, 10, 10)

        self.pos[0] -= self.throw_speed[0]
        self.pos[1] -= self.throw_speed[1]

        if .11 > self.throw_speed[0] > -.11 and .11 > self.throw_speed[1] > -.11:
            self.pos = copy.copy(self.end_dest)
            self.done_throwing = True

    def get_needed_speed(self, dest, speedx, speedy):
        # Get distance to dest so all cards go to it
        x_dist = float(self.pos[0]) - dest[0]
        y_dist = float(self.pos[1]) - dest[1]
        vx = x_dist / speedx
        vy = y_dist / speedy
        return [vx, vy]

    def update(self):

        # SHUFFLE AND THROW IF CONDITIONS ARE TRUE
        if self.shuffling:
            self.shuffle()
        if self.done_shuffling and not self.done_throwing:
            self.throw()

        # FOR SINUSOIDAL MOVEMENT OF CARDS
        if self.sin_move:
            self.elapsed += .1
            self.pos[0] = (.125 * sin(self.elapsed * -self.sinspeedx)) + self.pos[0]
            self.pos[1] = (.125 * sin(self.elapsed) * self.sinspeedy) + self.pos[1]

        self.rect.x, self.rect.y = self.pos[0], self.pos[1]

class Deck():
    """
    This class creates and handles
    each card used in the game

    Parameters: font, clock
    """

    cards_up = 0

    timer = 0

    cards_in_center = []

    def __init__(self, font, clock):

        self.sfx_remove = pygame.mixer.Sound(SFX_REMOVE)

        self.card_list = pygame.sprite.Group()

        self.clock = clock

        self.font = font

        # CREATE ALL CARDS
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

                # CREATE THE CARD AND ADD TO A GROUP
                card = Card(self.font, suit, clip, pos=copy.copy(list(CENTER)), number=letter)
                self.card_list.add(card)

        # PLACE EACH CARD ON POINTS IN CARD_POINTS
        for card in enumerate(self.card_list):
            card[1].shuffling = True
            card[1].set_end_dest(copy.copy(CARD_POINTS[card[0]]))

    def flip(self, m_pos):

        # IF MOUSE ON CARD, FLIP
        for card in self.card_list:
            if card.rect.collidepoint(m_pos):
                    card.set_front()

    def shuffle(self):

        # random.shuffle() WORKS
        # BETTER WITH LISTS
        # SO UNPACK GROUP INTO A LIST
        card_list = []
        for card in self.card_list:
            card_list.append(card)
        random.shuffle(card_list)

        random.shuffle(CARD_POINTS)

        # SHUFFLE CARDS AND ASSIGN
        # WHERE TO SEND EACH CARD.
        # IF FACING UP, FLIP FACE DOWN.
        for card in enumerate(card_list):
            card[1].shuffling = True
            card[1].set_end_dest(copy.copy(CARD_POINTS[card[0]]))
            card[1].set_back()

        # REFILL THE self.card_list GROUP
        # SO THAT WE CAN USE GROUP FUNCTIONS
        # ON THE CARDS
        self.card_list.empty()
        for card in card_list:
            self.card_list.add(card)

    def update(self):

        # GET THE NUMBER OF CARDS THAT ARE FACING UP
        self.cards_up = sum(True for card in self.card_list if card.front_up)

        # WHEN THE NUMBER OF CARDS FACING UP IS 2,
        # AFTER HALF A SECOND, THE CARDS ARE EITHER
        # REMOVED OR FLIPPED FACE DOWN AND TIMER
        # IS RESET.
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
                    self.sfx_remove.play()
                    up_cards[0].kill()
                    up_cards[1].kill()

                else:
                    up_cards[0].set_back()
                    up_cards[1].set_back()
                self.timer = 0


class Game():
    """
    This is the main game class that
    handles player interaction, game
    logic and display
    """

    def __init__(self):

        # INIT AND SETUP PYGAME
        pygame.display.init()
        pygame.font.init()
        pygame.mixer.init()
        self.surface = pygame.display.set_mode(WIN_SIZE)
        pygame.display.set_caption(GAME_NAME)

        # SETUP FONT
        self.font = pygame.font.Font(FONT_DIR, 15)

        # AN FPS CLOCK TO KEEP TRACK OF FRAMERATE
        self.fps_clock = pygame.time.Clock()

        # SETUP GROUPS
        self.all_sprites_list = pygame.sprite.Group()

        # CREATE SOUND
        # Create BG music and play it
        self.bg_music = pygame.mixer.Sound(BG_MUSIC)
        self.bg_music.set_volume(0.5)
        self.bg_music.play(-1, 0)

        # FILL CARD_POINTS WITH POINTS
        for y in range(30, WIN_SIZE[1] - 20, BOARD_SIZE[1]/4):
            for x in range(12,WIN_SIZE[0] - 60, BOARD_SIZE[0]/12):
                CARD_POINTS.append([x, y])

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

            # IF CLICKED
            elif event.type == pygame.MOUSEBUTTONDOWN:

                # IF LEFT CLICKED
                if event.button == 1:

                    # FLIP CARD
                    self.deck.flip(pygame.mouse.get_pos())

            # IF KEY PRESSED
            elif event.type == pygame.KEYDOWN:

                # IF 'ESCAPE' WAS PRESSED
                if event.key == pygame.K_ESCAPE:

                    # CLOSE PYGAME AND sys.exit() FOR GOOD MEASURE
                    pygame.quit()
                    sys.exit()

                # IF 'SPACE' WAS PRESSED
                elif event.key == pygame.K_SPACE:

                    # SHUFFLE CARDS
                    self.deck.shuffle()

                # IF 'P' WAS PRESSED, RESET GAME
                elif event.key == pygame.K_p:
                    self.level_init()

    def update(self):
        """
        Update whatever needs to be updated
        """

        self.deck.update()
        self.all_sprites_list.update()

    def collisions(self):

        pass

    def clear_screen(self):
        """
        Sets the background and removes
        everything else from the screen
        """

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

if __name__ == "__main__":
    game = Game()
    game.mainLoop()
