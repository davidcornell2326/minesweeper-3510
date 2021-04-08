class Board:
    def __init__(self, width, height, startX, startY, bombCount, grid):
        self.width = width
        self.height = height
        self.startX = startX
        self.startY = startY
        self.bombCount = bombCount
        self.gridString = grid
        # todo process grid

    def __repr__(self):
        return "a " + str(self.width) + " x " + str(self.height) + \
               " board starting at (" + str(self.startX) + "," + str(self.startY) + \
               ") with " + str(self.bombCount) + " bombs. \n" + self.gridString