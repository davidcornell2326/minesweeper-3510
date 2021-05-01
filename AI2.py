import random

# A Class to Represent Variables in the Constraint Satisfaction Problem
# A Variable in minesweeper is a tile which either has a known value of 0 or 1, or an unknown value (which
#  is still in the domain of 0-1).  0 means an empty tile, while 1 means the tile has a mine.
# Each variable has a value, and (x,y) pos, and a set of constraints which it is a part of (see Constraint below).
class Variable:
    def __init__(self, posX, posY):
        self.value = "unk"
        self.posX = posX
        self.posY = posY
        self.constraints = set()

    # Loop through all the constraints that this variable is a part of and remove the variable from it (and subtract
    #  the value of this variable from the constraints target count).  This may happen when the value of this variable
    #  has been determined so it is no longer an uncertain "free" variable in a constraint.
    def remove_from_constraints(self, ai2):
        for constraint in self.constraints.copy():
            if self in constraint.variables:
                constraint.variables.remove(self)
                constraint.target -= self.value
            constraint.update_variables(ai2)
        self.constraints = set()

    # Enables addition of known variables like A + B using addition operator
    def __add__(self, other):
        if type(other) is Variable:
            return self.value + other.value
        return self.value + other

    # Returns string representation of variable
    def __repr__(self):
        return "(" + str(self.posX) + "," + str(self.posY) + ")"


# A Class to represent Constraints in the Minesweeper Constraint Satisfaction Problem
#  A Constraint in minesweeper arises when we know the value of a numbered tile and the unknown tiles surrounding it
#  We can formulate an equation that VALUE = VAR1 + VAR2 + ...  When satisfied this equation will give us a potentially
#  valid board configuration that satisfies the requirements of this number tile.  When all constraints are satisfied we
#  have a potentially viable solution to the whole board.
class Constraint:
    def __init__(self, target, variables):
        self.target = target
        self.variables = variables

    # Loop through all the variables that this constraint has.  If the constraint has been reduced to 0 then all surrounding
    #  tiles are safe.  If the constraint target is equal to the number of unknowns then they must all be mines.  Set the
    #  variables and remove them from other constraints accordingly.
    def update_variables(self, ai2):
        if self.target == 0:
            for variable in self.variables.copy():
                variable.value = 0
                var_tuple = (variable.posX, variable.posY, "")
                if variable in ai2.unprobed and var_tuple not in ai2.safe_queue:
                    ai2.safe_queue.append(var_tuple)
                if self in variable.constraints:
                    variable.constraints.remove(self)
                    variable.remove_from_constraints(ai2)
            self.variables = set()
            if self in ai2.constraints:
                ai2.constraints.remove(self)
        elif self.target == len(self.variables):
            for variable in self.variables.copy():
                variable.value = 1
                var_tuple = (variable.posX, variable.posY, "m")
                if variable in ai2.unprobed and var_tuple not in ai2.mine_queue:
                    ai2.mine_queue.append(var_tuple)
                if self in variable.constraints:
                    variable.constraints.remove(self)
                    variable.remove_from_constraints(ai2)
            self.variables = set()
            if self in ai2.constraints:
                ai2.constraints.remove(self)

    # If another constraint is a complete subset of this constraint then we should remove it from this constraint
    #  and also subtract it's target value from this one.  For instance if 2 = VAR1 + VAR2 + VAR3 and 1 = VAR1 + VAR2
    #  we could satisfy the first constraint to 1 = VAR3 (which of course we then could update the variables, etc.)
    def remove_subset(self, constraint, ai2):
        for variable in constraint.variables:
            self.variables.remove(variable)
        self.target -= constraint.target
        self.update_variables(ai2)

    # Returns a string representation of the instance of the Constraint class.
    def __repr__(self):
        output = []
        for var in self.variables:
            output.append(str(var))
        return str(self.target) + " = " + " + ".join(output)

# Loops through and returns all the surrounding tiles to a given (x,y) coordinate which have an unknown variable value.
#  Also returns a count of the known variable values surrounding the tile so this can be subtracted from the numeric tile
#  to get the target value of just the unknown tiles.
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


# A Class to implement a Minesweeper AI.  Given a board it will continue to return moves when get_choice() is called
#  until the game is completed
class AI2:
    def __init__(self, board):
        self.board = board
        self.safe_queue = []
        self.mine_queue = []
        self.vboard = []
        self.unprobed = set()
        for y in range(board.height):
            self.vboard.append([])
            for x in range(board.width):
                new_var = Variable(x, y)
                self.vboard[y].append(new_var)
                self.unprobed.add(new_var)
        self.constraints = set()
        self.move_queue = []
        self.remaining_bombs = self.board.bomb_count
        self.remaining_spaces = self.board.width * self.board.height
        self.details = False

    # Helper method to add a constraint at a specified (x,y) coordinate.  Also adds the new constraint to the constraint
    #  list for all variables in the constraint
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

    # Checks if a constraint is a subset of any other constraint and removes the subset if it is
    def check_constraint(self, constraint):
        for constr in self.constraints.copy():
            if constr == constraint:
                continue
            if constr.variables.issubset(constraint.variables) and len(constr.variables) > 0:
                constraint.remove_subset(constr, self)
            elif constraint.variables.issubset(constr.variables) and len(constraint.variables) > 0:
                constr.remove_subset(constraint, self)

    # Updates the constraint satisfaction problem based on a new probed (x,y) position (and whether or not this was
    #  flagging a mine or probing the spot for info).  Updates the remaining free spots and bombs, but also removes the
    #  variable from constraints if it is in any since the value is known now, and adds a constraint in the current spot
    #  if the current spot contains a number indicating the amount of surrounding mines
    def update_csp(self, x, y, flagging):
        self.remaining_spaces -= 1
        self.unprobed.remove(self.vboard[y][x])
        if self.board.grid_actual[y][x] == 9:
            self.remaining_bombs -= 1
            self.vboard[y][x].value = 1
        elif flagging:
            # print("DEBUG: ALGORITHM MADE A MISTAKE FLAGGING!!")
            self.remaining_bombs -= 1
            self.vboard[y][x].value = 1
        else:
            self.vboard[y][x].value = 0

        self.vboard[y][x].remove_from_constraints(self)

        if not self.board.grid_actual[y][x] == 9 and not flagging:
            constraint = self.add_constraint(x, y)
            if constraint is not None and len(constraint.variables) > 0:
                self.check_constraint(constraint)
        if self.details:
            print("Safe queue:", self.safe_queue)
            print("Mine queue:", self.mine_queue)
            print("Constraints:", self.constraints)

    # Checks if a possible solution does not YET violate constraints
    def verify_soln_possible(self, const_list):
        for constraint in const_list:
            curr = constraint.target
            for variable in constraint.variables:
                if not variable.value == "unk":
                    curr -= variable.value
            if curr < 0:
                return False
        return True

    # Checks if a possible solution satisfies all the constraints in const_list
    def vertify_soln_valid(self, const_list):
        for constraint in const_list:
            curr = constraint.target
            for variable in constraint.variables:
                curr -= variable.value
            if not curr == 0:
                return False
        return True

    # Recursive helper method to generate all possible solutions using variables in var_list that satisfy all
    #  constraints in const_list.  Adds mines to mine_list and eventually adds solutions to solns.  Uses backtracking
    #  to generate every possible solution.  Immediately stops backtracking chain when a constraint is dissatisfied.
    def generate_solutions(self, var_list, const_list, mine_list, solns=[]):
        if len(var_list) == 0:
            if self.vertify_soln_valid(const_list):
                solns.append(mine_list)
            return
        curr = var_list.pop(0)
        curr.value = 1
        if self.verify_soln_possible(const_list):
            self.generate_solutions(var_list, const_list, mine_list + [curr], solns)
        curr.value = 0
        if self.verify_soln_possible(const_list):
            self.generate_solutions(var_list, const_list, mine_list, solns)
        curr.value = "unk"
        var_list.insert(0, curr)

    # Pick a random tile "smartly".  For instance pick one of the corners and if this doesn't work at least pick a tile
    #  we haven't probed yet
    def pick_random_smart(self):
        rem_corners = []
        if self.vboard[0][0] in self.unprobed:
            rem_corners.append((0, 0))
        if self.vboard[self.board.height - 1][0] in self.unprobed:
            rem_corners.append((0, self.board.height - 1))
        if self.vboard[0][self.board.width - 1] in self.unprobed:
            rem_corners.append((self.board.width - 1, 0))
        if self.vboard[self.board.height - 1][self.board.width - 1] in self.unprobed:
            rem_corners.append((self.board.width - 1, self.board.height - 1))
        if len(rem_corners) > 0:
            corner = random.choice(rem_corners)
            self.update_csp(corner[0], corner[1], False)
            return str(corner[1]), str(corner[0])
        else:
            spot = random.sample(self.unprobed, 1)[0]
            self.update_csp(spot.posX, spot.posY, False)
            return str(spot.posY), str(spot.posX)

    # Returns the next choice of tile to mark or probe by the minesweeper algorithm
    def get_choice(self, details):
        self.details = details
        # If it is the first move we just return the safe space and add its constraints
        if self.board.first_move:
            self.board.first_move = False
            self.update_csp(self.board.start_x, self.board.start_y, False)

            return str(self.board.start_y), str(self.board.start_x)  # return safe starting choice if on first move

        # Now we should check if we have a queue of mine tiles to mark or safe tiles to probe
        queue = []
        if len(self.mine_queue) > 0:
            queue = self.mine_queue
        elif len(self.safe_queue) > 0:
            queue = self.safe_queue

        # Step 1: Look through every space on the board and define a constraint such that the NUMBER revealed by the space
        #  is equal to the true value of the bomb/empty space around that tile

        # Step 2: Try to simplify the constraints by seeing if any sets of variables fit completely within another set of constraints
        #   If any of the constraints become trivial begin probing again like in step 1

        # If we have a queue of tiles then lets handle those first
        if len(queue) > 0:
            move = queue.pop(0)
            x, y = move[0], move[1]

            # Add the tile to the csp based on if it is meant to be a marked mine or a probed number tile
            self.update_csp(x, y, move[2] == "m")

            return str(move[1]) + str(move[2]), str(move[0])

        # Step 3: Group constraints that share variables and use backtracking to find solutions for those clusters.  Now look at how many mines
        #   each of these clusters requires for their solutions and make sure it adds up with the remaining mines in the game (even when combined
        #   with other clusters)

        # This would be a good place to use the Union Find Data structure to improve time complexity
        # For now perform bfs on the constraints to find connected components

        # Here we didn't have any tiles that were known to be safe or mines so we are going to find solutions which
        #  satisfy constraints.  Since this is a very expensive operation (using backtracking means we can have n! operations),
        #  we should try to reduce the size of our problem.  To do this we will separate the solutions into clusters of
        #  overlapping variables.  Not all constraints are connected so we can solve different constraint sets separately.
        #  To find which sets of constraints are connected we perform a breadth first search where the constraints are
        #  nodes and the variables are edges.  Then we form a list of sets of connected constraints/variables.
        visited_vars = set()
        unvisited = self.constraints.copy()
        if len(unvisited) == 0:
            return self.pick_random_smart()

        visit_queue = [next(iter(unvisited))]
        i = 0
        variable_sets = []
        constraint_sets = []
        while len(unvisited) > 0:
            variable_sets.append(set())
            constraint_sets.append(set())
            while len(visit_queue) > 0:
                curr = visit_queue.pop(0)
                if curr in unvisited:
                    unvisited.remove(curr)
                    for variable in curr.variables:
                        if variable not in visited_vars:
                            variable_sets[i].add(variable)
                            visited_vars.add(variable)
                            for constraint in variable.constraints:
                                if constraint in unvisited:
                                    visit_queue.append(constraint)
                                    constraint_sets[i].add(constraint)
            if len(unvisited) > 0:
                visit_queue.append(next(iter(unvisited)))
            i += 1

        # Now that we have found a set of connected variables/constraints we must find the solutions that satisfy each
        #  of these constraint clusters.  Loop through them generating solutions.  Also initialize a probability dict
        #  to have zero probability that any of the tiles are mines in these constraints for now (to be updated later)
        proposed_mine_clusters = []
        probabilities = {}
        for var_set, const_set in zip(variable_sets, constraint_sets):
            solns = []
            self.generate_solutions(list(var_set), list(const_set), [], solns)
            proposed_mine_clusters.append(solns)
            for variable in var_set:
                probabilities[variable] = 0.0

        # TODO This is where we could implement checking if any of the proposed solutions have too many mines

        guaranteed_mine = []
        guaranteed_safe = []
        min_probability = 1.1
        best_pick = None
        # Compute the probability that each position is safe or has a mine based on proposed solutions
        # Basically check how many times each tile is safe and how many times it is a mine across all possible solutions
        for var_set, solns in zip(variable_sets, proposed_mine_clusters):
            for soln in solns:
                for variable in soln:
                    probabilities[variable] += 1
            for variable in var_set:
                probabilities[variable] /= len(solns)
                if probabilities[variable] == 0.0:
                    guaranteed_safe.append(variable)
                if probabilities[variable] == 1.0:
                    guaranteed_mine.append(variable)
                if probabilities[variable] < min_probability:
                    min_probability = probabilities[variable]
                    best_pick = variable

        # Probability 1 = guaranteed mine
        # Probability 0 = guaranteed safe
        ret = None
        if len(guaranteed_mine) > 0:
            m = guaranteed_mine.pop(0)
            ret = (m.posX, m.posY, "m")
        elif len(guaranteed_safe) > 0:
            s = guaranteed_safe.pop(0)
            ret = (s.posX, s.posY, "")

        # Step 4: If the solution set has any guaranteed mines then mark them.  If there are gauranteed free spaces we can probe them and add them to
        #   the constraint set and return to step 1

        for mine in guaranteed_mine:
            mine_tuple = (mine.posX, mine.posY, "m")
            if mine in self.unprobed and mine_tuple not in self.mine_queue:
                self.mine_queue.append(mine_tuple)
        for safe in guaranteed_safe:
            safe_tuple = (safe.posX, safe.posY, "")
            if safe in self.unprobed and safe_tuple not in self.safe_queue:
                self.safe_queue.append(safe_tuple)

        if ret:
            self.update_csp(ret[0], ret[1], "m" == ret[2])
            return str(ret[1]) + ret[2], str(ret[0])
        # print(probabilities)

        # Step 5: If there are no guarantees pick the square with the lowest probability of being a mine across all proposed solutions

        # compute the probability that a random tile (with absolutely no insight into the csp) has a mine
        random_prob = self.remaining_bombs / self.remaining_spaces
        # print(random_prob)

        # We have found a spot that is better than random guessing so pick that
        if min_probability <= random_prob:
            self.update_csp(best_pick.posX, best_pick.posY, False)
            return str(best_pick.posY), str(best_pick.posX)
        else: # We have to pick randomly

            # Step 6: If the lowest probability is higher than just guessing randomly then actually randomly guess instead**
            #   Random comes with a caveat that corners are better and tiles with overlapping variables in the constraint are better
            return self.pick_random_smart()

# Main method
if __name__ == "__main__":
    print("If you're seeing this, please read README.MD!!!")
