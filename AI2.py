import random

class Variable:
    def __init__(self, posX, posY):
        self.value = "unk"
        self.posX = posX
        self.posY = posY
        self.constraints = set()

    def remove_from_constraints(self, ai2):
        for constraint in self.constraints.copy():
            if self in constraint.variables:
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

    # Checks solution does not YET violate constraints
    def verify_soln_possible(self, const_list):
        for constraint in const_list:
            curr = constraint.target
            for variable in constraint.variables:
                if not variable.value == "unk":
                    curr -= variable.value
            if curr < 0:
                return False
        return True

    # Checks solution satisfies the constraints
    def vertify_soln_valid(self, const_list):
        for constraint in const_list:
            curr = constraint.target
            for variable in constraint.variables:
                curr -= variable.value
            if not curr == 0:
                return False
        return True

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


    def get_choice(self):
        if self.board.first_move:
            self.board.first_move = False
            self.vboard[self.board.start_y][self.board.start_x].value = 0

            self.add_constraint(self.board.start_x, self.board.start_y)

            self.remaining_spaces -= 1
            self.unprobed.remove(self.vboard[self.board.start_y][self.board.start_x])

            return str(self.board.start_y), str(self.board.start_x)  # return safe starting choice if on first move

        queue = []
        if len(self.mine_queue) > 0:
            queue = self.mine_queue
        elif len(self.safe_queue) > 0:
            queue = self.safe_queue

        # Step 1: Look through every space on the board and define a constraint such that the NUMBER revealed by the space
        #  is equal to the true value of the bomb/empty space around that tile

        # Step 2: Try to simplify the constraints by seeing if any sets of variables fit completely within another set of constraints
        #   If any of the constraints become trivial begin probing again like in step 1

        if len(queue) > 0:
            move = queue.pop(0)
            x, y = move[0], move[1]

            self.update_csp(x, y, move[2] == "m")

            # print(self.safe_queue)
            # print(self.mine_queue)
            # print(self.constraints)

            return str(move[1]) + str(move[2]), str(move[0])

        # Step 3: Group constraints that share variables and use backtracking to find solutions for those clusters.  Now look at how many mines
        #   each of these clusters requires for their solutions and make sure it adds up with the remaining mines in the game (even when combined
        #   with other clusters)

        # This would be a good place to use the Union Find Data structure to improve time complexity
        # For now perform bfs on the constraints to find connected components
        visited_vars = set()
        unvisited = self.constraints.copy()
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

        random_prob = self.remaining_bombs / self.remaining_spaces
        # print(random_prob)

        # We have found a spot that is better than random guessing
        if min_probability <= random_prob:
            self.update_csp(best_pick.posX, best_pick.posY, False)
            return str(best_pick.posY), str(best_pick.posX)
        else: # We have to pick randomly

            # Step 6: If the lowest probability is higher than just guessing randomly then actually randomly guess instead**
            #   Random comes with a caveat that corners are better and tiles with overlapping variables in the constraint are better
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
