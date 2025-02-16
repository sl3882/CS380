import sys
import time
from collections import deque
import copy

class Puzzle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]

    def load_board(self, filename):
        try:
            with open(filename, 'r') as file:
                content = file.read().strip()

            rows = content.split("\n")
            for y in range(self.height):
                for x in range(self.width):
                    self.board[y][x] = int(rows[y][x])

        except Exception as e:
            print(f"Error loading game state from {filename}: {e}")
            return False
        return True

    def clone_state(self):
        return copy.deepcopy(self.board)

    def normalize(self):
        next_idx = 3  # Start with index 3
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == next_idx:
                    next_idx += 1
                elif self.board[y][x] > next_idx:
                    self.swap_cells(y, x, next_idx)
                    next_idx += 1

    def swap_cells(self, y, x, next_idx):
        old_idx = self.board[y][x]
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == next_idx:
                    self.board[i][j] = old_idx
                elif self.board[i][j] == old_idx:
                    self.board[i][j] = next_idx

    def available_moves(self):
        moves = []
        piece_positions = self.get_piece_positions()

        for piece, positions in piece_positions.items():
            min_r = min(r for r, _ in positions)
            max_r = max(r for r, _ in positions)
            min_c = min(c for _, c in positions)
            max_c = max(c for _, c in positions)

            # Only check moves if the piece is near the edge
            if min_r > 0:  # Up movement check
                moves.append(('up', piece))
            if max_r < self.height - 1:  # Down movement check
                moves.append(('down', piece))
            if min_c > 0:  # Left movement check
                moves.append(('left', piece))
            if max_c < self.width - 1:  # Right movement check
                moves.append(('right', piece))

        return moves

    def get_piece_positions(self):
        piece_positions = {}
        for y in range(self.height):
            for x in range(self.width):
                piece = self.board[y][x]
                if piece != 0:
                    if piece not in piece_positions:
                        piece_positions[piece] = []
                    piece_positions[piece].append((y, x))
        return piece_positions

    def is_done(self):
        # Check if the board is in the goal state
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != (y * self.width + x + 1):
                    return False
        return True

    def apply_move(self, piece, direction):
        piece_positions = self.get_piece_positions()
        positions = piece_positions.get(piece)

        if not positions:
            print(f"Piece {piece} not found.")
            return False

        # Find the first position of the piece and apply the move
        y, x = positions[0]
        if direction == 'up' and y > 0:
            self.board[y - 1][x] = piece
            self.board[y][x] = 0
        elif direction == 'down' and y < self.height - 1:
            self.board[y + 1][x] = piece
            self.board[y][x] = 0
        elif direction == 'left' and x > 0:
            self.board[y][x - 1] = piece
            self.board[y][x] = 0
        elif direction == 'right' and x < self.width - 1:
            self.board[y][x + 1] = piece
            self.board[y][x] = 0
        else:
            print(f"Invalid move: {piece} cannot move {direction}.")
            return False
        return True

    def bfs(self):
        start_time = time.time()
        initial_state = self.clone_state()
        queue = deque([([], initial_state)])
        visited = set()
        visited.add(tuple(map(tuple, initial_state)))  # Hashable state for set
        nodes_explored = 1

        while queue:
            moves, current_state = queue.popleft()
            temp_puzzle = Puzzle(self.width, self.height)
            temp_puzzle.board = current_state

            # Check if the puzzle is done
            if self.apply_and_check_state(moves, temp_puzzle):
                break

            available_moves = temp_puzzle.available_moves()
            for move in available_moves:
                piece, direction = move
                new_state = self.clone_state()
                temp_puzzle.board = new_state

                temp_puzzle.apply_move(piece, direction)
                temp_puzzle.normalize()

                if temp_puzzle.is_done():
                    print(f"Solution found: {moves + [(piece, direction)]}")
                    break
                if tuple(map(tuple, temp_puzzle.board)) not in visited:
                    visited.add(tuple(map(tuple, temp_puzzle.board)))
                    queue.append((moves + [(piece, direction)], temp_puzzle.board))
                    nodes_explored += 1

        print(f"BFS complete: {nodes_explored} nodes explored.")
        print(f"Time taken: {time.time() - start_time} seconds.")

    def apply_and_check_state(self, moves, temp_puzzle):
        temp_puzzle.apply_move(*moves[-1])
        temp_puzzle.normalize()

        if temp_puzzle.is_done():
            print(f"Solution found: {moves}")
            return True
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 sbp.py <command> <filename> [args]")
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    puzzle = Puzzle(4, 4)
    puzzle.load_board(filename)

    if command == "print":
        for row in puzzle.board:
            print(" ".join(map(str, row)))
    elif command == "done":
        print("Puzzle done:", puzzle.is_done())
    elif command == "availableMoves":
        moves = puzzle.available_moves()
        print("Available moves:", moves)
    elif command == "applyMove":
        piece, direction = sys.argv[3], sys.argv[4]
        puzzle.apply_move(int(piece), direction)
        print("Board after move:", puzzle.board)
    elif command == "compare":
        other_filename = sys.argv[3]
        other_puzzle = Puzzle(4, 4)
        other_puzzle.load_board(other_filename)
        print("Boards are equal:", puzzle.board == other_puzzle.board)
    elif command == "norm":
        puzzle.normalize()
        print("Board after normalization:", puzzle.board)
    elif command == "random":
        # Random walk logic
        pass
    elif command == "bfs":
        puzzle.bfs()
    else:
        print(
            f"Unknown command: {command}. Please use one of: print, done, availableMoves, applyMove, compare, norm, random, bfs")

if __name__ == "__main__":
    main()
