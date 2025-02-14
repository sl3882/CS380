import sys
import random
from collections import deque
import time

class Sbp:  # Define the Sbp (Sliding Block Puzzle) class
    def __init__(self):  # Constructor method
        self.width = 0  # Initialize width of the board
        self.height = 0  # Initialize height of the board
        self.board = []  # Initialize empty board

    def load_board(self, filename):  # Method to load board from a file
        try:
            with open(filename, 'r') as file:  # Open the file in read mode
                content = file.read().strip()  # Read and strip whitespace from file content
            # Parse width, height, and board
            parts = content.split(",")  # Split content by commas
            self.width = int(parts[0])  # Set width from first part
            self.height = int(parts[1])  # Set height from second part
            self.board = [  # Create 2D list for board
                list(map(int, parts[i * self.width + 2:(i + 1) * self.width + 2]))
                for i in range(self.height)
            ]
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found.")
            sys.exit(1)
        except ValueError:
            print("Error: File content format is invalid.")
            sys.exit(1)
        except Exception as e:  # Catch all other exceptions
            print(f"Error loading game state: {e}")
            sys.exit(1)

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

    def can_move(self, piece, direction):  # Method to check if a move is valid
        cells = self.get_piece_cells(piece)  # Get coordinates of the piece
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]  # Get direction vector

        for x, y in cells:  # Iterate over piece cells
            new_x, new_y = x + dx, y + dy  # Calculate new position
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):  # Check if new position is within bounds
                return False  # Return False if out of bounds
            if self.board[new_y][new_x] not in [0, -1] and (
                    new_x, new_y) not in cells:  # Check if new position is occupied by another piece
                return False  # Return False if occupied by another piece

            # Allow piece 2 to move into the empty space (-1)
            if self.board[new_y][new_x] == -1 and piece != 2:
                return False  # Return False if a piece other than 2 is trying to move into empty space (-1)

        return True  # Return True if move is valid

    def available_moves(self):  # Method to get all available moves
        moves = []  # Initialize empty list for moves
        pieces = set(val for row in self.board for val in row if val >= 2)  # Get set of all pieces
        directions = ["up", "down", "left", "right"]  # List of possible directions

        for piece in pieces:  # Iterate over pieces
            for direction in directions:  # Iterate over directions
                if self.can_move(piece, direction):  # Check if move is valid
                    moves.append((piece, direction))  # Add valid move to list
        return moves  # Return list of available moves

    def apply_move(self, piece, direction):  # Method to apply a move
        cells = self.get_piece_cells(piece)  # Get coordinates of the piece
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]  # Get direction vector

        for x, y in cells:  # Iterate over piece cells
            self.board[y][x] = 0 if self.board[y][x] != -1 else -1  # Clear old position

        for x, y in cells:  # Iterate over piece cells
            self.board[y + dy][x + dx] = piece  # Set new position

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
        nodes_explored = 0

        while queue:
            moves_list, current_state = queue.popleft()
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

            for piece, direction in temp_puzzle.available_moves():
                new_puzzle = Sbp()
                new_puzzle.width = self.width
                new_puzzle.height = self.height
                new_puzzle.board = [row[:] for row in current_state]

                new_puzzle.apply_move(piece, direction)
                new_puzzle.normalize()

                if new_puzzle.board not in visited:
                    queue.append((moves_list + [(piece, direction)], new_puzzle.board))
                    visited.append(new_puzzle.board)

        return False

    def print_board(self):
        for row in self.board:
            print(" ".join(str(x) for x in row))

def main():
    puzzle = Sbp()
    puzzle.load_board('puzzle.txt')
    print("Initial State:")
    puzzle.print_board()
    print()

    while not puzzle.is_done():
        moves = puzzle.available_moves()
        if not moves:
            print("No solution found.")
            break

        move = random.choice(moves)
        piece, direction = move
        puzzle.apply_move(piece, direction)
        puzzle.print_board()
        print()

    if puzzle.is_done():
        print("Puzzle Solved!")
    else:
        print("Unable to solve puzzle.")

if __name__ == "__main__":
    main()
