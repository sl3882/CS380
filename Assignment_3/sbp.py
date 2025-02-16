import sys
from random import choice
import time
from collections import deque
import copy

class Sbp:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.board = []

    def load_board(self, filename):
        try:
            with open(filename, 'r') as file:
                content = file.read().strip()
            # Parse width, height, and board
            parts = content.split(",")
            self.width = int(parts[0])
            self.height = int(parts[1])
            self.board = [
                list(map(int, parts[i * self.width + 2:(i + 1) * self.width + 2]))
                for i in range(self.height)
            ]
        except Exception as e:
            print(f"Error loading game state: {e}")
            sys.exit(1)

    # def clone_state(self):
    #     return [row[:] for row in self.board]
    def clone_state(self):
        return copy.deepcopy(self.board)
    def is_done(self):
        return not any(-1 in row for row in self.board)

    def print_board(self):
        print(f"{self.width},{self.height},")
        for row in self.board:
            print(",".join(map(str, row)) + ",")

    def get_piece_positions(self):
        """Returns a dictionary mapping piece IDs to their positions on the board."""
        pieces = {}
        for r in range(self.height):
            for c in range(self.width):
                piece = self.board[r][c]
                if piece > 0:  # Ignore empty cells and walls
                    if piece not in pieces:
                        pieces[piece] = []
                    pieces[piece].append((r, c))
        return pieces

    def available_moves(self):
        """Returns a list of all available moves as (piece, direction)."""
        moves = []
        piece_positions = self.get_piece_positions()

        for piece, positions in piece_positions.items():
            min_r = min(r for r, _ in positions)
            max_r = max(r for r, _ in positions)
            min_c = min(c for _, c in positions)
            max_c = max(c for _, c in positions)

            # Check movement in all four directions
            if min_r > 0 and all(self.board[r - 1][c] == 0 for r, c in positions):  # Up
                moves.append((piece, "up"))
            if max_r < self.height - 1 and all(self.board[r + 1][c] == 0 for r, c in positions):  # Down
                moves.append((piece, "down"))
            if min_c > 0 and all(self.board[r][c - 1] == 0 for r, c in positions):  # Left
                moves.append((piece, "left"))
            if max_c < self.width - 1 and all(self.board[r][c + 1] == 0 for r, c in positions):  # Right
                moves.append((piece, "right"))

        return moves

    def apply_move(self, piece, direction):
        """Applies the given move to the board if it is available."""
        if (piece, direction) not in self.available_moves():
            return  # Do nothing if the move is not available

        directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        dx, dy = directions[direction]
        piece_positions = self.get_piece_positions()[piece]

        # Move the piece
        new_positions = [(r + dx, c + dy) for r, c in piece_positions]
        for r, c in piece_positions:
            self.board[r][c] = 0
        for r, c in new_positions:
            self.board[r][c] = piece

    def apply_move_and_return_new_state(self, piece, direction):
        """Returns a new state resulting from applying the move."""
        new_state = Sbp()
        new_state.width = self.width
        new_state.height = self.height
        new_state.board = self.clone_state()
        new_state.apply_move(piece, direction)
        return new_state

    def compare_board(self, other_board):  # Method to compare this board with another
        if len(self.board) != len(other_board) or len(self.board[0]) != len(
                other_board[0]):  # Check if dimensions match
            return False  # Return False if dimensions don't match
        return all(self.board[i][j] == other_board[i][j]  # Compare all cells
                   for i in range(len(self.board))
                   for j in range(len(self.board[0])))

    def normalize(self):  # Method to normalize the board
        next_idx = 3  # Start with index 3 (1 and 2 are reserved)
        for y in range(self.height):  # Iterate over rows
            for x in range(self.width):  # Iterate over columns
                if self.board[y][x] == next_idx:  # If cell matches next index
                    next_idx += 1  # Increment next index
                elif self.board[y][x] > next_idx:  # If cell is higher than next index
                    # Swap indices
                    old_idx = self.board[y][x]  # Store old index
                    for i in range(self.height):  # Iterate over rows
                        for j in range(self.width):  # Iterate over columns
                            if self.board[i][j] == next_idx:  # If cell matches next index
                                self.board[i][j] = old_idx  # Set to old index
                            elif self.board[i][j] == old_idx:  # If cell matches old index
                                self.board[i][j] = next_idx  # Set to next index
                    next_idx += 1  # Increment next index

    def random_walk(self, N):  # Method to perform a random walk
        history = []  # Initialize empty list for move history
        for _ in range(N):  # Repeat N times
            moves = self.available_moves()  # Get available moves
            if not moves or self.is_done():  # If no moves or puzzle is solved
                break  # Exit loop
            piece, direction = choice(moves)  # Choose a random move
            self.apply_move(piece, direction)  # Apply the move
            self.normalize()  # Normalize the board
            history.append(((piece, direction), self.clone_state()))  # Add move and board state to history
        return history  # Return move history

    def bfs(self):
        start_time = time.time()
        initial_state = self.clone_state()
        queue = deque([([], initial_state)])
        visited = [initial_state]
        nodes_explored = 1

        while queue:
            moves_list, current_state = queue.popleft()
            nodes_explored += 1

            temp_puzzle = Sbp()
            temp_puzzle.width = self.width
            temp_puzzle.height = self.height
            temp_puzzle.board = current_state

            if temp_puzzle.is_done():
                nodes_explored += 1
                end_time = time.time()
                # Print the moves
                for piece, direction in moves_list:
                    print(f"({piece},{direction})")
                print()

                temp_puzzle.print_board()
                print()
                # Print statistics
                print(nodes_explored)
                print(f"{end_time - start_time:.2f}")
                print(len(moves_list))
                return True

            # Try each possible move
            for piece, direction in temp_puzzle.available_moves():
                # Create new puzzle state
                new_puzzle = Sbp()
                new_puzzle.width = self.width
                new_puzzle.height = self.height
                new_puzzle.board = [row[:] for row in current_state]

                # Apply the move
                new_puzzle.apply_move(piece, direction)
                new_puzzle.normalize()

                # Check if we've seen this state before
                is_new_state = True
                for visited_state in visited:
                    if new_puzzle.compare_board(visited_state):
                        is_new_state = False
                        break

                if is_new_state:
                    visited.append(new_puzzle.board)
                    new_moves = moves_list + [(piece, direction)]
                    queue.append((new_moves, new_puzzle.board))

        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 sbp.py <command> <filename> [args]")
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]
    puzzle = Sbp()

    if command == "print":
        puzzle.load_board(filename)
        puzzle.print_board()
    elif command == "done":
        puzzle.load_board(filename)
        print(puzzle.is_done())
    elif command == "availableMoves":
        puzzle.load_board(filename)
        moves = puzzle.available_moves()
        for move in moves:
            print(f"({move[0]}, {move[1]})")
    elif command == "applyMove":
        if len(sys.argv) < 4:
            print("Usage: python3 sbp.py applyMove <filename> <move>")
            sys.exit(1)
        move = sys.argv[3].strip("()").split(",")
        piece = int(move[0])
        direction = move[1]
        puzzle.load_board(filename)
        new_state = puzzle.apply_move_and_return_new_state(piece, direction)
        new_state.print_board()
    elif command == "compare":  # If command is "compare"
        if len(sys.argv) != 4:  # Check if correct number of arguments
            print("Usage: python3 sbp.py compare <filename1> <filename2>")  # Print usage instructions
            sys.exit(1)  # Exit with error code 1
        puzzle2 = Sbp()  # Create second Sbp instance
        puzzle.load_board(filename)  # Load first board
        puzzle2.load_board(sys.argv[3])  # Load second board
        print(puzzle.compare_board(puzzle2.board))  # Print comparison result
    elif command == "norm":
        puzzle.load_board(filename)
        puzzle.normalize()
        puzzle.print_board()
    elif command == "random":  # If command is "random"
        if len(sys.argv) != 4:  # Check if correct number of arguments
            print("Usage: python3 sbp.py random <filename> <N>")  # Print usage instructions
            sys.exit(1)  # Exit with error code 1
        puzzle.load_board(filename)  # Load board from file
        N = int(sys.argv[3])  # Get number of random moves
        puzzle.print_board()  # Print initial board
        for (piece, direction), state in puzzle.random_walk(N):  # Perform random walk
            print(f"({piece}, {direction})")  # Print each move
            puzzle.board = state  # Update board state
            puzzle.print_board()  # Print updated board

    elif command == "bfs":
        puzzle.load_board(filename)
        puzzle.normalize()
        puzzle.bfs()

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
