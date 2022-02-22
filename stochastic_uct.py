import backends
from treenode import TreeNode
import chess


weak_evaluator = backends.player_model_evaluator
strong_evaluator = backends.strong_evaluator


playing_as_white = None
opponent_probability_cutoff = 0.0
engine_culling_cutoff = 0.0
tendril_count = 16


def get_best_move(position, nodes_limit, own_probability_cutoff, enemy_probability_cutoff):
    global playing_as_white
    playing_as_white = len(position) % 2 == 0

    global engine_culling_cutoff
    engine_culling_cutoff = own_probability_cutoff

    global opponent_probability_cutoff
    opponent_probability_cutoff = enemy_probability_cutoff

    root_node = TreeNode(total_value=0, visit_count=0, probability=1.0, position=position)

    nodes_count = 0
    while nodes_count < nodes_limit // tendril_count:
        perform_iteration(root_node)
        nodes_count += 1

    best_move = root_node.get_best_move()
    if best_move is None:
        best_move = get_best_legal_move(position)

    return best_move


def perform_iteration(root_node):

    #
    # TRAVERSAL
    #

    leaf_nodes = []
    for i in range(tendril_count):
        leaf_node = root_node
        while leaf_node.has_children():
            leaf_node = leaf_node.select_child(playing_as_white)

        leaf_nodes.append(leaf_node)

    leaf_nodes = remove_list_duplicates(leaf_nodes)

    #
    # EXPANSION
    #

    chance_nodes = []
    chance_node_positions = []

    for index in range(len(leaf_nodes)):
        # Skip expansion if the node is terminal.
        if is_terminal_position(leaf_nodes[index].position):
            pass
        elif leaf_nodes[index].visit_count > 0:
            if leaf_nodes[index].is_own_move(playing_as_white):
                # Own move node
                legal_moves = get_legal_moves_from_position(leaf_nodes[index].position)
                probabilities = []
                for i in range(len(legal_moves)):
                    probabilities.append(1.0)
                probability_distribution = list(zip(legal_moves, probabilities))

                leaf_nodes[index].expand_with_probability_distribution(probability_distribution)
                leaf_nodes[index] = leaf_nodes[index].select_child(playing_as_white)

            else:
                # Chance node
                chance_nodes.append(leaf_nodes[index])
                chance_node_positions.append(leaf_nodes[index].position)

    chance_evaluations = weak_evaluator.get_evaluations_from_moves(chance_node_positions)
    for index in range(len(chance_nodes)):
        leaf_index = leaf_nodes.index(chance_nodes[index])
        probability_distribution = chance_evaluations[index].move_policy_list

        probability_distribution = get_simplified_probability_distribution(probability_distribution,
                                                                           opponent_probability_cutoff)

        leaf_nodes[leaf_index].expand_with_probability_distribution(probability_distribution)
        leaf_nodes[leaf_index] = leaf_nodes[leaf_index].select_child(playing_as_white)

    #
    # ROLLOUT
    #

    positions = []

    for leaf in leaf_nodes:
        positions.append(leaf.position)
    expected_values = strong_evaluator.get_expected_outcomes_from_moves(positions)

    for index in range(len(leaf_nodes)):
        if is_terminal_position(leaf_nodes[index].position):
            expected_values[index] = get_result(leaf_nodes[index].position, playing_as_white)
        else:
            expected_values[index] = (expected_values[index] + 1.0) / 2.0

            if not playing_as_white:
                expected_values[index] = 1.0 - expected_values[index]  # Reverse objective value if playing as black

    #
    # BACKPROPAGATION
    #

    for index in range(len(leaf_nodes)):

        curr_node = leaf_nodes[index]

        while curr_node is not None:
            curr_node.visit_count += 1
            curr_node.total_value += expected_values[index]

            curr_node = curr_node.parent


def get_legal_moves_from_position(moves_list):

    if engine_culling_cutoff <= 0.0:
        board = chess.Board()
        for move in moves_list:
            board.push_uci(move)

        legal_moves = []
        for legal_move in board.legal_moves:
            legal_moves.append(legal_move.uci())

    else:
        evaluation = strong_evaluator.get_full_evaluation_from_moves(moves_list)
        policies_list = evaluation.move_policy_list

        # Remove the most unpromising moves.
        policies_list = get_simplified_probability_distribution(policies_list, engine_culling_cutoff)

        legal_moves = []
        for policy in policies_list:
            legal_moves.append(policy[0])

    return legal_moves


def is_terminal_position(position):
    board = chess.Board()
    for move in position:
        board.push_uci(move)

    outcome = board.outcome(claim_draw=True)
    if outcome is not None:
        return True
    else:
        return False


def get_result(position, is_white):

    board = chess.Board()
    for move in position:
        board.push_uci(move)
    outcome = board.outcome(claim_draw=True)
    if outcome.result() == "1-0":
        result = 1.0
    elif outcome.result() == "0-1":
        result = 0.0
    else:
        result = 0.5

    if not is_white:
        result = 1.0 - result

    return result


def get_simplified_probability_distribution(distribution, cutoff):

    new_distribution = []
    new_distribution_sum = 0.0
    for element in distribution:
        if element[1] < cutoff:
            pass
        else:
            new_distribution_sum += element[1]

    for element in distribution:
        if element[1] < cutoff:
            pass
        else:
            new_distribution.append((element[0], element[1] / new_distribution_sum))

    return new_distribution


def probability_distribution_sort(entry):
    return entry[1]


# Quickly return the legal move with the highest policy value.
def get_best_legal_move(position):

    evaluation = strong_evaluator.get_full_evaluation_from_moves(position)
    legal_moves = evaluation.move_policy_list
    legal_moves.sort(key=probability_distribution_sort, reverse=True)

    return legal_moves[0][0]


def remove_list_duplicates(input_list):
    output_list = []
    for element in input_list:
        if element not in output_list:
            output_list.append(element)

    return output_list
