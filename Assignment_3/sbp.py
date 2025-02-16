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
            parts = content.split(",")
            self.width = int(parts[0])
            self.height = int(parts[1])
            self.board = [
                list(map(int, parts[i * self.width + 2:(i + 1) * self.width + 2]))
                for i in range(self.height)
            ]
        except FileNotFoundError:
            print(f"Error: File not found: {filename}")
            sys.exit(1)
        except ValueError:
            print(f"Error: Invalid data in file: {filename}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading game state: {e}")
            sys.exit(1)

    def clone_state(self):
        """Creates a deep copy of the board state."""
        new_sbp = Sbp()
        new_sbp.width = self.width
        new_sbp.height = self.height
        new_sbp.board = [row[:] for row in self.board]
        return new_sbp

    def is_done(self):
        """Checks if the puzzle is solved."""
        return not any(-1 in row for row in self.board)

    def get_piece_cells(self, piece):
        """Gets the coordinates of all cells occupied by a piece."""
        cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == piece:
                    cells.append((x, y))
        return cells

    def can_move(self, piece, direction):
        """Checks if a piece can move in a given direction."""
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        for x, y in cells:
            new_x, new_y = x + dx, y + dy

            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                return False

            target_cell = self.board[new_y][new_x]

            # if target_cell == 0:
            #     continue
            if target_cell == 1:
                return False

            if target_cell == -1 and piece != 2:
                return False

            if target_cell not in [0, -1] and (new_x, new_y) not in cells:
                return False

        return True

    def available_moves(self):
        """Gets all available moves."""
        moves = []
        pieces = sorted(set(val for row in self.board for val in row if val >= 2))
        directions = ["up", "down", "left", "right"]

        for piece in pieces:
            for direction in directions:
                if self.can_move(piece, direction):
                    moves.append((piece, direction))
        return moves

    def apply_move(self, piece, direction):
        """Applies a move to the board."""
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        # for x, y in cells:
        #     self.board[y][x] = 0

        for x, y in cells:
            new_x, new_y = x + dx, y + dy
            self.board[new_y][new_x] = piece


        self.normalize()

    def print_board(self):
        """Prints the board."""
        print(f"{self.width},{self.height},")
        for row in self.board:
            print(",".join(map(str, row)) + ",")

    def compare_states(self, other):
        """Compares the current state with another state."""
        if self.width != other.width or self.height != other.height:
            return False
        for row1, row2 in zip(self.board, other.board):
            if row1 != row2:
                return False
        return True

    def normalize(self):
        """Normalizes the piece numbering on the board."""
        next_idx = 3
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == next_idx:
                    next_idx += 1
                elif self.board[y][x] > next_idx:
                    old_idx = self.board[y][x]
                    for i in range(self.height):
                        for j in range(self.width):
                            if self.board[i][j] == next_idx:
                                self.board[i][j] = old_idx
                            elif self.board[i][j] == old_idx:
                                self.board[i][j] = next_idx
                    next_idx += 1

    def random_walk(self, N):
        """Performs a random walk."""
        history = []
        for _ in range(N):
            moves = self.available_moves()
            if not moves or self.is_done():
                break
            piece, direction = random.choice(moves)
            self.apply_move(piece, direction)
            history.append(((piece, direction), self.clone_state()))
        return history

    def board_to_tuple(self):
        """Converts the board to a tuple of tuples for hashing."""
        return tuple(tuple(row) for row in self.board)

    def bfs(self, filename):
        """Performs a breadth-first search to solve the puzzle."""
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

    def dfs(self, filename):
        """Performs a depth-first search to solve the puzzle."""
        start_time = time.time()
        self.load_board(filename)
        initial_state = self.clone_state()
        stack = [(self, [])]  # Stack of (state, moves)
        visited = {self.board_to_tuple()}  # Set of visited states
        nodes_explored = 1

        while stack:
            current_state, moves = stack.pop()  # Pop from the stack (LIFO)
            nodes_explored += 1

            if current_state.is_done():
                end_time = time.time()
                elapsed_time = end_time - start_time
                nodes_explored += 1
                # Print the moves in the required format
                for piece, direction in moves:
                    print(f"({piece},{direction})")
                print()

                # Print the final state
                current_state.print_board()
                print()

                # Print statistics
                print(nodes_explored)
                print(f"{elapsed_time:.2f}")
                print(len(moves))
                return

            # Explore available moves in reverse order (to prioritize certain moves)
            for piece, direction in reversed(current_state.available_moves()):
                new_state = current_state.clone_state()
                new_state.apply_move(piece, direction)
                new_state.normalize()
                new_board_tuple = new_state.board_to_tuple()

                if new_board_tuple not in visited:
                    visited.add(new_board_tuple)
                    stack.append((new_state, moves + [(piece, direction)]))  # Push to the stack

        print("No solution found")
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
