import math
import random


class TreeNode:
    def __init__(self, total_value, visit_count, probability, parent=None, position=[]):
        self.total_value = total_value
        self.visit_count = visit_count
        self.probability = probability
        self.parent = parent
        self.children = []
        # The position is represented as a list of moves in LAN that have been made.
        self.position = position

    def is_own_move(self, is_white):
        white_to_play = len(self.position) % 2 == 0
        if is_white:
            return white_to_play
        else:
            return not white_to_play

    def add_child(self, child_node):
        self.children.append(child_node)

    def has_children(self):
        return len(self.children) > 0

    def expand_with_probability_distribution(self, probability_distribution):
        # probability_distribution needs to be a list of tuples of the form ('move', probability)
        for entry in probability_distribution:
            new_node = TreeNode(total_value=0, visit_count=0, probability=entry[1],
                                parent=self, position=self.position.copy())
            new_node.position.append(entry[0])
            self.add_child(new_node)

    def get_child_with_highest_uct(self):
        if not self.has_children():
            return None

        highest_uct_value = -math.inf
        highest_uct_child = None

        for child in self.children:
            uct_value = child.get_uct()

            if uct_value > highest_uct_value:
                highest_uct_value = uct_value
                highest_uct_child = child

        return highest_uct_child

    def get_uct(self):
        if self.visit_count <= 0:
            return math.inf
        else:
            exploitation = self.total_value / self.visit_count
            exploration = 2 * math.sqrt(math.log(self.parent.visit_count) / self.visit_count)
            return self.probability * (exploitation + exploration)

    def get_best_move(self):
        best_child = self.get_highest_value_child()
        if best_child is None:
            return None
        return best_child.position[len(best_child.position) - 1]

    def select_child(self, is_white):
        if self.is_own_move(is_white):
            selected_child = self.get_child_with_highest_uct()
        else:
            selected_child = self.get_random_child()
        return selected_child

    def get_random_child(self):
        if not self.has_children():
            return None

        random_value = random.random()
        for child in self.children:
            if random_value < child.probability:
                return child
            else:
                random_value -= child.probability

        # In case no child was selected.
        return self.children[0]

    def get_highest_value_child(self):
        if not self.has_children():
            return None

        highest_value_child = None
        highest_value_amount = -math.inf

        for child in self.children:
            if child.visit_count == 0:
                continue
            child_value = child.total_value / child.visit_count

            if child_value > highest_value_amount:
                highest_value_amount = child_value
                highest_value_child = child

        return highest_value_child
