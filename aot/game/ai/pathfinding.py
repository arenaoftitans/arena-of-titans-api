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


def a_star(start, goal, board):
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
    fscore[start] = heuristic_cost_estimate(start, goal)

    while len(open_set) > 0:
        current = get_node_lowest_fscore(fscore, open_set)
        if current == goal:
            return reconstruct_path(came_from, current)

        open_set.remove(current)
        closed_set.add(current)
        for neighbor in board.get_neighbors(current):
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
            fscore[neighbor] = gscore[neighbor] + heuristic_cost_estimate(neighbor, goal)

    return []  # pragma: no cover


def heuristic_cost_estimate(start, goal):
    return 10 * (abs(start.x - goal.x) + abs(start.y - goal.y))


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
