import random
import sys
import time

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5


def check_bound(area: pg.Rect, obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：オブジェクト（爆弾，こうかとん）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < area.left or area.right < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < area.top or area.bottom < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    _delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self._img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"ex03/fig/{num}.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        self._img_rev = pg.transform.flip(self._img, True, False)
        self._imgs = {
            (+1, 0): self._img,
            (+1, -1): pg.transform.rotozoom(self._img, 45, 1.0),
            (0, -1): pg.transform.rotozoom(self._img, 90, 1.0),
            (-1, -1): pg.transform.rotozoom(self._img_rev, -45, 1.0),
            (-1, 0): self._img_rev,
            (-1, +1): pg.transform.rotozoom(self._img_rev, 45, 1.0),
            (0, +1): pg.transform.rotozoom(self._img, -90, 1.0),
            (+1, +1): pg.transform.rotozoom(self._img, -45, 1.0)
        }
        self._rct = self._img.get_rect()
        self._rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__._delta.items():
            if key_lst[k]:
                self._rct.move_ip(mv)
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(screen.get_rect(), self._rct) != (True, True):
            for k, mv in __class__._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
        if sum_mv != [0, 0]:
            self._img = self._imgs[tuple(sum_mv)]
        screen.blit(self._img, self._rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    _colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255))
    _dires = (-1, 0, 1)
    def __init__(self):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        rad = random.randint(10, 50)
        color = random.choice(Bomb._colors)
        self._img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = random.choice(Bomb._dires), random.choice(Bomb._dires)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(screen.get_rect(), self._rct)
        if not yoko:
            self._vx *= -1
        if not tate:
            self._vy *= -1
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)


class Beam:
    """
    ビームに関するクラス
    """
    def __init__(self, bird, screen: pg.Surface):
        self._img = pg.image.load("ex03/fig/beam.png")
        self._rct = self._img.get_rect()
        self._rct.centerx = bird._rct.centerx + 10
        self._rct.centery = bird._rct.centery
        screen.blit(self._img, (self._rct.centerx, self._rct.centery))
        
    def update(self, screen: pg.Surface):
        self._vx = +1
        self._rct.move_ip(self._vx, 0)
        screen.blit(self._img, self._rct)

            

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    score = 0                                               # 撃ち落とした爆弾の数を格納する変数
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    fonto = pg.font.Font(None, 80)                          # フォントの作成

    bird = Bird(3, (900, 400))
    bombs = [Bomb() for _ in range(NUM_OF_BOMBS)]
    beam = None

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beam = Beam(bird, screen)
                
        tmr += 1
        screen.blit(bg_img, [0, 0])
        txt = fonto.render("Score : " + str(score), True, (0, 0, 0))
        screen.blit(txt, [100, 100])                        # テキストの描画
        
        for bomb in bombs:
            if bird._rct.colliderect(bomb._rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for i, bomb in enumerate(bombs):
            bomb.update(screen)
        if beam is not None:
            beam.update(screen)
            for i, bomb in enumerate(bombs):
                if beam._rct.colliderect(bomb._rct):
                    beam = None
                    del bombs[i]
                    score += 1                              # 爆弾を撃ち落とす度にスコアを加算
                    bird.change_img(6, screen)
                    break
        pg.display.update()
        clock.tick(500)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
