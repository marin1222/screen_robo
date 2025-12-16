import os
import sys
import random
import math
import time
import pygame
import serial

# =============================
#  環境変数・初期設定
# =============================
os.environ['SDL_AUDIODRIVER'] = 'directsound'

pygame.quit()
pygame.mixer.quit()

pygame.init()
pygame.mixer.init()

# =============================
#  Arduino シリアル接続
# =============================
SERIAL_PORT = "COM9"   # ★要変更
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2)
    print("Arduino connected")
except:
    ser = None
    print("Arduino not connected")

def send_to_arduino(ch):
    if ser:
        ser.write(ch.encode())

# =============================
#  画面設定
# =============================
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN.get_size()
pygame.display.set_caption("Cyber Mode")

CLOCK = pygame.time.Clock()
FPS = 60

DOT_FONT_SIZE = SCREEN_HEIGHT // 4
DOT_FONT = pygame.font.Font("PixelOperatorHB8.ttf", DOT_FONT_SIZE)

# =============================
#  色
# =============================
COLOR_WAITING = (120, 120, 120)
COLOR_EASY    = (0, 255, 255)
COLOR_HARD    = (255, 160, 0)
COLOR_EXTRA   = (255, 0, 0)
COLOR_PARTICLE = (0, 200, 255)

# =============================
#  モード
# =============================
MODE_WAITING = 0
MODE_EASY    = 1
MODE_HARD    = 2
MODE_EXTRA   = 3

# =============================
#  音楽
# =============================
pygame.mixer.music.load("8bit_Battle-With-Leaders.mp3")

# =============================
#  粒子
# =============================
class Particle:
    def __init__(self):
        self.reset(True)

    def reset(self, random_y=False):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT) if random_y else 0
        self.speed = random.uniform(2, 4)
        self.w = random.randint(2, 4)
        self.h = random.randint(6, 12)

    def update(self, mode):
        sp = self.speed + (3 if mode == MODE_EXTRA else 0)
        self.y += sp
        if self.y > SCREEN_HEIGHT:
            self.reset()

    def draw(self, surf, mode, sx, sy):
        color = COLOR_EXTRA if mode == MODE_EXTRA else COLOR_PARTICLE
        pygame.draw.rect(surf, color, (self.x + sx, self.y + sy, self.w, self.h))

particles = [Particle() for _ in range(80)]

# =============================
#  演出関数
# =============================
def fill_gradient(top, bottom):
    for y in range(SCREEN_HEIGHT):
        r = top[0] + (bottom[0]-top[0]) * y // SCREEN_HEIGHT
        g = top[1] + (bottom[1]-top[1]) * y // SCREEN_HEIGHT
        b = top[2] + (bottom[2]-top[2]) * y // SCREEN_HEIGHT
        pygame.draw.line(SCREEN, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def scanlines():
    line = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
    line.fill((0, 255, 255, 40))
    for y in range(0, SCREEN_HEIGHT, 4):
        SCREEN.blit(line, (0, y))

def glitch(mode, sx, sy):
    n = 15 if mode == MODE_EXTRA else 5
    color = COLOR_EXTRA if mode == MODE_EXTRA else (0, 255, 255)
    for _ in range(n):
        pygame.draw.rect(
            SCREEN, color,
            (random.randint(0, SCREEN_WIDTH)+sx,
             random.randint(0, SCREEN_HEIGHT)+sy,
             random.randint(40,200),
             random.randint(4,12))
        )

def draw_text(text, color, alpha, scale):
    surf = DOT_FONT.render(text, True, color)
    surf.set_alpha(alpha)
    w, h = int(surf.get_width()*scale), int(surf.get_height()*scale)
    surf = pygame.transform.smoothscale(surf, (w, h))
    SCREEN.blit(surf, (SCREEN_WIDTH//2-w//2, SCREEN_HEIGHT//2-h//2))

# =============================
#  メイン
# =============================
def main():
    mode = MODE_WAITING
    prev_mode = mode
    alpha = 0
    t = 0.0

    send_to_arduino('0')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_to_arduino('q')
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    send_to_arduino('q')
                    if ser: ser.close()
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_0:
                    mode = MODE_WAITING
                    send_to_arduino('0')
                    alpha = 0

                if event.key == pygame.K_1:
                    mode = MODE_EASY
                    send_to_arduino('1')
                    alpha = 0

                if event.key == pygame.K_2:
                    mode = MODE_HARD
                    send_to_arduino('2')
                    alpha = 0

                if event.key == pygame.K_3:
                    mode = MODE_EXTRA
                    send_to_arduino('3')
                    alpha = 0

        if mode != prev_mode:
            pygame.mixer.music.stop()
            if mode == MODE_EXTRA:
                pygame.mixer.music.play(-1)
            prev_mode = mode

        # 背景
        if mode == MODE_WAITING:
            fill_gradient((0,0,0),(20,20,20))
        elif mode == MODE_EASY:
            fill_gradient((0,30,60),(0,150,180))
        elif mode == MODE_HARD:
            fill_gradient((40,10,0),(160,60,0))
        else:
            fill_gradient((0,0,0),(80,0,0))

        sx = random.randint(-10,10) if mode == MODE_EXTRA else 0
        sy = random.randint(-10,10) if mode == MODE_EXTRA else 0

        for p in particles:
            p.update(mode)
            p.draw(SCREEN, mode, sx, sy)

        glitch(mode, sx, sy)

        alpha = min(255, alpha+5)
        scale = 1.0 + (0.1*math.sin(t) if mode == MODE_EXTRA else 0)

        text = ["WAITING","EASY","HARD","EXTRA"][mode]
        color = [COLOR_WAITING,COLOR_EASY,COLOR_HARD,COLOR_EXTRA][mode]
        draw_text(text, color, alpha, scale)

        scanlines()

        pygame.display.update()
        CLOCK.tick(FPS)
        t += 0.05

if __name__ == "__main__":
    main()
