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
        return [(x, y) for y in range(self.height) for x in range(self.width) if self.board[y][x] == piece]

    def can_move(self, piece, direction):
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        for x, y in cells:
            new_x, new_y = x + dx, y + dy
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                return False
            if self.board[new_y][new_x] not in [0, -1] and (new_x, new_y) not in cells:
                return False
            if self.board[new_y][new_x] == -1 and piece != 2:
                return False

        return True

    def available_moves(self):
        pieces = {val for row in self.board for val in row if val >= 2}
        directions = ["up", "down", "left", "right"]
        return [(piece, direction) for piece in pieces for direction in directions if self.can_move(piece, direction)]

    def apply_move(self, piece, direction):
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        for x, y in cells:
            self.board[y][x] = 0 if self.board[y][x] != -1 else -1

        for x, y in cells:
            self.board[y + dy][x + dx] = piece

    def compare_board(self, other_board):
        return self.board == other_board

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

    def search(self, strategy='bfs', depth_limit=50):
        start_time = time.time()
        initial_state = self.clone_state()
        if strategy == 'bfs':
            queue = deque([([], initial_state)])
        else:
            queue = [([], initial_state, 0)]
        visited = set()
        visited.add(tuple(map(tuple, initial_state)))
        nodes_explored = 0

        while queue:
            if strategy == 'bfs':
                moves_list, current_state = queue.popleft()
            else:
                moves_list, current_state, current_depth = queue.pop()

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

            if strategy == 'dfs' and current_depth >= depth_limit:
                continue

            for piece, direction in temp_puzzle.available_moves():
                new_puzzle = Sbp()
                new_puzzle.width = self.width
                new_puzzle.height = self.height
                new_puzzle.board = temp_puzzle.clone_state()
                new_puzzle.apply_move(piece, direction)
                new_puzzle.normalize()

                new_board_tuple = tuple(map(tuple, new_puzzle.board))
                if new_board_tuple not in visited:
                    visited.add(new_board_tuple)
                    new_moves = moves_list + [(piece, direction)]
                    if strategy == 'bfs':
                        queue.append((new_moves, new_puzzle.board))
                    else:
                        queue.append((new_moves, new_puzzle.board, current_depth + 1))

        return False

    def bfs(self):
        return self.search(strategy='bfs')

    def dfs(self, depth_limit=50):
        return self.search(strategy='dfs', depth_limit=depth_limit)

    def print_board(self):
        print(f"{self.width},{self.height},")
        for row in self.board:
            print(",".join(map(str, row)) + ",")

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
        for move in puzzle.available_moves():
            print(f"({move[0]}, {move[1]})")

    elif command == "applyMove":
        if len(sys.argv) != 4:
            print("Usage: python3 sbp.py applyMove <filename> <move>")
            sys.exit(1)
        puzzle.load_board(filename)
        move = sys.argv[3].strip("()")
        piece, direction = move.split(",")
        puzzle.apply_move(int(piece), direction.strip())
        puzzle.print_board()

    elif command == "compare":
        if len(sys.argv) != 4:
            print("Usage: python3 sbp.py compare <filename1> <filename2>")
            sys.exit(1)
        puzzle2 = Sbp()
        puzzle.load_board(filename)
        puzzle2.load_board(sys.argv[3])
        print(puzzle.compare_board(puzzle2.board))

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
        puzzle.load_board(filename)
        puzzle.normalize()
        puzzle.bfs()

    elif command == "dfs":
        puzzle.load_board(filename)
        puzzle.normalize()
        puzzle.dfs()

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()