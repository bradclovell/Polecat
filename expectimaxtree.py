

class Node:

    def __init__(self, parent, position, local_probability, position_probability, children):
        self.parent = parent
        self.position = position
        self.local_probability = local_probability
        self.position_probability = position_probability
        self.children = children

    def add_child(self, child):
        self.children.append(child)

    def is_own_move(self, is_white):
        white_to_play = len(self.position) % 2 == 0
        if is_white:
            return white_to_play
        else:
            return not white_to_play

    def expand_with_probability_distribution(self, probability_distribution, position_probability_cutoff):
        # probability_distribution needs to be a list of tuples of the form ('move', probability)
        for entry in probability_distribution:
            if entry[1] * self.position_probability < position_probability_cutoff:
                continue
            new_node = Node(self, self.position.copy(), entry[1], entry[1] * self.position_probability, [])
            new_node.position.append(entry[0])
            self.add_child(new_node)
