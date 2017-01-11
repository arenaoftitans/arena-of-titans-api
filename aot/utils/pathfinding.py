################################################################################
# Copyright (C) 2015-2016 by Arena of Titans Contributors.
#
# This file is part of Arena of Titans.
#
# Arena of Titans is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Arena of Titans is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
################################################################################

from aot.utils.heuristic import (
    CORRECT_X_LEFT,
    DISTANCE_BRANCH_TO_BRANCH,
    Side,
)


def a_star(start, goal, board, movements_types=None):
    '''A* algorithom to find shortest path from start to goal

    Take and adapted from https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode
    '''

    # The set of nodes already evaluated
    closed_set = set()
    # The set of currently discovered nodes still to be evaluated.
    # Initially, only the start node is known.
    open_set = {start}
    # For each node, which node it can most efficiently be reached from.
    # If a node can be reached from many nodes, cameFrom will eventually contain the
    # most efficient previous step.
    came_from = {}

    # For each node, the cost of getting from the start node to that node.
    gscore = {}
    # The cost of going from start to start is zero.
    gscore[start] = 0
    # For each node, the total cost of getting from the start node to the goal
    # by passing by that node. That value is partly known, partly heuristic.
    fscore = {}
    # For the first node, that value is completely heuristic.
    fscore[start] = heuristic_cost_estimate(start, goal, board)

    while len(open_set) > 0:
        current = get_node_lowest_fscore(fscore, open_set)
        if current == goal:
            return reconstruct_path(came_from, current)

        open_set.remove(current)
        closed_set.add(current)
        for neighbor in board.get_neighbors(current, movements_types=movements_types):
            if neighbor in closed_set:
                continue  # Ignore the neighbor which is already evaluated.
            # The distance from start to a neighbor. The dist between current and neighbors is
            # always 1.
            tentative_gscore = gscore[current] + 1
            if neighbor not in open_set:  # Discover a new node
                open_set.add(neighbor)
            elif tentative_gscore >= gscore[neighbor]:
                continue  # This is not a better path.

            # This path is the best until now. Record it!
            came_from[neighbor] = current
            gscore[neighbor] = tentative_gscore
            fscore[neighbor] = gscore[neighbor] + heuristic_cost_estimate(neighbor, goal, board)

    return []  # pragma: no cover


def heuristic_cost_estimate(start, goal, board):
    '''Give an estimation of the cost required to go from start to goal.

    The cost is calculated as follows:

    1. If the two squares are in the same arm, we compute the absolute difference between the
       two abscissas and the two ordinates.
    2. If they are not, we get the distance between the two branches from a static map. We then
       estimate the distance to get from on to the other. To do that, we compute the adjusted
       distance depending on the side in x (x0 is at 1 from x31, at 2 from x30 but at 4 from
       x4, 5 from x5 and so on) and the distance in ordinate.
    '''
    no_arm_start = board.get_arm_id(start)
    no_arm_goal = board.get_arm_id(goal)

    if no_arm_start == no_arm_goal:
        xx = abs(start.x - goal.x)
        yy = abs(start.y - goal.y)
        if xx == yy:
            # Moving in diagonal
            return 10 * xx
        else:
            if xx == 0 or yy == 0:
                return 10 * (xx + yy)
            else:
                return 10 * (xx + yy - 1)
    else:
        branch_distance = DISTANCE_BRANCH_TO_BRANCH[no_arm_start][no_arm_goal]
        start_x_corrected = start.x % board.arms_width
        goal_x_corrected = goal.x % board.arms_width
        if branch_distance.side == Side.LEFT:
            goal_x_corrected = CORRECT_X_LEFT[goal_x_corrected]
            arm_distance = start_x_corrected + goal_x_corrected
        else:
            goal_x_corrected += board.arms_width
            arm_distance = goal_x_corrected - start_x_corrected

        return 20 * branch_distance.distance + arm_distance + abs(start.y - goal.y)


def get_node_lowest_fscore(fscore, open_set):
    score_min = float('inf')
    square_min = None
    for square, score in fscore.items():
        if score < score_min and square in open_set:
            score_min = score
            square_min = square

    return square_min


def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path
