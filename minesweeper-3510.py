import json
from Board import Board
import time
import os
import pprint

########################################################################################################################
#                                                                                                                      #
#                                          CS3510 Minesweeper Algorithms                                               #
#                                   David Cornell, Josh Rosenthal, Michael Ryan                                        #
#                                                                                                                      #
########################################################################################################################




def load_board(testcase_path):
    with open(testcase_path) as f:
        data = json.load(f)

        dims = data['dim'].split(',')
        height = int(dims[0])
        width = int(dims[1])

        startPos = data['safe'].split(',')
        startY = int(startPos[0])
        startX = int(startPos[1])

        bombCount = int(data['bombs'])

        grid = data['board']

        return Board(width, height, startX, startY, bombCount, grid)


# Main method
if __name__ == "__main__":

    directory = "./testcases/standard_boards/varied_size_boards"
    # directory = "./testcases/standard_boards/varied_density_boards"

    testcase = "./testcases/standard_boards/varied_size_boards/10rows_10cols_10d_0.json"

    print("Minesweeper Project by Michael Ryan, David Cornell, and Josh Rosenthal")
    print("\nPLEASE READ README.MD BEFORE RUNNING ANY FILES")
    input("Press enter to continue (make sure the terminal is selected and the cursor is at the end of this line)")
    print("\nChoose one of the following run options:")
    print("\n1: Do a full run of a single test case with AI1, with details shown (change the testcase by modifying the testcase variable in minesweeper-3510.py)")
    print("\n2: Do a full run of a single test case with AI2, with details shown (change the testcase by modifying the testcase variable in minesweeper-3510.py)")
    print("\n3: Run ALL varied size testcases for AI1, with only results shown")
    print("\n4: Run ALL varied mine density testcases for AI1, with only results shown")
    print("\n5: Run ALL varied size testcases for AI2, with only results shown")
    print("\n6: Run ALL varied mine density testcases for AI2, with only results shown")
    # note: option 7 is the mode that will write the results to a file for our analysis purposes (should not be an option for the grading TA)
    choice = int(input("\nEnter a number and then press enter to continue: "))

    if choice == 1:
        board = load_board(testcase)
        start_time = time.time()
        print(board.AI1(True))
        end_time = time.time()
        print("\n")
        print("Milliseconds of execution:", 1000 * (end_time - start_time))

    if choice == 2:
        board = load_board(testcase)
        start_time = time.time()
        print(board.AI2(True))
        end_time = time.time()
        print("\n")
        print("Milliseconds of execution:", 1000 * (end_time - start_time))

    if choice == 3:
        directory = "./testcases/standard_boards/varied_size_boards"
        for filename in os.listdir(directory):
            print(filename)
            board = load_board(directory + "/" + filename)
            start_time = time.time()
            print(board.AI1(False))
            end_time = time.time()
            print("")
            print("Milliseconds of execution:", 1000 * (end_time - start_time))
            print("\n\n")

    if choice == 4:
        directory = "./testcases/standard_boards/varied_density_boards"
        for filename in os.listdir(directory):
            print(filename)
            board = load_board(directory + "/" + filename)
            start_time = time.time()
            print(board.AI1(False))
            end_time = time.time()
            print("")
            print("Milliseconds of execution:", 1000 * (end_time - start_time))
            print("\n\n")

    if choice == 5:
        directory = "./testcases/standard_boards/varied_size_boards"
        for filename in os.listdir(directory):
            print(filename)
            board = load_board(directory + "/" + filename)
            start_time = time.time()
            print(board.AI2(False))
            end_time = time.time()
            print("")
            print("Milliseconds of execution:", 1000 * (end_time - start_time))
            print("\n\n")

    if choice == 6:
        directory = "./testcases/standard_boards/varied_density_boards"
        for filename in os.listdir(directory):
            print(filename)
            board = load_board(directory + "/" + filename)
            start_time = time.time()
            print(board.AI2(False))
            end_time = time.time()
            print("")
            print("Milliseconds of execution:", 1000 * (end_time - start_time))
            print("\n\n")

    if choice == 7:
        r = open("outputRuntimes.txt", "a")
        for filename in os.listdir(directory):
            board = load_board(directory + "/" + filename)
            # print(filename)
            start_time = time.time()

            board.AI1(False)
            # board.AI2(False)

            # print(board.AI1())
            # print(board.AI2())
            end_time = time.time()
            # print("\n")
            # print("Milliseconds of execution:", 1000 * (end_time - start_time))

            r.write(str(1000 * (end_time - start_time)) + "\t")

        r.close()
