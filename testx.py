import os
import sys
import random
import math
import pygame

# =============================
#  環境変数・初期設定
# =============================
# Windows用のオーディオドライバを強制
os.environ['SDL_AUDIODRIVER'] = 'directsound'
# 他候補:
# os.environ['SDL_AUDIODRIVER'] = 'winmm'
# os.environ['SDL_AUDIODRIVER'] = 'wasapi'

# 一度クリーンにしてから初期化
pygame.quit()
pygame.mixer.quit()

pygame.init()
pygame.mixer.init()

# =============================
#  画面・基本設定
# =============================
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN.get_size()
pygame.display.set_caption("Cyber Mode Fullscreen Dot Text")

CLOCK = pygame.time.Clock()
FPS = 60

# フォント設定
DOT_FONT_SIZE = SCREEN_HEIGHT // 4  # 画面高さの 1/4
DOT_FONT = pygame.font.Font("PixelOperatorHB8.ttf", DOT_FONT_SIZE)

# =============================
#  カラー定義
# =============================
COLOR_WAITING = (120, 120, 120)
COLOR_EASY    = (0, 255, 255)
COLOR_HARD    = (255, 160, 0)
COLOR_EXTRA   = (255, 0, 0)
COLOR_PARTICLE_NORMAL = (0, 200, 255)

# =============================
#  モード定義
# =============================
MODE_WAITING = 0
MODE_EASY    = 1
MODE_HARD    = 2
MODE_EXTRA   = 3

# =============================
#  音楽ロード
# =============================
pygame.mixer.music.load("8bit_Battle-With-Leaders.mp3")

# =============================
#  粒子クラス
# =============================
class Particle:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset(randomize_y=True)

    def reset(self, randomize_y=False):
        self.x = random.randint(0, self.screen_width)
        self.y = random.randint(0, self.screen_height) if randomize_y else 0
        self.speed = random.uniform(2, 4)
        self.w = random.randint(2, 4)
        self.h = random.randint(6, 12)

    def update(self, mode):
        # EXTRAモードはスピードアップ
        move_speed = self.speed
        if mode == MODE_EXTRA:
            move_speed += random.uniform(2, 4)

        self.y += move_speed

        # 画面下に出たら上に戻す
        if self.y > self.screen_height:
            self.reset(randomize_y=False)

    def draw(self, surface, mode, shake_x=0, shake_y=0):
        if mode == MODE_EXTRA:
            color = COLOR_EXTRA
        else:
            color = COLOR_PARTICLE_NORMAL

        pygame.draw.rect(
            surface,
            color,
            (int(self.x) + shake_x, int(self.y) + shake_y, self.w, self.h)
        )

# 粒子生成
particles = [Particle(SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(80)]

# =============================
#  背景グラデーション
# =============================
def fill_gradient(surface, top_color, bottom_color):
    """縦方向の簡易グラデーションを塗る"""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

# =============================
#  スキャンライン演出
# =============================
def draw_scanlines(surface, spacing=4, alpha=40):
    """古いモニタ風スキャンライン"""
    scanline = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
    # シアン寄りのライン（アルファ付き）
    line_color = (0, 255, 255, alpha)
    scanline.fill(line_color)

    for y in range(0, SCREEN_HEIGHT, spacing):
        surface.blit(scanline, (0, y))

# =============================
#  グリッチ矩形
# =============================
def draw_glitch_rects(surface, mode, shake_x=0, shake_y=0):
    """グリッチ風の短冊矩形を描く"""
    glitch_count = 5 if mode != MODE_EXTRA else 15
    color = (0, 255, 255) if mode != MODE_EXTRA else COLOR_EXTRA

    for _ in range(glitch_count):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        w = random.randint(40, 200)
        h = random.randint(4, 12)
        pygame.draw.rect(surface, color, (x + shake_x, y + shake_y, w, h))

# =============================
#  モード→文字＆色
# =============================
def get_mode_text_and_color(mode):
    if mode == MODE_WAITING:
        return "WAITING", COLOR_WAITING
    elif mode == MODE_EASY:
        return "EASY", COLOR_EASY
    elif mode == MODE_HARD:
        return "HARD", COLOR_HARD
    elif mode == MODE_EXTRA:
        return "EXTRA", COLOR_EXTRA
    else:
        return "UNKNOWN", (255, 255, 255)

# =============================
#  中央テキスト（EXTRAで脈動）
# =============================
def draw_center_text_pulsed(surface, text, color, alpha, mode, t, shake_x=0, shake_y=0):
    """EXTRAモード時に文字が拡大縮小する演出付き"""
    text_surf = DOT_FONT.render(text, True, color)
    text_surf.set_alpha(alpha)

    scale = 1.0
    if mode == MODE_EXTRA:
        # 1.0 ± 0.1 くらいで拡大縮小
        scale = 1.0 + 0.1 * math.sin(t)

    w = int(text_surf.get_width() * scale)
    h = int(text_surf.get_height() * scale)
    scaled = pygame.transform.smoothscale(text_surf, (w, h))

    x = SCREEN_WIDTH // 2 - scaled.get_width() // 2 + shake_x
    y = SCREEN_HEIGHT // 2 - scaled.get_height() // 2 + shake_y

    surface.blit(scaled, (x, y))

# =============================
#  メインループ
# =============================
def main():
    mode = MODE_WAITING
    prev_mode = mode
    alpha = 0
    t = 0.0  # パルス用タイマー

    while True:
        # -------------------------
        # イベント処理
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_0:
                    mode = MODE_WAITING
                    alpha = 0
                elif event.key == pygame.K_1:
                    mode = MODE_EASY
                    alpha = 0
                elif event.key == pygame.K_2:
                    mode = MODE_HARD
                    alpha = 0
                elif event.key == pygame.K_3:
                    mode = MODE_EXTRA
                    alpha = 0

        # -------------------------
        # モード切り替え時の音再生
        # -------------------------
        if mode != prev_mode:
            pygame.mixer.music.stop()

            if mode == MODE_WAITING:
                # 無音（タイトル待機っぽい）
                pass
            elif mode in (MODE_EASY, MODE_HARD):
                # EASY / HARD は1回だけ再生
                pygame.mixer.music.stop()
            elif mode == MODE_EXTRA:
                # EXTRAはループ再生
                pygame.mixer.music.play(-1)

            prev_mode = mode

        # -------------------------
        # 背景グラデーション
        # -------------------------
        if mode == MODE_WAITING:
            fill_gradient(SCREEN, (0, 0, 0), (20, 20, 20))
        elif mode == MODE_EASY:
            fill_gradient(SCREEN, (0, 30, 60), (0, 150, 180))
        elif mode == MODE_HARD:
            fill_gradient(SCREEN, (40, 10, 0), (160, 60, 0))
        elif mode == MODE_EXTRA:
            fill_gradient(SCREEN, (0, 0, 0), (80, 0, 0))

        # -------------------------
        # 画面揺れ（EXTRAのみ）
        # -------------------------
        shake_x, shake_y = 0, 0
        if mode == MODE_EXTRA:
            shake_x = random.randint(-10, 10)
            shake_y = random.randint(-10, 10)

        # -------------------------
        # 粒子の更新・描画
        # -------------------------
        for p in particles:
            p.update(mode)
            p.draw(SCREEN, mode, shake_x, shake_y)

        # -------------------------
        # グリッチ矩形
        # -------------------------
        draw_glitch_rects(SCREEN, mode, shake_x, shake_y)

        # -------------------------
        # 文字フェード & 脈動
        # -------------------------
        alpha = min(255, alpha + 5)
        text, color = get_mode_text_and_color(mode)
        draw_center_text_pulsed(SCREEN, text, color, alpha, mode, t, shake_x, shake_y)

        # -------------------------
        # スキャンライン
        # -------------------------
        draw_scanlines(SCREEN)

        # -------------------------
        # 画面更新
        # -------------------------
        pygame.display.update()
        CLOCK.tick(FPS)

        # パルス用タイマー進行
        t += 0.05


if __name__ == "__main__":
    main()
