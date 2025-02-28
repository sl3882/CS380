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
        return random.choice(moves)

class MinimaxAgent(game.Player):
    def __init__(self, depth):
        super().__init__()
        self.depth = depth

    def choose_move(self, state):
        # Generate the list of moves
        moves = state.generateMoves()

        # If no moves are available, return None (pass)
        if not moves:
            return None

        # Initialize variables to keep track of the best move
        best_move = None
        best_value = float('-inf')

        # Current player
        player = state.nextPlayerToMove

        # Evaluate each move using minimax
        for move in moves:
            # Apply the move to get the next state
            next_state = state.applyMoveCloning(move)

            # Get the value of this move using minimax
            value = self.minimax(next_state, self.depth - 1, False, player)

            # Update the best move if this one is better
            if value > best_value:
                best_value = value
                best_move = move

        return best_move

    def minimax(self, state, depth, is_maximizing, original_player):
        # If we've reached the terminal depth or the game is over, evaluate the state
        if depth == 0 or state.game_over():
            # Get the score from the perspective of the original player
            score = state.score()
            # Adjust score based on who the original player is (PLAYER1 wants positive, PLAYER2 wants negative)
            return score if original_player == state.PLAYER1 else -score

        # Generate possible moves
        moves = state.generateMoves()

        # If no moves are available, pass and continue with the other player
        if not moves:
            # Create a new state with the next player to move
            next_state = state.clone()
            next_state.nextPlayerToMove = state.OTHER_PLAYER[next_state.nextPlayerToMove]
            return self.minimax(next_state, depth, not is_maximizing, original_player)

        if is_maximizing:
            # If maximizing, find the move with the highest value
            max_value = float('-inf')
            for move in moves:
                next_state = state.applyMoveCloning(move)
                value = self.minimax(next_state, depth - 1, False, original_player)
                max_value = max(max_value, value)
            return max_value
        else:
            # If minimizing, find the move with the lowest value
            min_value = float('inf')
            for move in moves:
                next_state = state.applyMoveCloning(move)
                value = self.minimax(next_state, depth - 1, True, original_player)
                min_value = min(min_value, value)
            return min_value
#
#
# class AlphaBeta(game.Player):
#     pass