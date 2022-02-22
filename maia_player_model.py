import random
import backends


player_model_evaluator = backends.player_model_evaluator


def get_move(position):
    evaluation = player_model_evaluator.get_evaluations_from_moves([position])[0]

    probability_distribution = evaluation.move_policy_list

    if len(probability_distribution) == 0:
        print("ERROR: Could not find move for Maia Player.")
        exit(1)

    roll = random.random()

    for entry in probability_distribution:
        if roll <= entry[1]:
            return entry[0]
        else:
            roll -= entry[1]

    return probability_distribution[0][0]
