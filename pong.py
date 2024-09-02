import pygame
from pygame import Surface
from typing import List
import random
import serial

import threading

pygame.init()

WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7
SCORE_FONT = pygame.font.SysFont("comicsans", 50)

DYNAMIC_BALL_COLOR = True

SERIAL_PORT = "/dev/ttyUSB0"

pygame.display.set_caption("Pong")

class GameColor:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)

# TODO: set the type of the variables
# TODO: refactor the colloion function


class Paddle:

    COLOR = GameColor.WHITE
    VEL = 4

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self, win: Surface) -> None:
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))
    
    def move(self, up: bool = True, vel: int = 0):
        if up:
            if self.y > 0:
                self.y -= (self.VEL + vel)
        else:
            if self.y < HEIGHT - self.height:
                self.y += (self.VEL + vel)
    

class Ball:

    MAX_VEL = 5

    def __init__(self, x, y, radius, color):
        self.x = self.og_x = x
        self.y = self.og_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0
        self.color = self.og_color = color
    

    def draw(self, win: Surface) -> None:
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
    
    def reset(self):
        self.x = self.og_x
        self.y = self.og_y
        self.y_vel = 0
        self.x_vel *= -1
        self.color = self.og_color





def draw(win: Surface, paddles: List[Paddle], ball: Ball, score: tuple) -> None:
    win.fill(GameColor.BLACK)

    left_score_text = SCORE_FONT.render(f"{score[0]}", 1, GameColor.WHITE)
    right_score_text = SCORE_FONT.render(f"{score[1]}", 1, GameColor.WHITE)
    
    win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text, (WIDTH * (3/4) + right_score_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)
    
    # draw a dotted line
    for i in range(10, HEIGHT, HEIGHT//20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, GameColor.WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

    ball.draw(win)
    pygame.display.update()


def handle_paddle_movement(keys, left_paddle: Paddle, right_paddle: Paddle) -> None:

    # movement for the left paddle
    if keys[pygame.K_w]:
        left_paddle.move(up=True)
    if keys[pygame.K_s]:
        left_paddle.move(up=False)
    
    # movement for the right paddle
    if keys[pygame.K_UP]:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN]:
        right_paddle.move(up=False)


def serial_paddle_movement(paddle: Paddle, stop) -> None:
    # init serial connection
    print("---> init serial...")
    with serial.Serial(port=SERIAL_PORT, baudrate=9600) as ser:
        while True:
            if stop():
                break
            instruction = int(ser.readline().decode("utf-8").strip())

            if instruction == -1:
                paddle.move(up=True, vel=20)
            elif instruction == 0:
                # do nothing
                pass
            elif instruction == 1:
                paddle.move(up=False, vel=20)
    


def get_random_color() -> tuple:
    ball_colors = [GameColor.WHITE, GameColor.RED, GameColor.BLUE, GameColor.GREEN, GameColor.CYAN, GameColor.YELLOW]
    return ball_colors[random.randint(0, len(ball_colors))-1]



def handle_collision(ball, left_paddle, right_paddle) -> None:
    if ball.y + ball.radius >= HEIGHT:
        ball.y_vel *= -1
    elif ball.y - ball.radius <= 0:
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                ball.x_vel *= -1

                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
                ball.color = get_random_color()
    else:
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_vel *= -1
                
                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
                ball.color = get_random_color()
                



def main():
    run = True
    clock = pygame.time.Clock()

    # paddles
    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS, GameColor.WHITE)

    # score
    left_score = 0
    right_score = 0

    # start serial read in thread
    stop_thread = False
    thread = threading.Thread(target=serial_paddle_movement, args=(left_paddle, lambda: stop_thread, ))
    thread.start()

    # serial_paddle_movement()

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, (left_score, right_score))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        keys = pygame.key.get_pressed()
        
        handle_paddle_movement(keys, left_paddle, right_paddle)
        handle_collision(ball, left_paddle, right_paddle)
        ball.move()

        if ball.x <= 0:
            right_score += 1
            ball.reset()
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()

    
    pygame.quit()
    stop_thread = True
    thread.join()



if __name__ == "__main__":
    main()


