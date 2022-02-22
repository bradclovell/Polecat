import math
import backends


nn_evaluator = backends.strong_evaluator


def get_move(position):
    evaluation = nn_evaluator.get_evaluations_from_moves([position])[0]

    probability_distribution = evaluation.move_policy_list

    if len(probability_distribution) == 0:
        print("ERROR: Could not find move for Leela Weights.")
        exit(1)

    top_move = None
    top_move_value = -math.inf

    for entry in probability_distribution:
        if entry[1] > top_move_value:
            top_move = entry[0]
            top_move_value = entry[1]

    return top_move
