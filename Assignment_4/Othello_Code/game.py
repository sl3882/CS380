import othello
# import util
import  time

class Player:

    def choose_move(self, state):
        raise NotImplementedError


class Game:

    def __init__(self, initial_state, player1, player2):
        self.initial_state = initial_state
        self.players = [player1, player2]

    def play(self):
        start_time = time.time()  # Record the start time
        state = self.initial_state.clone()
        states = [state]
        player_index = 0
        while not state.game_over():
            # Display the current state in the console:
            print("\nCurrent state, " + othello.PLAYER_NAMES[state.nextPlayerToMove] + " to move:")
            print(state)
            # Get the move from the player:
            player = self.players[player_index]
            move = player.choose_move(state)
            if move != None: print(move)
            state = state.applyMoveCloning(move)
            states.append(state)
            # util.pprint(state)
            player_index = (player_index + 1) % len(self.players)
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        print("\n*** Final winner: " + state.winner() +" ***" )
        print(state)
        print(f"Game finished in {elapsed_time:.4f} seconds.")
        return states


