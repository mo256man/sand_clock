import cv2
import numpy as np
import math
import random
import time

class Sand():
    def __init__(self, i, x, y):
        self.char = chr(i+65)       # Aから始まる
        self.x = x
        self.y = y
        self.cnt = i
        self.on_ground = False
        self.color = (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255))

class Field():
    def __init__(self, angle):
        self.angle = angle
        self.gx = -math.sin(math.radians(self.angle))
        self.gy = math.cos(math.radians(self.angle))
        self.width = 32
        self.height = 32
        self.unit = 20

    def __str__(self):
        return  "\n".join([f"{r}: " + " ".join(map(str, row)) for r, row in enumerate(self.matrix)]) + "\n   " + "="*2*self.width

    def apply(self, sands:list[Sand]):
        self.matrix = [["_" for _ in range(self.width)] for _ in range(self.height)]
        for sand in sands:
            x, y, char, color = sand.x, sand.y, sand.char, sand.color
            self.matrix[y][x] = color

    def drop_sands(self, sands:list[Sand]):
        for i, sand in enumerate(sands):
            x, y, char = sand.x, sand.y, sand.char
            # 真下と右下と左下
            xu, yu = round(x + self.gx), round(y + self.gy)                         # 真下
            xl, yl = round(x + self.gx - self.gy), round(y + self.gy - self.gx)     # 左下
            xr, yr = round(x + self.gx + self.gy), round(y + self.gy + self.gx)     # 右下

            if self.is_movable(xu, yu):                             # 真下に動けるならば
                sand.x, sand.y = xu, yu                             # 真下に移動
            elif not self.is_movable(xr, yr) and not self.is_movable(xl, yl):   # 真下・右下・左下のすべてに動けなければ
                sand.on_ground = True                                                            # 何もしない（動かない）
            elif self.is_movable(xr, yr) and not self.is_movable(xl, yl):       # 右下のみ動けるならば
                sand.x, sand.y = xr, yr
            elif not self.is_movable(xr, yr) and self.is_movable(xl, yl):       # 左下のみ動けるならば
                    sand.x, sand.y = xl, yl
            elif self.is_movable(xr, yr) and self.is_movable(xl, yl):           # 右下左下両方に動けるならば
                """
                if sand.cnt == len(sands)-1:    # 最後の砂のとき注目
                    pass
                if self.matrix[yr][xr] == "_" and self.matrix[yl][xl] != "_":       # 右下だけが空白ならば
                    sand.x, sand.y = xr, yr
                elif self.matrix[yr][xr] != "_" and self.matrix[yl][xl] == "_":     # 左下だけが空白ならば
                    sand.x, sand.y = xl, yl
                elif self.matrix[yr][xr] != "_" and self.matrix[yl][xl] != "_":     # どちらも空白でなかったら
                    sand.on_ground = True
                else:                                                               # どちらも空白ならば
                    k = random.choice([0, 1])
                    sand.x, sand.y = [xr, xl][k], [yr, yl][k]
                """
                k = random.choice([0, 1])
                sand.x, sand.y = [xr, xl][k], [yr, yl][k]
            else:
                sand.on_ground = True
            
            # 接地フラグ（次の砂が出てくる）は、最後の一粒にのみ作用する　つまりそれ以外は動けなくてもFalseにする
            if sand.cnt < max(sands, key=lambda x: x.cnt).cnt:
                sand.on_ground = False

        self.apply(sands)

    def isin(self, x, y):
        # x,yがマトリックス内にあるかどうか
        """
        ここ修正する マトリックス内にあって空白かどうか
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def is_movable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.matrix[y][x] == "_":
                ret = True
            else:
                ret = False
        else:
            ret = False
        return ret

    def draw(self):
        image = np.full((self.unit * self.height, self.unit * self.width, 3), (0,0,0), np.uint8)
        for r, row in enumerate(self.matrix):
            y = int((r+0.5) * self.unit)
            for c, cell in enumerate(row):
                x = int((c + 0.5) * self.unit)
                if cell != "_":
                    cv2.circle(image, (x,y), self.unit//2, cell, -1)
        cv2.imshow("", image)

def get_start_pos(gravity_angle, field:Field):
    if gravity_angle == 0:              # 重力が下方向
        x0 = random.randint(0, field.width-1)
        y0 = 0
    elif gravity_angle == 90:           # 重力が左方向
        x0 = field.width - 1
        y0 = random.randint(0, field.height-1)
    elif gravity_angle == 180:          # 重力が上方向
        x0 = random.randint(0, field.width-1)
        y0 = field.height - 1
    elif gravity_angle == 270:          # 重力が右方向
        x0 = 0
        y0 = random.randint(0, field.height-1)
#    return x0, y0
    return random.randint(0, field.width-1), 0

def main():
    gravity_angle = 45
    field = Field(gravity_angle)
    x0, y0 = get_start_pos(gravity_angle, field)

    i = 0
    sands = []
    sands.append(Sand(i, x0, y0))
    field.apply(sands)

    while True:
        # print(field)
        if sands[-1].on_ground:
            i += 1
            x0, y0 = get_start_pos(gravity_angle, field)
            sands.append(Sand(i, x0, y0))
            # print(field)
        field.drop_sands(sands)
        field.draw()
        key = cv2.waitKey(1)
        if key == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
