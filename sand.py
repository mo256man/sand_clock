import numpy as np
import cv2
import math
import random

BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
YELLOW = (0, 255, 255)
BROWN = (42, 42, 165)
ORANGE = (0, 165, 255)
PINK = (203, 192, 255)
WHITE = (255, 255, 255)

COLORS = [BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, ORANGE, PINK, GRAY, WHITE]


# 重力方向を360度の角度で指定（真下が0度）
def gravity_vector(angle):
    rad = math.radians(angle)
    return (math.sin(rad), math.cos(rad))

class App():
    def __init__(self):
        self.width = 800
        self.height = 640
        self.image = np.full((self.height, self.width, 3), WHITE, np.uint8)

        # グリッド
        self.division = 32
        self.grid = np.zeros((self.division, self.division), dtype=int)
        self.errors =  np.zeros((self.division, self.division, 2), dtype=float)     # 累積誤差を管理する変数

        # 円の外を壁にする
        columns = [range(5), range(3), range(2), [0], [0]]
        for r, cols in enumerate(columns):
            for c in cols:
                self.set_symmetric(r, c, 9)

        # ランダムに砂を発生させる
        color_id = 2
        for _ in range(10):
            c = random.randint(0, self.division-1)
            r = random.randint(0, self.division-1)
            if self.grid[r, c] == 0:
                self.grid[r, c] = color_id
                color_id = (color_id % 8) + 1   # 2~8でループ


        # ディスク
        self.disc_size = min(self.height, self.width)
        self.tile_size = self.disc_size // self.division
        disc = np.full((self.disc_size, self.disc_size, 3), BLACK, np.uint8)
        cv2.circle(disc, (self.disc_size//2, self.disc_size//2), self.disc_size//2, WHITE, 1)
        for x in range(0, self.disc_size, self.tile_size):
            cv2.line(disc, (x,0), (x,self.disc_size), GREEN, 1)
        for y in range(0, self.disc_size, self.tile_size):
            cv2.line(disc, (0,y), (self.disc_size,y), GREEN, 1)
        self.disc_origin = disc
        self.angle = 0

    def set_symmetric(self, r, c, value):
        symmetric_positions = [
            (r, c),
            (r, self.division - c - 1),
            (self.division - r - 1, c),
            (self.division - r - 1, self.division - c - 1)
        ]
        for rr, cc in symmetric_positions:
            self.grid[rr, cc] = value


    # 累積誤差補正法を使用した最も重力方向に近い隣接セルを計算
    def find_closest_cell_with_error(self, r, c):
        # dx, dy = self.gravity  # 重力ベクトルの成分
        self.errors[r, c, :2] += self.gravity
        error_x, error_y = self.errors[r, c]

        move_x, move_y = 0, 0

        if abs(error_y) >= 1:
            move_y = 1 if error_y > 0 else -1
            error_y -= math.copysign(1, error_y)  # 誤差補正

        if abs(error_x) >= 1:
            move_x = 1 if error_x > 0 else -1
            error_x -= math.copysign(1, error_x)  # 誤差補正

        # 移動先セルの決定
        nr, nc = r + move_y, c + move_x
        if 0 <= nr < self.division and 0 <= nc < self.division and self.grid[nr, nc] == 0:
            self.errors[nr, nc] = (error_x, error_y)
            self.errors[r, c] = (0, 0)
            return nr, nc

        # 移動が無効な場合はその場にとどまる
        return r, c

    def reset_errors(self):
        self.errors =  np.zeros((self.division, self.division, 2), dtype=float)

    def simulate_sand(self):
        self.gravity = gravity_vector(self.angle)

        updated = False
        new_grid = self.grid.copy()

        for r in range(self.division):
            for c in range(self.division):
                if 0 < self.grid[r, c] < 9:  # IDを持つ砂粒のみ移動
                    sand_id = self.grid[r, c]  # 現在の砂粒のID
                    next_cell = self.find_closest_cell_with_error(r, c)
                    if next_cell:
                        nr, nc = next_cell
                        if (nr, nc) != (r, c):  # 移動先が現在の位置でない場合
                            new_grid[nr, nc] = sand_id
                            new_grid[r, c] = 0
                            updated = True

        self.grid = new_grid

    def show(self):
        disc = self.disc_origin.copy()
        for r in range(self.division):
            for c in range(self.division):
                x0 = c * self.tile_size
                y0 = r * self.tile_size
                x1 = (c+1) * self.tile_size
                y1 = (r+1) * self.tile_size
                cell = self.grid[r,c]
                color = COLORS[cell]
                if color:
                    cv2.rectangle(disc, (x0,y0), (x1,y1), color, -1)

        # 基準の真下
        x0, y0 = self.disc_size//2, self.disc_size//2
        x1, y1 = x0, self.disc_size
        cv2.line(disc, (x0, y0), (x1, y1), RED, 1)

        # 重力の方向
        gx, gy = gravity_vector(self.angle)
        x1 = int(x0 + self.disc_size * gx)
        y1 = int(y0 + self.disc_size * gy)
        cv2.line(disc, (x0, y0), (x1, y1), BLUE, 1)

        M = cv2.getRotationMatrix2D((self.disc_size//2, self.disc_size//2), -self.angle, 1)
        disc_rot = cv2.warpAffine(disc, M, (self.disc_size, self.disc_size))
        x0 = (self.width - self.disc_size)//2
        x1 = (self.width + self.disc_size)//2
        self.image[:, x0:x1] = disc
        cv2.imshow("origin", self.image)
        self.image[:, x0:x1] = disc_rot
        cv2.imshow("rot", self.image)

def main():
    app = App()
    while True:
        app.simulate_sand()
        app.show()
        key = cv2.waitKey(100) & 0xFF
        if key == 27:
            break
        elif key == ord("a"):
            app.angle += 10
            app.reset_errors()
        elif key == ord("d"):
            app.angle -= 10
            app.reset_errors()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
