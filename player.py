import random
import chess
import chess.pgn
import expectimax
import stockfish_utility
import leela_weights_greedy
import maia_player_model
import stochastic_uct
import blunder_creator

# Program will play a game of chess with you.

# Options for the computer opponent are the following:
# "blunder creator", "maia player model", "stockfish", "leela weights", "expectimax", or "stochastic uct"
computer_engine = "blunder creator"

# Playing options.
simulate_player = False
suppress_game_text = False


def get_player_move(input_board):
    while True:
        if simulate_player:
            position = []
            for move in input_board.move_stack:
                position.append(move.uci())
            move_input = maia_player_model.get_move(position)
            if not suppress_game_text:
                print("Player move: " + move_input)
        else:
            move_input = input("Your move: ")

        if move_input == "Show":
            print(input_board)
            continue

        try:
            move_parsed = chess.Move.from_uci(move_input)
        except ValueError:
            print("Not a valid move.")
            continue

        if move_parsed in input_board.legal_moves:
            return move_parsed
        else:
            print("Not a legal move.")


def get_computer_move(input_board):
    position = []
    for move in input_board.move_stack:
        position.append(move.uci())

    # Select computer engine.
    if computer_engine == "maia player model":
        return maia_player_model.get_move(position)
    elif computer_engine == "blunder creator":
        return blunder_creator.get_best_move(position)
    elif computer_engine == "stockfish":
        return stockfish_utility.get_best_move(position)
    elif computer_engine == "leela weights":
        return leela_weights_greedy.get_move(position)
    elif computer_engine == "stochastic uct":
        return stochastic_uct.get_best_move(position, 2000, .01, .02)
    elif computer_engine == "expectimax":
        return expectimax.get_best_move(position, 4, .01, .01, .02)
    else:
        print("Computer engine is not specified.")
        exit(1)


def play_game():

    computer_plays_white = random.choice([True, False])

    if not suppress_game_text:
        if computer_plays_white:
            print("Let's have a game! I'll go first.")
        else:
            print("Let's have a game! You can go first.")
        print("Type a move in long algebraic notation to play, or type 'Show' to show the board!")

    board = chess.Board()

    if computer_plays_white:
        # Play first move.
        computer_move = get_computer_move(board)
        board.push(chess.Move.from_uci(computer_move))
        if not suppress_game_text:
            print(computer_move)

    while True:
        player_move = get_player_move(board)
        board.push(player_move)

        outcome = board.outcome(claim_draw=True)
        if outcome is not None:
            if not suppress_game_text:
                if outcome.result() == "1-0":
                    if computer_plays_white:
                        print("Checkmate.")
                    else:
                        print("You win, congratulations!")
                elif outcome.result() == "0-1":
                    if computer_plays_white:
                        print("You win, congratulations!")
                    else:
                        print("Checkmate.")
                else:
                    print("A draw!")
            break

        computer_move = get_computer_move(board)
        board.push(chess.Move.from_uci(computer_move))
        if not suppress_game_text:
            print(computer_move)

        outcome = board.outcome(claim_draw=True)
        if outcome is not None:
            if outcome.result() == "1-0":
                if not suppress_game_text:
                    print("You win, congratulations!")
            elif outcome.result() == "0-1":
                if not suppress_game_text:
                    print("Checkmate.")
            else:
                if not suppress_game_text:
                    print("A draw!")
            break

    if not suppress_game_text:
        print("Good game! Let's play again soon.")

    position = []
    for move in board.move_stack:
        position.append(move.uci())
    return position


def print_example_game():

    moves = play_game()

    pgn_game = chess.pgn.Game()

    node = pgn_game
    for chess_move in moves:
        node = node.add_variation(chess.Move.from_uci(chess_move))

    print(pgn_game)
    print("")
