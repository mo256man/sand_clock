import time
import random
import copy

# 砂時計のサイズ
WIDTH = 12   # 横幅
HEIGHT = 16  # 高さ

# 砂の初期配置（上半分に砂を詰める）
def init_field():
    field = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    # 上半分の三角形に砂を敷き詰める
    for y in range(HEIGHT // 2):
        for x in range(WIDTH):
            if triangle_mask(y, x):
                field[y][x] = 1
    return field

# 砂時計形状のマスク: trueなら砂が置ける場所
def triangle_mask(y, x):
    mid = WIDTH // 2
    spread = y * WIDTH // HEIGHT
    return mid - spread <= x <= mid + spread

# 描画
def print_field(field):
    for y in range(HEIGHT):
        line = ""
        for x in range(WIDTH):
            line += "●" if field[y][x] == 1 else " "
        print(line)
    print("-" * WIDTH)

# 1ステップ分の砂の落下
def update_field(field):
    new_field = copy.deepcopy(field)
    # 下から上へチェック（衝突判定のため）
    for y in range(HEIGHT - 2, -1, -1):
        for x in range(WIDTH):
            if field[y][x] == 1:
                # 真下が空いていれば落とす
                if field[y + 1][x] == 0 and triangle_mask(y + 1, x):
                    new_field[y][x] = 0
                    new_field[y + 1][x] = 1
                # 下が壁や砂なら、左右に落ちる（確率でランダム）
                else:
                    dirs = []
                    if x > 0 and field[y + 1][x - 1] == 0 and triangle_mask(y + 1, x - 1):
                        dirs.append(-1)
                    if x < WIDTH - 1 and field[y + 1][x + 1] == 0 and triangle_mask(y + 1, x + 1):
                        dirs.append(1)
                    if dirs:
                        dx = random.choice(dirs)
                        new_field[y][x] = 0
                        new_field[y + 1][x + dx] = 1
    return new_field

# すべて下に落ちたか判定
def is_all_down(field):
    for y in range(HEIGHT // 2):
        for x in range(WIDTH):
            if field[y][x] == 1:
                return False
    return True

# 上下反転
def flip_field(field):
    flipped = [row[:] for row in field[::-1]]
    return flipped

if __name__ == "__main__":
    field = init_field()
    while True:
        print_field(field)
        time.sleep(0.1)
        new_field = update_field(field)
        # 変化がなければ、全て落ちた扱い
        if new_field == field and is_all_down(field):
            time.sleep(1)
            field = flip_field(field)
        else:
            field = new_field