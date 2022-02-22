import backends
import chess
import math
from expectimaxtree import Node

weak_evaluator = backends.player_model_evaluator
strong_evaluator = backends.strong_evaluator


def expectiminimax(node, depth, value_to_beat, is_white):
    if is_terminal_position(node.position) or depth <= 0:
        heuristic = get_heuristic(node.position, is_white)
        return heuristic

    if node.is_own_move(is_white):
        # Expand node
        legal_moves = get_legal_moves_from_position(node.position)
        probabilities = []
        for i in range(len(legal_moves)):
            probabilities.append(1.0)
        probability_distribution = list(zip(legal_moves, probabilities))
        node.expand_with_probability_distribution(probability_distribution, probability_cutoff)

        # Node expansion may not produce any children due to the probability cutoff.
        if len(node.children) <= 0:
            heuristic = get_heuristic(node.position, is_white)
            return heuristic

        # Get maximum child
        max_value = -math.inf
        for child in node.children:
            child_value = expectiminimax(child, depth - 1, max_value, is_white)
            if child_value > max_value:
                max_value = child_value

        return max_value

    else:
        # Prune immediately if the sibling node is unbeatable.
        if value_to_beat >= 1.0:
            return 0.0

        # Expand node
        evaluation = weak_evaluator.get_full_evaluation_from_moves(node.position)
        probability_distribution = evaluation.move_policy_list

        # Simplifying here, an unsound way of saving time.
        probability_distribution = get_simplified_probability_distribution(probability_distribution,
                                                                           opponent_culling_cutoff)

        probability_distribution.sort(key=probability_distribution_sort, reverse=True)
        node.expand_with_probability_distribution(probability_distribution, probability_cutoff)

        # Node expansion may not produce any children due to the probability cutoff.
        if len(node.children) <= 0:
            heuristic = get_heuristic(node.position, is_white)
            return heuristic

        # Get expected value
        expected_value = 0.0
        remaining_weight = 1.0
        for child in node.children:
            max_possible_value = expected_value + remaining_weight

            # Prune if this node cannot hope to beat its sibling.
            if max_possible_value <= value_to_beat:
                return 0.0

            child_contribution = child.local_probability * expectiminimax(child, depth - 1, 0.0, is_white)
            expected_value += child_contribution

            remaining_weight -= child.local_probability

        return expected_value


# Minimum probability for any position to be considered.
probability_cutoff = 0.0

# Cutoff when culling policy distributions.
engine_culling_cutoff = 0.0

opponent_culling_cutoff = 0.0


def get_best_move(position, depth, position_probability_cutoff, move_culling_cutoff, enemy_culling_cutoff):
    global probability_cutoff
    probability_cutoff = position_probability_cutoff
    global engine_culling_cutoff
    engine_culling_cutoff = move_culling_cutoff
    global opponent_culling_cutoff
    opponent_culling_cutoff = enemy_culling_cutoff

    root_node = Node(None, position, 1.0, 1.0, [])
    is_white = len(position) % 2 == 0

    if is_terminal_position(root_node.position):
        return None

    if depth <= 0:
        return get_best_legal_move(position)

    # Expand node
    legal_moves = get_legal_moves_from_position(root_node.position)
    probabilities = []
    for i in range(len(legal_moves)):
        probabilities.append(1.0)
    probability_distribution = list(zip(legal_moves, probabilities))
    root_node.expand_with_probability_distribution(probability_distribution, probability_cutoff)

    # Node expansion may not produce any children due to the probability cutoff.
    if len(root_node.children) <= 0:
        return get_best_legal_move(position)

    # Get maximum child
    max_value = -math.inf
    max_child = None
    for child in root_node.children:
        child_value = expectiminimax(child, depth - 1, max_value, is_white)
        if child_value > max_value:
            max_value = child_value
            max_child = child

    return max_child.position[len(max_child.position) - 1]


def is_terminal_position(position):
    board = chess.Board()
    for move in position:
        board.push_uci(move)

    outcome = board.outcome(claim_draw=True)
    if outcome is not None:
        return True
    else:
        return False


def get_heuristic(position, is_white):
    if is_terminal_position(position):
        board = chess.Board()
        for move in position:
            board.push_uci(move)
        outcome = board.outcome(claim_draw=True)
        if outcome.result() == "1-0":
            heuristic = 1.0
        elif outcome.result() == "0-1":
            heuristic = 0.0
        else:
            heuristic = 0.5

    else:
        evaluation = strong_evaluator.get_expected_outcome_from_moves(position)
        heuristic = (evaluation + 1.0) / 2.0

    if is_white:
        return heuristic
    else:
        return 1.0 - heuristic


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

        # Roughly order the list to help with pruning.
        policies_list.sort(key=probability_distribution_sort, reverse=True)
        legal_moves = []
        for policy in policies_list:
            legal_moves.append(policy[0])

    return legal_moves


def probability_distribution_sort(entry):
    return entry[1]


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


# Quickly return the legal move with the highest policy value.
def get_best_legal_move(position):

    evaluation = strong_evaluator.get_full_evaluation_from_moves(position)
    legal_moves = evaluation.move_policy_list
    legal_moves.sort(key=probability_distribution_sort, reverse=True)

    return legal_moves[0][0]
