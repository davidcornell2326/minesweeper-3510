import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)
from tkinter import *
import random, argparse
import minesweeperAI1 
import minesweeperAI2


# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class Window(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, numRows, numCols, numBombs, safeSquare, AIType, master=None):
        
        # parameters that you want to send through the Frame class. 
        Frame.__init__(self, master)   

        #reference to the master widget, which is the tk window                 
        self.master = master

        #with that, we want to then run init_window, which doesn't yet exist
        self.outcome = 0

        # game variables that can be accessed in any method in the class. For example, to access the number of rows, use "self.numRows" 
        self.numRows = numRows
        self.numCols = numCols
        self.numBombs = numBombs
        self.safeSquare = safeSquare
        self.AIType = AIType

        self.init_window()

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget      
        self.master.title("Minesweeper")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)
        
        self.button = []
        for row in range(self.numRows):
            curRow = []
            for col in range(self.numCols):
                curRow.append(Button(self, bg="gray", width=2, height=1, command=lambda rw=row, cl=col: self.open_button(rw, cl)))
                curRow[col].grid(row=row, column=col)
            self.button.append(curRow)

        self.generate_board()
        AIAlgo1Button = Button(self, bg="blue", text="AI 1", width=6, height=5, command=self.AIAlgo)
        AIAlgo1Button.place(x=600, y=150)

        AIAlgo2Button = Button(self, bg="blue", text="AI 2", width=6, height=5, command=self.AIAlgo)
        AIAlgo2Button.place(x=600, y=350)

        self.AI = None
        if self.AIType == 1:
            self.AI = minesweeperAI1.AI1(self.numRows, self.numCols, self.numBombs, self.safeSquare)
        else:
            self.AI = minesweeperAI2.AI2(self.numRows, self.numCols, self.numBombs, self.safeSquare)

        self.highlight_button(self.safeSquare)

        self.AIAlgo()

    # (DO NOT MODIFY): uncover a square and perform appriopriate action based on game rule
    def open_button(self, r, c):

        if not self.squareInBounds(r, c):
            return

        self.button[r][c].config(state="disabled")
        if self.ans[r][c] != 9:
            self.button[r][c]["text"] = self.ans[r][c]
            self.button[r][c]["bg"] = "white"
        else:
            self.button[r][c]["bg"] = "red"
            if self.outcome == 0:
                self.outcome = -1

        if self.outcome != 0:
            root.destroy()

    # (helper function): return true if and only if all non-bomb squares have been uncovered (game is won) 
    def isGameWon(self):
        cnt = 0
        for row in range(self.numRows):
            for col in range(self.numCols):
                if self.button[row][col]['state'] != 'disabled': cnt += 1
        return cnt == self.numBombs

    # (helper function): return true if and only if a square (r, c) is within the game grid
    def squareInBounds(self, r, c):
        return r >= 0 and c >= 0 and r < self.numRows and c < self.numCols

    # (helper function): return true if and only if the board has all covered (unopened) squares
    def isNewBoard(self):
        for row in range(self.numRows):
            for col in range(self.numCols):
                if self.button[row][col]['state'] == 'disabled':
                    return False
        return True   

    # (helper function): change the color of specified square to blue to indicate this is the square you will select next
    def highlight_button(self, square):
        if self.squareInBounds(square[0], square[1]):
            self.button[square[0]][square[1]]["bg"] = "blue"  

    # (helper function): get the current board state from player POV. Note -1 represents unknown square
    def getBoardState(self):
        board = np.full((self.numRows, self.numCols), -1)
        for row in range(self.numRows):
            for col in range(self.numCols):
                value = 0
                if self.button[row][col]['state'] == 'disabled':
                    if self.button[row][col]["text"] != "":
                        value = int(self.button[row][col]["text"])
                    board[row][col] = value
        return board

    # generate a random board based on inputs {self.numRows, self.numCols, self.numBombs, self.safeSquare}
    def generate_board(self):

        # Create a safe 3x3 grid around the safe starting square
        bombsNotAllowed = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                r = self.safeSquare[0] + dx
                c = self.safeSquare[1] + dy
                if self.squareInBounds(r, c):
                    bombsNotAllowed.append((r, c))

        self.ans = np.full((self.numRows, self.numCols), 0)

        # Add self.numBombs number of bombs to the ans grid 
        self.bombLocations = []
        while len(self.bombLocations) < self.numBombs:
            tempX = random.randint(0, self.numRows - 1)
            tempY = random.randint(0, self.numCols - 1)
            if (tempX, tempY) not in self.bombLocations and (tempX, tempY) not in bombsNotAllowed:
                self.bombLocations.append((tempX, tempY))
                self.ans[tempX][tempY] = 9

        # Add numbers 0-8 to the ans grid 
        for row in range(self.numRows):
            for col in range(self.numCols):
                if self.ans[row][col] == 0:
                    squareValue = 0
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            r = row + dx
                            c = col + dy
                            if self.squareInBounds(r, c) and self.ans[r][c] == 9:
                                squareValue += 1   
                    self.ans[row][col] = squareValue

        print(self.ans)

        output = ""
        for row in self.ans:
            for val in row:
                output = output + str(val)
        print(output)

    # parse the user's command and perform the appropriate action.
    def parseAIAlgo(self, userCommand):
        if type(userCommand) is not tuple:
            print("cannot parse command")
        elif "open_square" in userCommand[0]:
            self.nextSquareToOpen = userCommand[1]
            self.highlight_button(self.nextSquareToOpen)
        elif "final_answer" in userCommand[0]:
            userAnswer = userCommand[1]
            if set(self.bombLocations) == set(userAnswer):
                self.outcome = 1
                numDigs = np.count_nonzero(self.getBoardState() != -1)
                print(f"YOU WON! You performed {numDigs} digs")
            else:
                self.outcome = -1
                print(f"WRONG BOMB LIST. expected: {self.bombLocations}, received: {userAnswer}")
            root.destroy()

    """
    Each time you click the button, We would recommend you to perform the following loop in your algorithm:
    1) uncover the best square computed last iteration using `self.open_button(r, c)`. Note a safe square is given for the first iteration
    2) perform your algorithm to find the best square using performAI1()
    3) visually display the square you will select on the next iteration (blue square) using self.highlight_button(r, c)
    """
    def AIAlgo(self):
        if self.outcome != 0:
            return # game is already over (won or loss)

        if self.isNewBoard():
            self.open_button(self.safeSquare[0], self.safeSquare[1])
        else:
            self.open_button(self.nextSquareToOpen[0], self.nextSquareToOpen[1])

        if self.outcome != 0:
            return # game is already over (won or loss)

        boardState = self.getBoardState()
        userCommand = self.AI.performAI(boardState)
        self.parseAIAlgo(userCommand)      

        if self.outcome == 0:
            self.AIAlgo()


parser = argparse.ArgumentParser()
parser.add_argument('-r', default = 10, type=int, help='number of rows on the board')
parser.add_argument('-c', default = 10, type=int, help='number of cols on the board')
parser.add_argument('-b', default = 10, type=int, help='number of bombs on the board')
parser.add_argument('-safe', default = [0, 0], nargs='+', type=int, help='the safe square on the board: (r, c)')
parser.add_argument('-type', default = 1, type=int, help='the AI to use (1 or 2)')
parser.add_argument('-numgames', default = 10, type=int, help='the number of games to play')
args = parser.parse_args()

numGames = args.numgames

numWins = 0
numLosses = 0
for i in range(numGames):
    print(f"match={i+1}")
    root = Tk()
    root.geometry("800x800")
    
    app = Window(numRows = args.r, numCols = args.c, numBombs = args.b, safeSquare = tuple(args.safe), AIType = args.type, master = root)
    root.mainloop()

    outcome = "ERROR"
    if app.outcome == -1: 
        outcome = "LOSS"
        numLosses += 1
    elif app.outcome == 1:
        outcome = "WON"
        numWins += 1

    print(f"outcome={outcome}")
    print("\n************\n")
    
print(f"totalWins={numWins}, totalLosses={numLosses}, winPercentage={numWins/numGames}")

