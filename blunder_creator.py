import backends
import stockfish_utility
from treenode import TreeNode
import chess


weak_evaluator = backends.player_model_evaluator
strong_evaluator = backends.strong_evaluator

playing_as_white = None
engine_culling = .02
opponent_culling = .02


def get_best_move(position):

    # e4 player for sharper positions. Consider this an opening book.
    if len(position) == 0:
        return 'e2e4'

    global playing_as_white
    playing_as_white = len(position) % 2 == 0

    # Select engine
    current_value = get_position_value(position)
    if current_value > .9:
        return stockfish_utility.get_best_move(position)

    root_node = TreeNode(total_value=0, visit_count=0, probability=1.0, position=position)

    # Expand root node with candidate moves.
    legal_moves = get_engine_moves(position)
    probabilities = []
    for i in range(len(legal_moves)):
        probabilities.append(1.0)
    probability_distribution = list(zip(legal_moves, probabilities))

    root_node.expand_with_probability_distribution(probability_distribution)

    # Expand child chance nodes.
    children = root_node.children
    positions = []
    for child in children:
        positions.append(child.position)

    evaluations = weak_evaluator.get_evaluations_from_moves(positions)

    leaf_nodes = []

    for index in range(len(children)):
        probability_distribution = evaluations[index].move_policy_list

        # Cull opponent move set
        probability_distribution = get_simplified_probability_distribution(probability_distribution, opponent_culling)

        children[index].expand_with_probability_distribution(probability_distribution)
        leaf_nodes.extend(children[index].children)

    # Evaluate each player response node and propagate its value upward.
    for leaf in leaf_nodes:
        leaf_value = get_position_value(leaf.position)
        leaf.total_value = leaf_value

        leaf.parent.total_value += leaf_value * leaf.probability

    # Set values of candidate moves that are terminal nodes.
    for child in children:
        if is_terminal_position(child.position):
            result = get_result(child.position)
            child.total_value = result
            if child.total_value >= 1.0:
                child.total_value = 100

    # Get best move.
    max_child = children[0]
    max_value = children[0].total_value

    for child in children:
        if child.total_value > max_value:
            max_child = child
            max_value = child.total_value

    return max_child.position[len(max_child.position) - 1]


def get_legal_moves(position):

    board = chess.Board()
    for move in position:
        board.push_uci(move)

    legal_moves = []
    for legal_move in board.legal_moves:
        legal_moves.append(legal_move.uci())

    return legal_moves


def get_engine_moves(moves_list):

    if engine_culling <= 0.0:
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
        policies_list = get_simplified_probability_distribution(policies_list, engine_culling)

        legal_moves = []
        for policy in policies_list:
            legal_moves.append(policy[0])

    return legal_moves


def get_position_value(position):

    if is_terminal_position(position):
        return get_result(position)

    position_as_list = [position]

    value = strong_evaluator.get_expected_outcomes_from_moves(position_as_list)[0]

    value = (value + 1.0) / 2.0

    if playing_as_white:
        return value
    else:
        return 1.0 - value


def is_terminal_position(position):
    board = chess.Board()
    for move in position:
        board.push_uci(move)

    outcome = board.outcome(claim_draw=True)
    if outcome is not None:
        return True
    else:
        return False


def get_result(position):

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

    if not playing_as_white:
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
