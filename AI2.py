class Variable:
    def __init__(self, posX, posY):
        self.value = "unk"
        self.posX = posX
        self.posY = posY
        self.constraints = set()

    def remove_from_constraints(self, ai2):
        for constraint in self.constraints:
            constraint.variables.remove(self)
            constraint.target -= self.value
            constraint.update_variables(ai2)
        self.constraints = set()

    def __add__(self, other):
        if type(other) is Variable:
            return self.value + other.value
        return self.value + other

    def __repr__(self):
        return "(" + str(self.posX) + "," + str(self.posY) + ")"


class Constraint:
    def __init__(self, target, variables):
        self.target = target
        self.variables = variables

    def update_variables(self, ai2):
        if self.target == 0:
            for variable in self.variables:
                variable.value = 0
                ai2.safe_queue.append((variable.posX, variable.posY, ""))
                variable.constraints.remove(self)
                variable.remove_from_constraints(ai2)
            self.variables = set()
            ai2.constraints.remove(self)
        elif self.target == len(self.variables):
            for variable in self.variables:
                variable.value = 1
                ai2.mine_queue.append((variable.posX, variable.posY, "m"))
                variable.constraints.remove(self)
                variable.remove_from_constraints(ai2)
            self.variables = set()
            ai2.constraints.remove(self)

    def remove_subset(self, constraint, ai2):
        for variable in constraint.variables:
            self.variables.remove(variable)
        self.target -= constraint.target
        self.update_variables(ai2)

    def __repr__(self):
        output = []
        for var in self.variables:
            output.append(str(var))
        return str(self.target) + " = " + " + ".join(output)


def getAdjacentVariables(x, y, vboard):
    output = set()
    pre_def = 0
    for i in range(3):
        cX = x - 1 + i
        for j in range(3):
            cY = y - 1 + j
            if 0 <= cY < len(vboard) and 0 <= cX < len(vboard[0]) and not (i == 1 and j == 1):
                if vboard[cY][cX].value == "unk":
                    output.add(vboard[cY][cX])
                else:
                    pre_def += vboard[cY][cX].value
    return output, pre_def


class AI2:
    def __init__(self, board):
        self.board = board
        self.safe_queue = []
        self.mine_queue = []
        self.vboard = []
        for y in range(board.height):
            self.vboard.append([])
            for x in range(board.width):
                self.vboard[y].append(Variable(x, y))
        self.constraints = set()
        self.move_queue = []

    def add_constraint(self, x, y):
        variables, sub = getAdjacentVariables(x, y, self.vboard)
        if len(variables) > 0:
            constraint = Constraint(self.board.grid_actual[y][x] - sub, variables)
            self.constraints.add(constraint)
            for var in variables:
                var.constraints.add(constraint)
            constraint.update_variables(self)
            return constraint
        return None

    def check_constraint(self, constraint):
        for constr in self.constraints.copy():
            if constr == constraint:
                continue
            if constr.variables.issubset(constraint.variables) and len(constr.variables) > 0:
                constraint.remove_subset(constr, self)
            elif constraint.variables.issubset(constr.variables) and len(constraint.variables) > 0:
                constr.remove_subset(constraint, self)

    def update_csp(self, x, y, flagging):
        print(self.board.grid_actual[y][x])
        if self.board.grid_actual[y][x] == 9:
            self.vboard[y][x].value = 1
        elif flagging:
            print("DEBUG: ALGORITHM MADE A MISTAKE FLAGGING!!")
            self.vboard[y][x].value = 1
        else:
            self.vboard[y][x].value = 0

        self.vboard[y][x].remove_from_constraints(self)

        if not self.board.grid_actual[y][x] == 9 and not flagging:
            constraint = self.add_constraint(x, y)
            if constraint is not None and len(constraint.variables) > 0:
                self.check_constraint(constraint)

    def get_choice(self):
        if self.board.first_move:
            self.board.first_move = False
            self.vboard[self.board.start_y][self.board.start_x].value = 0

            self.add_constraint(self.board.start_x, self.board.start_y)

            print(self.safe_queue)
            print(self.mine_queue)
            print(self.constraints)

            return str(self.board.start_y), str(self.board.start_x)  # return safe starting choice if on first move

        queue = []
        if len(self.mine_queue) > 0:
            queue = self.mine_queue
        elif len(self.safe_queue) > 0:
            queue = self.safe_queue

        if len(queue) > 0:
            move = queue.pop(0)
            x, y = move[0], move[1]

            self.update_csp(x, y, move[2] == "m")

            print(self.safe_queue)
            print(self.mine_queue)
            print(self.constraints)

            return str(move[1]) + str(move[2]), str(move[0])

        # Step 1: Look through every space on the board and define a constraint such that the NUMBER revealed by the space
        #  is equal to the true value of the bomb/empty space around that tile

        # Step 2: Try to simplify the constraints by seeing if any sets of variables fit completely within another set of constraints
        #   If any of the constraints become trivial begin probing again like in step 1

        # Step 3: Group constraints that share variables and use backtracking to find solutions for those clusters.  Now look at how many mines
        #   each of these clusters requires for their solutions and make sure it adds up with the remaining mines in the game (even when combined
        #   with other clusters)

        # Step 4: If the solution set has any guaranteed mines then mark them.  If there are gauranteed free spaces we can probe them and add them to
        #   the constraint set and return to step 1

        # Step 5: If there are no guarantees pick the square with the lowest probability of being a mine across all proposed solutions

        # Step 6: If the lowest probability is higher than just guessing randomly then actually randomly guess instead**
        #   Random comes with a caveat that corners are better and tiles with overlapping variables in the constraint are better
