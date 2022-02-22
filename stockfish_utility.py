import config
from stockfish import Stockfish


strong_stockfish = Stockfish(path=config.PATH_TO_STOCKFISH, depth=12)
weak_stockfish = Stockfish(path=config.PATH_TO_STOCKFISH, depth=12)


def get_best_move(position):
    strong_stockfish.set_position(position)
    return strong_stockfish.get_best_move()


def get_value_at_position(position):
    # Returns objective evaluation (from white's perspective)
    playing_as_white = len(position) % 2 == 0

    weak_stockfish.set_position(position)

    wdl = weak_stockfish.get_wdl_stats()

    if not playing_as_white:
        wdl.reverse()

    position_value = 0

    wdl_total = wdl[0] + wdl[1] + wdl[2]
    position_value += wdl[0] / wdl_total
    position_value += (wdl[1] / 2.0) / wdl_total

    return position_value
