import config
import player

# Performs a number of trials, comparing the blunder_creator version of Polecat against Stockfish.
# Outputs average number of half-moves per game for each engine.

trials = config.NUMBER_OF_TRIALS

total_bc_half_moves = 0
total_sf_half_moves = 0

print("Running trials...")

player.simulate_player = True
player.suppress_game_text = True

for i in range(trials):
    played_game = player.play_game()
    total_bc_half_moves += len(played_game)

player.computer_is_blunder_creator = False
player.computer_is_stockfish = True

for i in range(trials):
    played_game = player.play_game()
    total_sf_half_moves += len(played_game)

print("Completed " + str(trials) + " trials.")
print("")
print("  Polecat average half-moves: " + str(total_bc_half_moves / trials))
print("Stockfish average half-moves: " + str(total_sf_half_moves / trials))
