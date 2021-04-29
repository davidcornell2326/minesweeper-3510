import json
from Board import Board

########################################################################################################################
#                                                                                                                      #
#                                          CS3510 Minesweeper Algorithms                                               #
#                                   David Cornell, Josh Rosenthal, Michael Ryan                                        #
#                                                                                                                      #
########################################################################################################################


testcase = "./testcases/standard_boards/varied_size/10x_10y_10d_0.json"


def load_board(testcase_path):
    with open(testcase_path) as f:
        data = json.load(f)

        dims = data['dim'].split(',')
        height = int(dims[0])
        width = int(dims[1])

        startPos = data['safe'].split(',')
        startX = int(startPos[0])
        startY = int(startPos[1])

        bombCount = int(data['bombs'])

        grid = data['board']

        return Board(width, height, startX, startY, bombCount, grid)


# Main method
if __name__ == "__main__":
    board = load_board(testcase)
    print(board.AI1())
