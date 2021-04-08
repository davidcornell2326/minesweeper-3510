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
        return "\n".join([self.gridString[i:i+self.width] for i in range(0, len(self.gridString), self.width)])