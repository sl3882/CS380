import sys
import random
from collections import deque
import time

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
            parts = content.split(",")  # Split content by commas
            self.width = int(parts[0])  # Set width from first part
            self.height = int(parts[1])  # Set height from second part
            self.board = [  # Create 2D list for board
                list(map(int, parts[i * self.width + 2:(i + 1) * self.width + 2]))
                for i in range(self.height)
            ]
        except Exception as e:  # Handle any exceptions
            print(f"Error loading game state : {e}")  # Print error message
            sys.exit(1)  # Exit the program with error code 1

    def clone_state(self):  # Method to create a deep copy of the board
        new_sbp = Sbp()
        new_sbp.width = self.width
        new_sbp.height = self.height
        new_sbp.board = [row[:] for row in self.board]
        return new_sbp

    def is_done(self):  # Method to check if the puzzle is solved
        return not any(-1 in row for row in self.board)  # Check if any -1 (empty space) remains

    def get_piece_cells(self, piece):  # Method to get coordinates of a piece
        cells = []  # Initialize empty list for cell coordinates
        for y in range(self.height):  # Iterate over rows
            for x in range(self.width):  # Iterate over columns
                if self.board[y][x] == piece:  # If cell matches the piece
                    cells.append((x, y))  # Add coordinates to cells list
        return cells  # Return list of coordinates

    def can_move(self, piece, direction):
        cells = self.get_piece_cells(piece)  # Get all (x, y) positions occupied by the piece
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        for x, y in cells:
            new_x, new_y = x + dx, y + dy  # Compute new position

            # Check if the move is within boundaries
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                return False  # Out of bounds

            target_cell = self.board[new_y][new_x]  # Check what's in the target cell

            # The piece can move into an empty cell (0)
            if target_cell == 0:
                continue

            # Only the master brick (2) can move into the goal (-1)
            if target_cell == -1 and piece != 2:
                return False  # Other pieces cannot move into the goal

            # If the target cell is another brick or boundary, prevent movement
            if target_cell not in [0, -1] and (new_x, new_y) not in cells:
                return False  # The move is blocked by another piece

        return True  # If all checks pass, the move is valid

    def available_moves(self):  # Method to get all available moves
        moves = []  # Initialize empty list for moves
        # Get pieces in sorted order for consistent move generation
        pieces = set(val for row in self.board for val in row if val >= 2)
        directions = ["up", "down", "left", "right"]  # List of possible directions

        for piece in pieces:  # Iterate over pieces
            for direction in directions:  # Iterate over directions
                if self.can_move(piece, direction):  # Check if move is valid
                    moves.append((piece, direction))  # Add valid move to list
        return moves  # Return list of available moves

    def apply_move(self, piece, direction):
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        # Clear old positions, ensuring goal cells remain
        for x, y in cells:
            self.board[y][x] = 0

        # Set new positions
        for x, y in cells:
            new_x, new_y = x + dx, y + dy
            self.board[new_y][new_x] = piece

        self.normalize()

    def print_board(self):  # Method to print the board
        print(f"{self.width},{self.height},")  # Print width and height
        for row in self.board:  # Iterate over rows
            print(",".join(map(str, row)) + ",")  # Print each row as comma-separated string

    def compare_states(self, other):  # Method to compare states
        if self.width != other.width or self.height != other.height:  # Check dimensions
            return False  # Return False if dimensions don't match
        for row1, row2 in zip(self.board, other.board):  # Iterate over rows
            if row1 != row2:  # Check if rows are different
                return False  # Return False if rows are different
        return True  # Return True if all rows are the same

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
            piece, direction = random.choice(moves)  # Choose a random move
            self.apply_move(piece, direction)  # Apply the move
            self.normalize()  # Normalize the board
            history.append(((piece, direction), self.clone_state()))  # Add move and board state to history
        return history  # Return move history

    def board_to_tuple(self):
        """Converts the board to a tuple of tuples for hashing."""
        return tuple(tuple(row) for row in self.board)

    def bfs(self, filename):
        start_time = time.time()
        self.load_board(filename)
        initial_state = self.clone_state()
        queue = deque([(self, [])])  # Queue of (state, moves)
        visited = {self.board_to_tuple()}  # Set of visited states
        nodes_explored = 0

        while queue:
            current_state, moves = queue.popleft()
            nodes_explored += 1

            if current_state.is_done():
                end_time = time.time()
                elapsed_time = end_time - start_time

                for move in moves:
                    print(move)

                current_state.print_board()
                print(nodes_explored)
                print(f"{elapsed_time:.2f}")
                print(len(moves))
                return

            for piece, direction in current_state.available_moves():
                new_state = current_state.clone_state()
                new_state.apply_move(piece, direction)
                new_state.normalize()
                new_board_tuple = new_state.board_to_tuple()

                if new_board_tuple not in visited:
                    visited.add(new_board_tuple)
                    queue.append((new_state, moves + [(piece, direction)]))

        print("No solution found")
        return

    def dfs(self, filename, depth_limit=20):
        """Performs a depth-first search to solve the puzzle."""
        start_time = time.time()
        self.load_board(filename)
        visited = {self.board_to_tuple()}
        nodes_explored = 0
        solution_moves = []
        solution_found = False

        def recursive_dfs(state, moves, depth):
            nonlocal nodes_explored, solution_moves, solution_found

            nodes_explored += 1

            if state.is_done():
                solution_found = True
                solution_moves = moves[:]  # Copy the moves
                return True

            if depth >= depth_limit:
                return False

            for piece, direction in state.available_moves():
                new_state = state.clone_state()
                new_state.apply_move(piece, direction)
                new_state.normalize()
                new_board_tuple = new_state.board_to_tuple()

                if new_board_tuple not in visited:
                    visited.add(new_board_tuple)
                    if recursive_dfs(new_state, moves + [(piece, direction)], depth + 1):
                        return True
                    visited.remove(new_board_tuple)  # Backtrack

            return False

        if recursive_dfs(self, [], 0):
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Convert moves to the requested format
            formatted_moves = [(move[0], move[1]) for move in solution_moves]
            for move in formatted_moves:
                print(move)

            self.print_board()
            print(nodes_explored)
            print(f"{elapsed_time:.2f}")
            print(len(solution_moves))

        else:
            print("No solution found within depth limit")
        return

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
        puzzle.apply_move(piece, direction)
        puzzle.print_board()
    elif command == "compare":
        if len(sys.argv) < 4:
            print("Usage: python3 sbp.py compare <filename1> <filename2>")
            sys.exit(1)
        filename2 = sys.argv[3]
        puzzle.load_board(filename)
        other_puzzle = Sbp()
        other_puzzle.load_board(filename2)
        print(puzzle.compare_states(other_puzzle))
    elif command == "norm":
        puzzle.load_board(filename)
        puzzle.normalize()
        puzzle.print_board()
    elif command == "random":
        if len(sys.argv) != 4:
            print("Usage: python3 sbp.py random <filename> <N>")
            sys.exit(1)
        puzzle.load_board(filename)
        N = int(sys.argv[3])
        puzzle.print_board()
        for (piece, direction), state in puzzle.random_walk(N):
            print(f"({piece}, {direction})")
            puzzle.board = state
            puzzle.print_board()
    elif command == "bfs":
        puzzle.bfs(filename)
    elif command == "dfs":
        puzzle.dfs(filename)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
