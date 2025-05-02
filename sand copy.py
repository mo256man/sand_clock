import numpy as np
import cv2
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
GRAY = (128, 128, 128)

class App():
    def __init__(self):
        self.width = 800
        self.height = 640
        self.image = np.full((self.height, self.width, 3), WHITE, np.uint8)

        # マトリックス
        self.division = 16
        self.matrix = [[0 for _ in range(self.division)] for _ in range(self.division)]

        # 円の外を壁にする
        columns = [range(5), range(3), range(2), [0], [0]]
        for r, cols in enumerate(columns):
            for c in cols:
                self.set_symmetric(r, c, 9)

        # ランダムに砂を発生させる
        for _ in range(50):
            c = random.randint(0, self.division-1)
            r = random.randint(0, self.division-1)
            if self.matrix[r][c] == 0:
                self.matrix[r][c] = 1


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
            self.matrix[rr][cc] = value

    def show(self):
        disc = self.disc_origin.copy()
        for r in range(self.division):
            for c in range(self.division):
                x0 = c * self.tile_size
                y0 = r * self.tile_size
                x1 = (c+1) * self.tile_size
                y1 = (r+1) * self.tile_size
                cell = self.matrix[r][c]
                if cell == 9:
                    color = GRAY
                elif cell == 1:
                    color = RED
                else:
                    color = 0
                if color:
                    cv2.rectangle(disc, (x0,y0), (x1,y1), color, -1)

        M = cv2.getRotationMatrix2D((self.disc_size//2, self.disc_size//2), self.angle, 1)
        disc_rot = cv2.warpAffine(disc, M, (self.disc_size, self.disc_size))
        x0 = (self.width - self.disc_size)//2
        x1 = (self.width + self.disc_size)//2
        self.image[:, x0:x1] = disc_rot
        cv2.imshow("", self.image)

def main():
    app = App()
    while True:
        app.show()
        key = cv2.waitKey(100) & 0xFF
        if key == 27:
            break
        elif key == ord("a"):
            app.angle += 10
        elif key == ord("d"):
            app.angle -= 10
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
