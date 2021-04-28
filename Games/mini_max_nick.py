import random
import math
import numpy as np


def flip_player(player):
    if player == 'x':
        return 'o'
    else:
        return 'x'


def actions(board):
    options = []
    for col in range(0, len(board[0])):
        if board[0][col] == ' ':
            options.append(col)
    return options


def random_order_actions(board):
    options = actions(board)
    random.shuffle(options)
    return options


def agent_random(board, player='x'):
    options = actions(board)
    if len(options) == 0:
        return None
    return random.choice(options)


# Environment methods
def place_piece(board, col, player='x'):
    """Place the player piece in the col on the board"""
    if board[0][col] != ' ':
        return False

    next_open_row = len(board) - 1  # if the col is empty use the bottom row
    for row in range(0, len(board)):
        if board[row][col] != ' ':
            next_open_row = row - 1
            break

    board[next_open_row][col] = player


def result(board, player, action):
    board_copy = board.copy()
    place_piece(board_copy, action, player)
    return board_copy


# TODO: Optimize this
def check_series_for_winner(series):
    """Check if this line (could be anywhere)
    has 4 in a row"""
    count = 0
    prev = ' '
    for current_space in series:
        if current_space != ' ' and current_space == prev:
            count += 1
        elif current_space != ' ' and current_space != prev:
            count = 1
            prev = current_space
        elif current_space == ' ':
            prev = ' '
            count = 0

        if count == 4:
            return prev


def get_all_series(board):
    """Get all of the rows/cols/diags that could be winning streaks"""
    num_cols = len(board[0])
    num_rows = len(board)

    runs = []
    for row in range(0, num_rows):
        runs.append(board[row])
    for col in range(0, num_cols):
        runs.append(board[:, col])

    for offset in range(1 - num_rows, num_cols):
        runs.append(np.diagonal(board, offset=offset))
        runs.append(np.diagonal(np.fliplr(board), offset=offset))
    # get all diags
    max_row_cols = max(num_rows, num_cols)

    return runs


def terminal(board):
    """Determine if a player has won"""
    num_cols = len(board[0])
    num_rows = len(board)
    if len(actions(board)) == 0:
        return 'c'

    series = get_all_series(board)
    for s in series:
        winner = check_series_for_winner(s)
        if winner is not None:
            return winner
    return ' '


def utility(board, player='x'):
    """check is a state a terminal state, return the utility if it is.
    None means not terminal"""

    winner = terminal(board)
    if winner == player:
        return +1
    if winner == flip_player(player):
        return -1
    if winner == 'c':
        return 0
    return None


def play_list_plays(moves, board, starting_player='x'):
    for move in moves:
        place_piece(board=board, player=starting_player, col=move)
        starting_player = flip_player(starting_player)


def actions_middle_first(board):
    """Return the option of moves in the order starting with the middle"""
    moves = actions(board) # the moves in order
    num_cols = board.shape[1]
    new_order = []
    if board[0][num_cols//2] == ' ':
        new_order.append(num_cols//2)
    for i in range(1, num_cols//2+1):
        idx = (num_cols//2) + i
        if idx < num_cols and board[0][idx] == ' ':
            new_order.append(idx)
        idx = (num_cols//2) - i
        if idx >= 0 and board[0][idx] == ' ':
            new_order.append(idx)
    return new_order


def basic_heuristic(board, player='x'):
    series = get_all_series(board)
    util = utility(board, player)
    if util is not None: return util * 100, True

    util = 0
    for s in series:
        as_string = ""
        as_string = as_string.join(s)
        # points for xxx

        idx = as_string.find(player * 3)
        while idx >= 0:
            if idx - 1 >= 0 and as_string[idx - 1] == ' ':
                util += 3
            if idx >= 0 and idx + 3 < len(as_string) and as_string[idx + 3] == ' ':
                util += 3
            idx = as_string.find(player * 3, idx + 3)

        # points for xx
        idx = as_string.find(player * 2)
        while idx >= 0:
            if idx - 1 >= 0 and as_string[idx - 1] == player:
                idx = as_string.find(player * 2, idx + 2)
                continue
            if idx + 2 < len(as_string) and as_string[idx + 2] == player:
                idx = as_string.find(player * 2, idx + 2)
                continue
            if idx - 1 >= 0 and as_string[idx - 1] == ' ':
                util += 2
            if idx > 0 and idx + 2 < len(as_string) and as_string[idx + 2] == ' ':
                util += 2
            idx = as_string.find(player * 2, idx + 2)
    return util, False


def basic_heuristic(board, player='x'):
    series = get_all_series(board)
    util = utility(board, player)
    if util is not None: return util * 100, True

    util = 0
    for s in series:
        as_string = ""
        as_string = as_string.join(s)
        # points for xxx

        idx = as_string.find(player * 3)
        while idx >= 0:
            if idx - 1 >= 0 and as_string[idx - 1] == ' ':
                util += 3
            if idx >= 0 and idx + 3 < len(as_string) and as_string[idx + 3] == ' ':
                util += 3
            idx = as_string.find(player * 3, idx + 3)

        # points for xx
        idx = as_string.find(player * 2)
        while idx >= 0:
            if idx - 1 >= 0 and as_string[idx - 1] == player:
                idx = as_string.find(player * 2, idx + 2)
                continue
            if idx + 2 < len(as_string) and as_string[idx + 2] == player:
                idx = as_string.find(player * 2, idx + 2)
                continue
            if idx - 1 >= 0 and as_string[idx - 1] == ' ':
                util += 2
            if idx > 0 and idx + 2 < len(as_string) and as_string[idx + 2] == ' ':
                util += 2
            idx = as_string.find(player * 2, idx + 2)
    return util, False


def alpha_beta_search_cutoff(board, cutoff=None, fp=None, player='x', H=basic_heuristic):

    value, move = max_value_ab_cutoff(board, player, -math.inf, +math.inf, 0, cutoff, fp, H)

    return value, move


def max_value_ab_cutoff(state, player, alpha, beta, depth, cutoff, fp, H):
    """Player's best move"""

    # cut off and terminal test
    v, terminal = H(state, player)
    oppo, terminal = H(state, flip_player(player))
    diff = v - oppo

    # difference here we will stop evaulating if pass the fp value of H
    if (cutoff is not None and depth >= cutoff) or \
            (fp is not None and diff < -fp) or terminal:
        if (terminal): alpha, beta = v, v
        return v, None

    v, move = -math.inf, None

    # check all possible actions in the state, update alpha and return move with the largest value
    possibles = actions_middle_first(state)
    for a in possibles:
        v2, a2 = min_value_ab_cutoff(result(state, player, a),
                                     player,
                                     alpha,
                                     beta,
                                     depth + 1,
                                     cutoff,
                                     fp,
                                     H)
        if v2 > v:
            v, move = v2, a
            alpha = max(alpha, v)
        if v >= beta: return v, move
    return v, move


def min_value_ab_cutoff(state, player, alpha, beta, depth, cutoff, fp, H):
    """opponent's best response."""

    # cut off and terminal test
    v, terminal = H(state, player)
    # if((cutoff is not None and depth >= cutoff) or terminal):
    # always let the opponent make her move
    if (terminal):
        alpha, beta = v, v
        return v, None

    v, move = +math.inf, None

    # check all possible actions in the state, update beta and return move with the smallest value
    for a in actions_middle_first(state):
        v2, a2 = max_value_ab_cutoff(result(state, flip_player(player), a),
                                     player,
                                     alpha,
                                     beta,
                                     depth + 1,
                                     cutoff,
                                     fp,
                                     H)
        if v2 < v:
            v, move = v2, a
            beta = min(beta, v)
        if v <= alpha: return v, move

    return v, move


class ABAgent:
    """Class used to make agents easily"""

    def __init__(self, H=basic_heuristic, cutoff=None, fp=None):
        self.H = H
        self.cutoff = cutoff
        self.fp = fp

    def act(self, board, player):
        v, move = alpha_beta_search_cutoff(board,
                                           cutoff=self.cutoff,
                                           fp=self.fp,
                                           player=player,
                                           H=self.H)
        return move

    def __str__(self):
        return f"(AB Agent cutoff: {self.cutoff} forward Pruning: {self.fp})"

