class Board:
    def __init__(self, width, height, startX, startY, bombCount, grid):
        self.width = width
        self.height = height
        self.startX = startX
        self.startY = startY
        self.bombCount = bombCount
        self.gridString = grid
        self.grid = [[] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                self.grid[y].append(int(grid[(y * width) + x]))

    def __repr__(self):
        lines = []
        for line in self.grid:
            line_arr = []
            for num in line:
                line_arr.append(str(num))
            lines.append("".join(line_arr))
        return "\n".join(lines)