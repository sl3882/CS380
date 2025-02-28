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

import time
import math
import random
from othello import State, OthelloMove, PLAYER1, PLAYER2, EMPTY, OTHER_PLAYER

class sl3882:
    def __init__(self, time_limit_ms):
        """
        Initialize the agent with a time limit in milliseconds.
        """
        self.time_limit = time_limit_ms / 1000  # Convert to seconds
        self.start_time = None

    def choose_move(self, state):
        """
        Choose the best move within the given time limit using iterative deepening.
        """
        self.start_time = time.time()
        best_move = None
        depth = 1

        while time.time() - self.start_time < self.time_limit:
            current_best_move = None
            best_value = -math.inf

            # Generate all possible moves
            moves = state.generateMoves()
            if not moves:
                return None  # No valid moves

            # Evaluate each move at the current depth
            for move in moves:
                next_state = state.applyMoveCloning(move)
                value = self.minimax(next_state, depth - 1, False, -math.inf, math.inf)
                if value > best_value:
                    best_value = value
                    current_best_move = move

                # Check if time limit has been exceeded
                if time.time() - self.start_time >= self.time_limit:
                    break

            # Update the best move if the search completed within the time limit
            if time.time() - self.start_time < self.time_limit:
                best_move = current_best_move
                depth += 1
            else:
                break

        return best_move

    def minimax(self, state, depth, maximizing_player, alpha, beta):
        """
        Minimax algorithm with Alpha-Beta pruning.
        """
        # Check if the time limit has been exceeded
        if time.time() - self.start_time >= self.time_limit:
            return 0  # Return a neutral value if time is up

        # Check if the game is over or the depth limit is reached
        if depth == 0 or state.game_over():
            return self.evaluate(state)

        if maximizing_player:
            best_value = -math.inf
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                value = self.minimax(next_state, depth - 1, False, alpha, beta)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break  # Beta cut-off
            return best_value
        else:
            best_value = math.inf
            for move in state.generateMoves():
                next_state = state.applyMoveCloning(move)
                value = self.minimax(next_state, depth - 1, True, alpha, beta)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break  # Alpha cut-off
            return best_value

    def evaluate(self, state):
        """
        Evaluate the state using a heuristic function.
        This function can be customized to improve the agent's performance.
        """
        # Simple heuristic: count the number of pieces
        score = state.score()

        # Add additional heuristics (e.g., corner control, mobility)
        corners = [(0, 0), (0, state.boardSize - 1), (state.boardSize - 1, 0), (state.boardSize - 1, state.boardSize - 1)]
        for x, y in corners:
            if state.get(x, y) == PLAYER1:
                score += 10  # Bonus for controlling corners
            elif state.get(x, y) == PLAYER2:
                score -= 10

        return score