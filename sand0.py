import numpy as np
import math
import cv2

# 定数定義
EMPTY = 0  # 空
SAND_BASE = 1  # 砂粒の識別用ベース値

# グリッドの初期化（砂粒10個を配置する）
def initialize_grid(rows, cols):
    grid = np.zeros((rows, cols), dtype=int)
    sand_id = 1  # 砂粒のID (1～9)
    for i in range(cols // 2 - 5, cols // 2 + 5):  # 中央付近に10個配置
        grid[0, i] = sand_id
        sand_id = (sand_id % 9) + 1  # 1～9 の範囲でループ
    return grid

# 重力方向を360度の角度で指定（真下が0度）
def gravity_vector(angle):
    rad = math.radians(angle)
    return (math.sin(rad), math.cos(rad))  # 真下が0度に対応

# 累積誤差補正法を使用した最も重力方向に近い隣接セルを計算
def find_closest_cell_with_error(r, c, gravity, rows, cols, grid, error):
    dx, dy = gravity  # 重力ベクトルの成分
    error[0] += dx  # x方向の累積誤差を更新
    error[1] += dy  # y方向の累積誤差を更新

    move_x, move_y = 0, 0

    # 縦方向の移動を優先
    if abs(error[1]) >= 1:
        move_y = 1 if error[1] > 0 else -1
        error[1] -= math.copysign(1, error[1])  # 誤差補正

    # 横方向の移動を次に考慮
    if abs(error[0]) >= 1:
        move_x = 1 if error[0] > 0 else -1
        error[0] -= math.copysign(1, error[0])  # 誤差補正

    # 移動先セルの決定
    nr, nc = r + move_y, c + move_x
    if 0 <= nr < rows and 0 <= nc < cols and grid[nr, nc] == EMPTY:
        return nr, nc

    # 移動が無効な場合はその場にとどまる
    return r, c

# 重力角度をキー入力に基づいて変更
def update_gravity(gravity_angle, key):
    # 真下を0度とする角度マッピング
    key_to_angle = {
        'x': 0,    # 下
        'z': 45,   # 左下
        'a': 90,   # 左
        'q': 135,  # 左上
        'w': 180,  # 上
        'e': 225,  # 右上
        'd': 270,  # 右
        'c': 315   # 右下
    }
    if key in key_to_angle:
        return key_to_angle[key]
    return gravity_angle  # 変更なしの場合はそのまま返す

# グリッドを画像として描画
def draw_grid(grid, cell_size=20):
    rows, cols = grid.shape
    img = np.zeros((rows * cell_size, cols * cell_size, 3), dtype=np.uint8)
    for r in range(rows):
        for c in range(cols):
            if grid[r, c] > EMPTY:
                cv2.rectangle(img, (c * cell_size, r * cell_size),
                              ((c + 1) * cell_size, (r + 1) * cell_size),
                              (0, 255, 255), -1)  # 黄色で塗りつぶし
            else:
                cv2.rectangle(img, (c * cell_size, r * cell_size),
                              ((c + 1) * cell_size, (r + 1) * cell_size),
                              (50, 50, 50), -1)  # グレーで塗りつぶし
    return img

# 砂粒のシミュレーション
def simulate_sand(grid, gravity_angle):
    rows, cols = grid.shape
    gravity = gravity_vector(gravity_angle)  # 重力ベクトルを計算
    error = [0, 0]  # 累積誤差を管理する変数

    while True:
        updated = False
        new_grid = grid.copy()

        for r in range(rows):
            for c in range(cols):
                if grid[r, c] > EMPTY:  # IDを持つ砂粒のみ移動
                    sand_id = grid[r, c]  # 現在の砂粒のID
                    next_cell = find_closest_cell_with_error(r, c, gravity, rows, cols, new_grid, error)
                    if next_cell:
                        nr, nc = next_cell
                        if (nr, nc) != (r, c):  # 移動先が現在の位置でない場合
                            new_grid[nr, nc] = sand_id
                            new_grid[r, c] = EMPTY
                            updated = True

        grid = new_grid

        # グリッドを描画して表示
        img = draw_grid(grid)
        cv2.imshow("Sand Simulation", img)

        # キー入力の取得（終了キー: 'sec'）
        key = cv2.waitKey(1) & 0xFF
        if key != 255:  # キーが押された場合
            key_char = chr(key).lower()
            if key_char == 's':  # 'sec' の入力を開始
                if cv2.waitKey(0) & 0xFF == ord('e'):
                    if cv2.waitKey(0) & 0xFF == ord('c'):
                        print("シミュレーションを終了します。")
                        break
            gravity_angle = update_gravity(gravity_angle, key_char)
            gravity = gravity_vector(gravity_angle)  # 重力ベクトルを更新
            error = [0, 0]  # 累積誤差をリセット

#        if not updated:
#            break

    cv2.destroyAllWindows()

# 実行例
if __name__ == "__main__":
    rows, cols = 10, 20  # グリッドサイズ
    grid = initialize_grid(rows, cols)

    gravity_angle = 0  # 初期状態で重力の方向を「真下」に設定
    print("シミュレーション開始:")
    print("キー操作:\n x:下, z:左下, a:左, q:左上, w:上, e:右上, d:右, c:右下")
    print("終了するには 'sec' を押してください。")
    simulate_sand(grid, gravity_angle)