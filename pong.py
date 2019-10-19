import pygame
import numpy as np
import sys

successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))

WIDTH, HEIGHT = 1920, 1080
FPS = 60  # Frames per second.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SPEED = 10
BAT_WEIGHT = 30
MENU_PAS = (180, 180, 180)
MENU_ACT = (200, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
# pygame.display.toggle_fullscreen()
clock = pygame.time.Clock()

# RED = (255, 0, 0), GREEN = (0, 255, 0), BLUE = (0, 0, 255).


class Bat(pygame.sprite.Sprite):
    def __init__(self, size, pos):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(WHITE)
        self.rect = pygame.Rect(pos, size)
        self.velocity = np.array([.0, .0])

    def update(self):
        self.rect.move_ip(self.velocity)
        if self.rect.y < 0:
            self.rect.move_ip(-self.velocity)
            self.velocity[1] = 0
        if self.rect.y > (HEIGHT-31):
            self.rect.move_ip(-self.velocity)
            self.velocity[1] = 0


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = pygame.Rect((WIDTH/2, HEIGHT/2), (10, 10))
        self.velocity = np.array([SPEED, np.random.randint(1, 5)])

    def collide_left(self):
        self.velocity = np.array([SPEED, np.random.randint(-SPEED, SPEED)])

    def collide_right(self):
        self.velocity = np.array([-SPEED, np.random.randint(-SPEED, SPEED)])

    def collide_ceil(self):
        self.velocity[1] = -self.velocity[1]

    def update(self):
        self.rect.move_ip(self.velocity)


left = Bat((10, 50), (0, HEIGHT-32))
right = Bat((10, 50), (WIDTH-10, HEIGHT-32))

right_up = False
left_up = False

ball = Ball()

points_left, points_right = 0, 0

font = pygame.font.SysFont("Consolas", 20, True, False)
font_menu = pygame.font.SysFont("Consolas", 30, False, True)

pause = True
mode = "pause"
last_mode = "duo"

hit = 0
missed = 0

while True:
    dt = clock.tick(FPS) / 1000

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                left_up = True
            elif event.key == pygame.K_KP9:
                right_up = True
            elif event.key == pygame.K_ESCAPE:
                mode = "pause"
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                left_up = False
            elif event.key == pygame.K_KP9:
                right_up = False

    # Dou Mode
    if mode == "duo":
        if right_up:
            right.velocity[1] -= BAT_WEIGHT*dt
        else:
            right.velocity[1] += BAT_WEIGHT*dt

        if ball.rect.colliderect(left.rect):
            ball.collide_left()
        elif ball.rect.colliderect(right.rect):
            ball.collide_right()

        if not 0 < ball.rect.y < HEIGHT-10:
            ball.collide_ceil()

        if ball.rect.x > WIDTH-10:
            points_left += 1
            ball.collide_right()
        elif ball.rect.x < 0:
            points_right += 1
            ball.collide_left()

        left.update()
        right.update()
        ball.update()

        scoreboard_left = font.render(str(points_left), True, MENU_ACT)
        scoreboard_right = font.render(str(points_right), True, MENU_ACT)

        pygame.mouse.set_visible(False)
        screen.fill(BLACK)
        screen.blit(left.image, left.rect)
        screen.blit(right.image, right.rect)
        screen.blit(ball.image, ball.rect)
        screen.blit(scoreboard_left, (20, 20))
        screen.blit(scoreboard_right, (WIDTH - 50, 20))

    # Solo Mode
    elif mode == "solo":
        if left_up:
            left.velocity[1] -= BAT_WEIGHT*dt
        else:
            left.velocity[1] += BAT_WEIGHT*dt

        if not 0 < ball.rect.y < HEIGHT-10:
            ball.collide_ceil()

        if ball.rect.colliderect(left.rect):
            ball.collide_left()
            hit += 1

        if ball.rect.x > WIDTH-10:
            ball.collide_right()
        elif ball.rect.x < 0:
            missed += 1
            ball.collide_left()

        ball.update()
        left.update()
        print(hit, missed)
        try:
            hit_ratio = hit / (hit+missed)
        except ZeroDivisionError:
            print("ZeroDivisionError")
            hit_ratio = 0
        hit_ratio_scoreboard = font.render("{}%".format(int(hit_ratio*100)), True, MENU_ACT)
        hit_scoreboard = font.render(str(hit), True, MENU_ACT)

        pygame.mouse.set_visible(False)
        screen.fill(BLACK)
        screen.blit(left.image, left.rect)
        screen.blit(ball.image, ball.rect)

        screen.blit(hit_scoreboard, (20, 20))
        screen.blit(hit_ratio_scoreboard, (20, 40))


    elif mode == "pause":
        screen.fill(BLACK)
        pygame.mouse.set_visible(True)
        x, y = pygame.mouse.get_pos()

        mouse_exit_pos = (50 < x < 200) and (50 < y < 80)
        mouse_continue_pos = (50 < x < 200) and (80 < y < 110)
        mouse_duo_pos = (50 < x < 200) and (110 < y < 140)
        mouse_solo_pos = (50 < x < 200) and (140 < y < 170)

        exit_button = font_menu.render("exit game", True, (MENU_ACT if mouse_exit_pos else MENU_PAS))
        continue_button = font_menu.render("continue", True, (MENU_ACT if mouse_continue_pos else MENU_PAS))
        duo_button = font_menu.render("new duo", True, (MENU_ACT if mouse_duo_pos else MENU_PAS))
        solo_button = font_menu.render("new solo", True, (MENU_ACT if mouse_solo_pos else MENU_PAS))

        if pygame.mouse.get_pressed()[0]:
            if mouse_exit_pos:
                pygame.quit()
                sys.exit()
            elif mouse_duo_pos:
                mode = "duo"
                last_mode = "duo"
                left = Bat((10, 50), (0, HEIGHT-32))
                right = Bat((10, 50), (WIDTH-10, HEIGHT-32))
                ball = Ball()
                points_left, points_right = 0, 0
            elif mouse_continue_pos:
                mode = last_mode
            elif mouse_solo_pos:
                mode = "solo"
                last_mode = "solo"
                hit, missed = 0, 0
                ball = Ball()
                left = Bat((10, 50), (0, HEIGHT-32))

        screen.blit(exit_button, (50, 50))
        screen.blit(continue_button, (50, 80))
        screen.blit(duo_button, (50, 110))
        screen.blit(solo_button, (50, 140))
    pygame.display.update()  # Or pygame.display.flip()