import pygame, sys, random, os

# 音声デバイスを ALSA に明示
os.environ['SDL_AUDIODRIVER'] = 'alsa'

pygame.init()
pygame.mixer.init()  # サウンド初期化

# フルスクリーンで画面作成
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Cyber Mode Fullscreen Dot Text")

# 大きめドットフォント（画面サイズに応じて調整）
dot_font_size = screen_height // 4  # 高さの4分の1くらい
dot_font = pygame.font.Font("PixelOperatorHB8.ttf", dot_font_size)

# 音楽ロード
pygame.mixer.music.load("Warning-Siren04-01(Low-Mid).mp3")

# 初期設定
mode = 0
prev_mode = 0  # 前回のモード記録
alpha = 0
clock = pygame.time.Clock()

# 粒子（シャープ矩形）
particles = [{"x": random.randint(0, screen_width),
              "y": random.randint(0, screen_height),
              "speed": random.uniform(2, 4),
              "w": random.randint(2, 4),
              "h": random.randint(6, 12)}
             for _ in range(80)]

def draw_dot_text(text, color):
    return dot_font.render(text, True, color)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_1: mode = 1; alpha = 0
            elif event.key == pygame.K_2: mode = 2; alpha = 0
            elif event.key == pygame.K_3: mode = 3; alpha = 0
            elif event.key == pygame.K_0: mode = 0; alpha = 0

    # モード切替時にだけ音再生
    if mode != prev_mode:
        pygame.mixer.music.stop()
        if mode == 1:
            pygame.mixer.music.stop() # 1回だけ再生
        elif mode == 2:
            pygame.mixer.music.stop()  # 1回だけ再生
        elif mode == 3:
            pygame.mixer.music.play(0)  # ループ再生
    prev_mode = mode

    screen.fill((0, 0, 0))
    shake_x, shake_y = 0, 0

    # 粒子描画
    for p in particles:
        speed = p["speed"]
        color = (0, 200, 255)
        if mode == 3:
            speed += random.uniform(2, 4)
            color = (255, 0, 0)
            shake_x = random.randint(-10, 10)
            shake_y = random.randint(-10, 10)

        pygame.draw.rect(screen, color,
                         (int(p["x"]) + shake_x, int(p["y"]) + shake_y, p["w"], p["h"]))
        p["y"] += speed
        if p["y"] > screen_height:
            p["y"] = 0
            p["x"] = random.randint(0, screen_width)
            p["w"] = random.randint(2, 4)
            p["h"] = random.randint(6, 12)

    # グリッチ矩形
    glitch_count = 5 if mode != 3 else 15
    for _ in range(glitch_count):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        w = random.randint(40, 200)
        h = random.randint(4, 12)
        color = (0, 255, 255) if mode != 3 else (255, 0, 0)
        pygame.draw.rect(screen, color, (x + shake_x, y + shake_y, w, h))

    # 文字フェード
    alpha = min(255, alpha + 5)
    if mode == 0: text = "WAITING"; color = (120, 120, 120)
    elif mode == 1: text = "EASY"; color = (0, 255, 255)
    elif mode == 2: text = "HARD"; color = (255, 160, 0)
    elif mode == 3: text = "EXTRA"; color = (255, 0, 0)

    text_surf = draw_dot_text(text, color)
    text_surf.set_alpha(alpha)
    screen.blit(text_surf,
                (screen_width // 2 - text_surf.get_width() // 2 + shake_x,
                 screen_height // 2 - text_surf.get_height() // 2 + shake_y))

    pygame.display.update()
    clock.tick(60)
