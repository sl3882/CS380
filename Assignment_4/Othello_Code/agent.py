import math
import random

import game

class HumanPlayer(game.Player):

    def __init__(self):
        super().__init__()

    def choose_move(self, state):
        # generate the list of moves:
        moves = state.generateMoves()

        for i, action in enumerate(moves):
            print('{}: {}'.format(i, action))
        response = input('Please choose a move: ')
        return moves[int(response)]

class RandomAgent(game.Player):
    def __init__(self):
        super().__init__()

    def choose_move(self, state):
        # generate the list of moves:
        moves = state.generateMoves()

        if moves:  # Check if the list is not empty
            return random.choice(moves)
        else:
            return None  # Or return a pass move.

class MinimaxAgent(game.Player):
    def __init__(self, depth):
        super().__init__()
        self.depth = depth

    def choose_move(self, state):
        # Generate the list of moves

        best_move = None
        best_value = float('-inf')

        moves = state.generateMoves()
        for move in moves:
            next_state = state.applyMoveCloning(move)
            value = self.minimax(next_state, self.depth - 1, False)
            if value > best_value:
                best_value = value
                best_move = move

        return best_move

    def minimax(self, state, depth, maximizing_player):

        if depth == 0 or state.game_over():
            return state.score()

        if maximizing_player:
            best_value = float('-inf')
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                best_value = max(best_value, self.minimax(next_state, depth - 1, False))
            return best_value
        else:
            best_value = float('inf')
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                best_value = min(best_value, self.minimax(next_state, depth - 1, True))
            return best_value

class AlphaBeta(game.Player):
    def __init__(self, depth):
        super().__init__()
        self.depth = depth

    def choose_move(self, state):
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in state.generateMoves():
            next_state = state.applyMoveCloning(move)
            value = self.alphabeta(next_state, self.depth - 1, False, alpha, beta)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
        return best_move

    def alphabeta(self, state, depth, maximizing_player, alpha, beta):
        if depth == 0 or state.game_over():
            return state.score()

        if maximizing_player:
            best_value = float('-inf')
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                best_value = max(best_value, self.alphabeta(next_state, depth - 1, False, alpha, beta))
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            return best_value
        else:
            best_value = float('inf')
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                best_value = min(best_value, self.alphabeta(next_state, depth - 1, True, alpha, beta))
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            return best_value

class sl3882(game.Player):
    def __init__(self, time_limit_ms):
        super().__init__()
        self.time_limit_ms = time_limit_ms

    def choose_move(self, state):
        start_time = time.time()
        time_limit_s = self.time_limit_ms / 1000.0
        best_move = None
        depth = 1

        while (time.time() - start_time) < time_limit_s:
            try:
                best_move = self.iterative_deepening_alphabeta(state, depth, start_time, time_limit_s)
                depth += 1
            except TimeoutError:
                break

        if best_move is None:
            moves = state.generateMoves()
            if moves:
                return random.choice(moves)
            else:
                return None

        return best_move

    def iterative_deepening_alphabeta(self, state, depth, start_time, time_limit_s):
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in state.generateMoves():
            if (time.time() - start_time) > time_limit_s:
                raise TimeoutError
            next_state = state.applyMoveCloning(move)
            value = self.alphabeta(next_state, depth - 1, False, alpha, beta, start_time, time_limit_s)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
        return best_move

    def alphabeta(self, state, depth, maximizing_player, alpha, beta, start_time, time_limit_s):
        if (time.time() - start_time) > time_limit_s:
            raise TimeoutError

        if depth == 0 or state.game_over():
            return self.evaluate(state)

        if maximizing_player:
            best_value = float('-inf')
            for move in state.generateMoves():
                if (time.time() - start_time) > time_limit_s:
                    raise TimeoutError
                next_state = state.applyMoveCloning(move)
                best_value = max(best_value,
                                 self.alphabeta(next_state, depth - 1, False, alpha, beta, start_time, time_limit_s))
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            return best_value
        else:
            best_value = float('inf')
            for move in state.generateMoves():
                if (time.time() - start_time) > time_limit_s:
                    raise TimeoutError
                next_state = state.applyMoveCloning(move)
                best_value = min(best_value,
                                 self.alphabeta(next_state, depth - 1, True, alpha, beta, start_time, time_limit_s))
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            return best_value

    def evaluate(self, state):
        # Improved evaluation function
        score = 0
        board_size = state.boardSize
        for i in range(board_size):
            for j in range(board_size):
                if state.board[i][j] == game.PLAYER1:
                    if (i == 0 or i == board_size - 1) and (j == 0 or j == board_size - 1):
                        score += 5  # Corner bonus
                    elif (i == 0 or i == board_size - 1) or (j == 0 or j == board_size - 1):
                        score += 2  # Edge bonus
                    else:
                        score += 1
                elif state.board[i][j] == game.PLAYER2:
                    if (i == 0 or i == board_size - 1) and (j == 0 or j == board_size - 1):
                        score -= 5
                    elif (i == 0 or i == board_size - 1) or (j == 0 or j == board_size - 1):
                        score -= 2
                    else:
                        score -= 1
        return score
