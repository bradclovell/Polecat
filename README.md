# Polecat ?! : A Chess Engine for Playing against Humans

Polecat is a chess engine, written in the Python programming language, that specializes in defeating human opponents by predicting their behavior and attempting to provoke mistakes and gain rapid advantages. After achieving an overwhelming advantage, Polecat defers to Stockfish engine recommendations to finish the game.

## Effectiveness

Qualitatively, Polecat is very fun to play against. Its games are exciting and feature lots of risky play, daring sacrifices, and positional gambits.

After running an experiment in which I had Polecat and Stockfish (a top chess engine) play 1,000 games each against a model of a human player with a skill rating of 1700 on [Lichess](https://lichess.org/), I found that Stockfish checkmates the opponent in 53.548 half-moves on average, and that Polecat, in its current form, checkmates its opponent in an average of only 51.604 half-moves. **This demonstrates that Polecat succeeds at playing better than Stockfish when facing a human.**

This experiment can be replicated by installing the project and running trial.py.

For annotated example games of Polecat playing against a [Maia Chess](https://maiachess.com/)-powered simulation of a human player, and against a real human player, you can examine this [Lichess Study](https://lichess.org/study/Q2eYjFDD).

## Installation

Polecat runs on Windows and can be installed by cloning this git repository or by downloading the [project .zip file](https://github.com/bradclovell/Polecat/archive/refs/heads/main.zip) from GitHub. Polecat requires Python 3.7 or later and was created and tested using Python 3.8. This project requires the two Python packages listed in requirements.txt: [chess](https://pypi.org/project/chess/) and [stockfish](https://pypi.org/project/stockfish/). Polecat includes both CPU and GPU backends for neural network evaluation. The OpenCL backend should work with both Nvidia and AMD graphics cards, but was only tested on an Nvidia card.

## Using Polecat

To use Polecat, use Python to run either play_engine.py to play a game against Polecat or trial.py to replicate the experiment I describe above.

This project includes the [Maia Chess](https://maiachess.com/) project's neural network files corresponding to ratings of 1100 to 1900 on [Lichess](https://lichess.org/). For the best results, config.py should be edited to point to the Maia model nearest the user's own rating. This makes sure that Polecat uses the most appropriate Maia neural network to predict its opponent's behavior.

For example, if your [Lichess](https://lichess.org/) rating is near 1500, you should change:
```
PATH_TO_PLAYER_MODEL_WEIGHTS_FILE = "./Neural Net Weights Files/maia-1700.pb.gz"
```
to instead read:
```
PATH_TO_PLAYER_MODEL_WEIGHTS_FILE = "./Neural Net Weights Files/maia-1500.pb.gz"
```

You can also edit config.py to change the number of trials run by trial.py, the neural network file used for evaluation, and the path to an installation of the Stockfish engine.

## Use of External Resources

This project uses resources from the [Maia Chess](https://maiachess.com/) project to model human behavior, as well as technology from the [Leela Chess Zero](https://lczero.org/) engine to evaluate neural networks trained by Maia and by Leela Chess Zero project contributors. This project also includes a distribution of the [Stockfish](https://stockfishchess.org/) engine for move recommendation and as a basis of comparison in testing Polecat's effectiveness.

## Technical Implementation

The source code includes several different methods of generating moves, including Stochastic UCT and Expectimax Tree Search with bounded Alpha-pruning, but the method Polecat currently uses is a shallow Expectimax Tree Search with pruning determined by neural network predictors.