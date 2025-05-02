def find_connected_puyos(grid):
    from collections import deque

    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    found_groups = []

    def bfs(r, c, value):
        queue = deque()
        group = []
        queue.append((r, c))
        visited[r][c] = True
        group.append((r, c))

        while queue:
            x, y = queue.popleft()
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < rows and 0 <= ny < cols and
                    not visited[nx][ny] and grid[nx][ny] == value
                ):
                    visited[nx][ny] = True
                    queue.append((nx, ny))
                    group.append((nx, ny))

        return group

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0 and not visited[i][j]:
                group = bfs(i, j, grid[i][j])
                if len(group) >= 4:
                    found_groups.append(group)

    return found_groups

grid = [
    [1, 1, 0, 2, 2],
    [1, 0, 2, 2, 0],
    [0, 0, 0, 2, 0],
    [3, 3, 3, 1, 1],
    [3, 0, 0, 0, 0],
]

connected_groups = find_connected_puyos(grid)
for group in connected_groups:
    print("Connected group (size {}):".format(len(group)))
    print(group)