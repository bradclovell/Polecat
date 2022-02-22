from lczero.backends import Weights, Backend, GameState, Output


class NeuralNetworkEvaluator:
    def __init__(self, path_to_weights):
        self.weights = Weights(path_to_weights)
        self.backend = Backend(self.weights)

    def get_full_evaluation_from_fen(self, fen_string):
        game_state = GameState(fen=fen_string)
        network_input = game_state.as_input(self.backend)
        output = self.backend.evaluate(network_input)
        position_evaluation = PositionEvaluation(game_state, output)
        return position_evaluation

    def get_full_evaluation_from_moves(self, input_moves):
        game_state = GameState(moves=input_moves)
        network_input = game_state.as_input(self.backend)
        output = self.backend.evaluate(network_input)
        position_evaluation = PositionEvaluation(game_state, output[0])
        return position_evaluation

    def get_full_evaluation_from_both(self, fen_string="", input_moves=None):
        if input_moves is None:
            input_moves = []

        game_state = GameState(fen=fen_string, moves=input_moves)
        network_input = game_state.as_input(self.backend)
        output = self.backend.evaluate(network_input)
        position_evaluation = PositionEvaluation(game_state, output)
        return position_evaluation

    def get_expected_outcome_from_fen(self, fen_string):
        game_state = GameState(fen=fen_string)
        network_input = game_state.as_input(self.backend)
        output = self.backend.evaluate(network_input)
        expected_outcome = output[0].q()
        return expected_outcome

    def get_expected_outcome_from_moves(self, input_moves, objective_evaluation=True):
        white_to_move = len(input_moves) % 2 == 0
        game_state = GameState(moves=input_moves)
        network_input = game_state.as_input(self.backend)
        output = self.backend.evaluate(network_input)
        expected_outcome = output[0].q()

        if not objective_evaluation:
            return expected_outcome
        else:
            if white_to_move:
                return expected_outcome
            else:
                return -expected_outcome

    def get_evaluations_from_moves(self, input_moves_list):
        nn_inputs = []
        game_states = []
        for move_list in input_moves_list:
            g = GameState(moves=move_list)
            game_states.append(g)
            i = g.as_input(self.backend)
            nn_inputs.append(i)

        nn_outputs = self.backend.evaluate(*nn_inputs)

        position_evaluations = []
        for index in range(len(nn_outputs)):
            evaluation = PositionEvaluation(game_states[index], nn_outputs[index])
            position_evaluations.append(evaluation)

        return position_evaluations

    def get_expected_outcomes_from_moves(self, input_moves_list, objective_evaluation=True):
        nn_inputs = []
        game_states = []
        for move_list in input_moves_list:
            g = GameState(moves=move_list)
            game_states.append(g)
            i = g.as_input(self.backend)
            nn_inputs.append(i)

        nn_outputs = self.backend.evaluate(*nn_inputs)

        position_evaluations = []
        for index in range(len(nn_outputs)):
            evaluation = PositionEvaluation(game_states[index], nn_outputs[index])
            position_evaluations.append(evaluation)

        outcomes_list = []

        for index in range(len(position_evaluations)):
            white_to_move = len(input_moves_list[index]) % 2 == 0
            if not objective_evaluation:
                outcomes_list.append(position_evaluations[index].expected_outcome)
            else:
                if white_to_move:
                    outcomes_list.append(position_evaluations[index].expected_outcome)
                else:
                    outcomes_list.append(-position_evaluations[index].expected_outcome)

        return outcomes_list


class PositionEvaluation:
    def __init__(self, game_state, output):
        self.expected_outcome = output.q()
        moves = game_state.moves()
        policies = output.p_softmax(*game_state.policy_indices())
        self.move_policy_list = list(zip(moves, policies))
