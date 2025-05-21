import numpy as np
import cv2
import random
from time import sleep
from collections import deque

W = 16
H = 16
OWANIMO = 4
COLORS = 4

is_generate = True

class Field():
    def __init__(self):
        self.clear()
        self.is_generate = True
        self.rensa = 0

    def clear(self):
        self.matrix = [[0] *W for h in range(H)]

    def print(self):
        texts = " "*20+"\n" if self.rensa==0 else f"   {self.rensa}連鎖{'!'*(self.rensa)}\n"
        for r, row in enumerate(self.matrix):
            texts += f"{r:02} "
            for cell in row:
                if cell == 0:
                    texts += " "
                else:
                    texts += f"\033[3{cell}m{cell}\033[0m"
            texts += "\n"
        texts += "   " + "=" * W
        texts += "\033[F" * (H+2)   # 行の数だけカーソル上移動を繰り返す
        print(texts)

        is_owanimo = any("*" in row for row in self.matrix)     # * があるかどうか
        wait_time = 0.8 if is_owanimo else 0.001
        sleep(wait_time)

    def generate_drop(self):
        # 全部埋まったとき＝最上段に0が一つもないときは一色が消える
        if not 0 in self.matrix[0]:
            self.erase_one_color()
        else:
            color = random.randint(1, COLORS)
            while True:
                c = random.randint(0, W-1)
                if self.matrix[0][c] == 0:
                    self.matrix[0][c] = color
                    break
        self.is_generate = False
        self.rensa = 0

    def drop(self):
        copy = [row[:] for row in self.matrix]
        for r in reversed(range(H)):    # 下からチェック
            for c in range(W):
                # ぷよが消える演出の * を空白に戻す
                if self.matrix[r][c] == "*":
                    self.matrix[r][c] = 0

                # 落下 最下行はこれより下に落ちないので評価しない
                if r < H-1:
                    if self.matrix[r+1][c] == 0:
                        self.matrix[r+1][c] = self.matrix[r][c]
                        self.matrix[r][c] = 0
                else:
                    pass

        if copy == self.matrix:             # マトリックスが変わっていない　つまりこれ以上動かないならば
            is_erase = self.erase()         # ぷよ消しチェック　戻り値は消えたかどうか
            if is_erase:                    # 消えたら
                self.rensa += 1             # 連鎖を+1する
            else:                           # 消えなかったら
                self.is_generate = True     # 次のぷよを発生させる


    def erase(self):
        checked = [[False] * W for _ in range(H)]
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        found_groups = []

        def bfs(r, c, value):
            queue = deque()
            group = []
            queue.append((r, c))
            checked[r][c] = True
            group.append((r, c))

            while queue:
                x, y = queue.popleft()
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < H and 0 <= ny < W and
                        not checked[nx][ny] and self.matrix[nx][ny] == value
                    ):
                        checked[nx][ny] = True
                        queue.append((nx, ny))
                        group.append((nx, ny))

            return group

        is_erase = False
        for r in range(H):
            for c in range(W):
                if self.matrix[r][c] != 0 and not checked[r][c]:
                    group = bfs(r, c, self.matrix[r][c])
                    if len(group) >= OWANIMO:
                        found_groups.append(group)
                        is_erase = True

        for group in found_groups:
            for r,c in group:
                self.matrix[r][c] = "*"   # ぷよが消える演出

        return is_erase

    def erase_one_color(self):
        color = random.randint(1, COLORS)
        self.matrix = [[0 if x == color else x for x in row] for row in self.matrix]

    def gameover(self):
        self.clear()

field = Field()

while True:
    if field.is_generate:
        field.is_generate = False
        field.generate_drop()
    else:
        field.drop()
    field.print()
