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
        return [row[:] for row in self.board]  # Return a new list of new lists

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
        pieces = set(val for row in self.board for val in row if val >= 2)  # Get set of all pieces
        directions = ["up", "down", "left", "right"]  # List of possible directions

        for piece in pieces:  # Iterate over pieces
            for direction in directions:  # Iterate over directions
                if self.can_move(piece, direction):  # Check if move is valid
                    moves.append((piece, direction))  # Add valid move to list
        return moves  # Return list of available moves

    def apply_move(self, piece, direction):
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        # Store original board state to preserve goal cells
        old_positions = {(x, y): self.board[y][x] for x, y in cells}

        # Clear old positions, ensuring goal cells remain
        for x, y in cells:
            if old_positions[(x, y)] == -1:
                continue  # Keep goal cell unchanged
            self.board[y][x] = 0

        # Set new positions
        for x, y in cells:
            self.board[y + dy][x + dx] = piece

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
    def dfs(self):
        start_time = time.time()
        initial_state = self.clone_state()
        stack = [([], initial_state)]
        visited = [initial_state]
        nodes_explored = 1

        while stack:
            moves_list, current_state = stack.pop()
            nodes_explored += 1

            temp_puzzle = Sbp()
            temp_puzzle.width = self.width
            temp_puzzle.height = self.height
            temp_puzzle.board = current_state

            if temp_puzzle.is_done():
                end_time = time.time()
                for piece, direction in moves_list:
                    print(f"({piece},{direction})")
                print()
                temp_puzzle.print_board()
                print()
                print(nodes_explored)
                print(f"{end_time - start_time:.2f}")
                print(len(moves_list))
                return True

            # Modified available_moves to ensure consistent ordering
            available = []
            pieces = list(set(val for row in temp_puzzle.board for val in row if val >= 2))
            pieces.sort(reverse=True)  # Sort in descending order to prioritize larger pieces
            directions = ["left", "right", "up", "down"]

            for piece in pieces:
                for direction in directions:
                    if temp_puzzle.can_move(piece, direction):
                        available.append((piece, direction))

            for piece, direction in available:
                new_puzzle = Sbp()
                new_puzzle.width = self.width
                new_puzzle.height = self.height
                new_puzzle.board = temp_puzzle.clone_state()
                new_puzzle.apply_move(piece, direction)
                new_puzzle.normalize()

                if not any(new_puzzle.compare_board(state) for state in visited):
                    visited.append(new_puzzle.board)
                    new_moves = moves_list + [(piece, direction)]
                    stack.append((new_moves, new_puzzle.board))

        return False

    def ids(self):
        start_time = time.time()
        initial_state = self.clone_state()
        depth = 0
        nodes_explored = 0

        while True:
            result, moves_list, nodes = self.dls(initial_state, depth)
            nodes_explored += nodes
            if result:
                end_time = time.time()
                for piece, direction in moves_list:
                    print(f"({piece},{direction})")
                print()
                self.board = initial_state
                for piece, direction in moves_list:
                    self.apply_move(piece, direction)
                self.print_board()
                print()
                print(nodes_explored)
                print(f"{end_time - start_time:.2f}")
                print(len(moves_list))
                return True
            depth += 1

    def dls(self, state, limit):
        stack = [([], state)]
        nodes_explored = 0

        while stack:
            moves_list, current_state = stack.pop()
            nodes_explored += 1

            temp_puzzle = Sbp()
            temp_puzzle.width = self.width
            temp_puzzle.height = self.height
            temp_puzzle.board = current_state

            if temp_puzzle.is_done():
                return True, moves_list, nodes_explored

            if len(moves_list) < limit:
                for piece, direction in temp_puzzle.available_moves():
                    new_puzzle = Sbp()
                    new_puzzle.width = self.width
                    new_puzzle.height = self.height
                    new_puzzle.board = temp_puzzle.clone_state()
                    new_puzzle.apply_move(piece, direction)
                    new_puzzle.normalize()

                    new_moves = moves_list + [(piece, direction)]
                    stack.append((new_moves, new_puzzle.board))

        return False, [], nodes_explored

    def print_board(self):  # Method to print the board
        print(f"{self.width},{self.height},")  # Print width and height
        for row in self.board:  # Iterate over rows
            print(",".join(map(str, row)) + ",")  # Print each row as comma-separated values

def main():  # Main function
    if len(sys.argv) < 3:  # Check if enough command-line arguments are provided
        print("Usage: python3 sbp.py <command> <filename> [args]")  # Print usage instructions
        sys.exit(1)  # Exit with error code 1

    command = sys.argv[1]  # Get command from command-line arguments
    filename = sys.argv[2]  # Get filename from command-line arguments
    puzzle = Sbp()  # Create Sbp instance

    if command == "print":  # If command is "print"
        puzzle.load_board(filename)  # Load board from file
        puzzle.print_board()  # Print the board

    elif command == "done":  # If command is "done"
        puzzle.load_board(filename)  # Load board from file
        print(puzzle.is_done())  # Print whether puzzle is solved

    elif command == "availableMoves":  # If command is "availableMoves"
        puzzle.load_board(filename)  # Load board from file
        for move in puzzle.available_moves():  # Iterate over available moves
            print(f"({move[0]}, {move[1]})")  # Print each move

    elif command == "applyMove":  # If command is "applyMove"
        if len(sys.argv) != 4:  # Check if correct number of arguments
            print("Usage: python3 sbp.py applyMove <filename> <move>")  # Print usage instructions
            sys.exit(1)  # Exit with error code 1
        puzzle.load_board(filename)  # Load board from file
        move = sys.argv[3].strip("()")  # Get move from command-line arguments
        piece, direction = move.split(",")  # Split move into piece and direction
        puzzle.apply_move(int(piece), direction.strip())  # Apply the move
        puzzle.print_board()  # Print the updated board

    elif command == "compare":  # If command is "compare"
        if len(sys.argv) != 4:  # Check if correct number of arguments
            print("Usage: python3 sbp.py compare <filename1> <filename2>")  # Print usage instructions
            sys.exit(1)  # Exit with error code 1
        puzzle2 = Sbp()  # Create second Sbp instance
        puzzle.load_board(filename)  # Load first board
        puzzle2.load_board(sys.argv[3])  # Load second board
        print(puzzle.compare_board(puzzle2.board))  # Print comparison result

    elif command == "norm":  # If command is "norm"
        puzzle.load_board(filename)  # Load board from file
        puzzle.normalize()  # Normalize the board
        puzzle.print_board()  # Print the normalized board

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
    elif command == "dfs":
        puzzle.load_board(filename)
        puzzle.normalize()
        puzzle.dfs()

    elif command == "ids":
        puzzle.load_board(filename)
        puzzle.normalize()
        puzzle.ids()


    else:  # If command is unknown
        print(f"Unknown command: {command}")  # Print error message

if __name__ == "__main__":  # If script is run directly
    main()  # Call main function
