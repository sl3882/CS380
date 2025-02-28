import math
import random
import time

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
        self.time_limit = time_limit_ms / 1000  # Convert to seconds

    def choose_move(self, state):
        start_time = time.time()
        best_move = None
        best_value = float('-inf')
        depth = 1

        while time.time() - start_time < self.time_limit:
            moves = state.generateMoves()
            if not moves:
                return None  # No valid moves

            current_best_move = best_move
            for move in moves:
                next_state = state.applyMoveCloning(move)
                value = self.minimax(next_state, depth - 1, False, start_time)
                if value > best_value:
                    best_value = value
                    current_best_move = move

            if time.time() - start_time < self.time_limit:
                best_move = current_best_move
                depth += 1
            else:
                break

        return best_move

    def minimax(self, state, depth, maximizing_player, start_time):
        if depth == 0 or state.game_over() or time.time() - start_time >= self.time_limit:
            return state.score()

        if maximizing_player:
            best_value = float('-inf')
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                best_value = max(best_value, self.minimax(next_state, depth - 1, False, start_time))
            return best_value
        else:
            best_value = float('inf')
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                best_value = min(best_value, self.minimax(next_state, depth - 1, True, start_time))
            return best_value
