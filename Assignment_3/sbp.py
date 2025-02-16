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
        except Exception as e:
            print(f"Error loading game state : {e}")
            sys.exit(1)

    def clone_state(self):
        return [row[:] for row in self.board]

    def is_done(self):
        return not any(-1 in row for row in self.board)

    def get_piece_cells(self, piece):
        cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == piece:
                    cells.append((x, y))
        return cells

    def can_move(self, piece, direction):
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        for x, y in cells:
            new_x, new_y = x + dx, y + dy

            # Check boundaries *first*
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                return False  # Out of bounds

            target_cell = self.board[new_y][new_x]

            if target_cell == 0:
                continue  # Empty cell, move is okay

            if target_cell == -1 and piece != 2:
                return False  # Goal cell, only piece 2 can enter

            # Blocked by another piece (or boundary)
            if target_cell not in [0, -1] and (new_x, new_y) not in cells:
                return False

        return True  # All checks passed, move is valid

    def available_moves(self):
        moves = []
        pieces = set(val for row in self.board for val in row if val >= 2)
        directions = ["up", "down", "left", "right"]

        for piece in pieces:
            for direction in directions:
                if self.can_move(piece, direction):
                    moves.append((piece, direction))
        return moves

    def apply_move(self, piece, direction):
        if not self.can_move(piece, direction):  # Crucial: Check *before* applying
            return  # Or raise an exception if you prefer to be explicit

        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        old_positions = {(x, y): self.board[y][x] for x, y in cells}

        for x, y in cells:
            if old_positions[(x, y)] == -1:
                continue
            self.board[y][x] = 0

        for x, y in cells:
            self.board[y + dy][x + dx] = piece

    def apply_move_and_return_new_state(self, piece, direction):
        return self.apply_move(piece, direction)

    def compare_board(self, other_board):
        if len(self.board) != len(other_board) or len(self.board[0]) != len(other_board[0]):
            return False
        return all(self.board[i][j] == other_board[i][j]
                   for i in range(len(self.board))
                   for j in range(len(self.board[0])))

    def normalize(self):
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
        history = []
        for _ in range(N):
            moves = self.available_moves()
            if not moves or self.is_done():
                break
            piece, direction = random.choice(moves)
            self.apply_move(piece, direction)
            self.normalize()
            history.append(((piece, direction), self.clone_state()))
        return history

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
        visited = {tuple(tuple(row) for row in initial_state)}  # Use a set for faster lookups
        nodes_explored = 0

        while stack:
            moves_list, current_state = stack.pop()
            nodes_explored += 1

            if self.is_done_check(current_state):  # Helper function for is_done()
                end_time = time.time()
                self.print_moves(moves_list)  # Helper function to print moves
                self.print_board_from_state(current_state)  # Helper function to print board
                print(nodes_explored)
                print(f"{end_time - start_time:.2f}")
                print(len(moves_list))
                return True

            available_moves = self.get_available_moves(current_state)  # Helper function to get available moves
            if (2, "left") in available_moves:
                available_moves.remove((2, "left"))  # Remove from original list
                available_moves.insert(0, (2, "left"))  # Insert at the beginning

            for piece, direction in available_moves:
                new_state = self.get_next_state(current_state, piece, direction)  # Helper function to get next state

                board_tuple = tuple(tuple(row) for row in new_state)

                if board_tuple not in visited:
                    visited.add(board_tuple)
                    new_moves = moves_list + [(piece, direction)]
                    stack.append((new_moves, new_state))

        return False

    def is_done_check(self, state):
        return not any(-1 in row for row in state)

    def print_moves(self, moves_list):
        for piece, direction in moves_list:
            print(f"({piece},{direction})")
        print()

    def print_board_from_state(self, state):
        print(f"{self.width},{self.height},")
        for row in state:
            print(",".join(map(str, row)) + ",")
        print()

    def get_available_moves(self, state):
        available = []
        pieces = set(val for row in state for val in row if val >= 2)
        directions = ["left", "right", "up", "down"]  # Consistent move order

        for piece in pieces:
            for direction in directions:
                temp_puzzle = Sbp()
                temp_puzzle.width = self.width
                temp_puzzle.height = self.height
                temp_puzzle.board = state
                if temp_puzzle.can_move(piece, direction):
                    available.append((piece, direction))
        return available

    def get_next_state(self, current_state, piece, direction):
        new_puzzle = Sbp()
        new_puzzle.width = self.width
        new_puzzle.height = self.height
        new_puzzle.board = [row[:] for row in current_state]  # Directly copy the state

        new_puzzle.apply_move(piece, direction)  # Apply move in the new puzzle
        new_puzzle.normalize()
        return new_puzzle.board

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
