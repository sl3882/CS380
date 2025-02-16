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
        new_sbp = Sbp()
        new_sbp.width = self.width
        new_sbp.height = self.height
        new_sbp.board = [row[:] for row in self.board]
        return new_sbp

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

            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                return False

            target_cell = self.board[new_y][new_x]

            if target_cell == 1 or (target_cell == -1 and piece != 2):
                return False

            if target_cell == 0:
                continue

            if target_cell > 1 and (new_x, new_y) not in cells:
                return False

        return True

    def available_moves(self):
        moves = []
        pieces = sorted(set(val for row in self.board for val in row if val >= 2))
        directions = ["up", "down", "left", "right"]

        for piece in pieces:
            for direction in directions:
                if self.can_move(piece, direction):
                    moves.append((piece, direction))
        return moves

    def apply_move(self, piece, direction):
        if not self.can_move(piece, direction):
            return

        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        old_positions = {(x, y): self.board[y][x] for x, y in cells}

        for x, y in cells:
            if old_positions[(x, y)] == -1:
                continue
            self.board[y][x] = 0

        for x, y in cells:
            self.board[y + dy][x + dx] = piece

        # self.normalize()

    def print_board(self):
        print(f"{self.width},{self.height},")
        for row in self.board:
            print(",".join(map(str, row)) + ",")

    def print_solution(self, moves, state, nodes_explored, start_time):
        end_time = time.time()
        elapsed_time = end_time - start_time

        for piece, direction in moves:
            print(f"({piece},{direction})")
        print()

        state.print_board()
        print()

        print(nodes_explored)
        print(f"{elapsed_time:.2f}")
        print(len(moves))

    def compare_states(self, other):
        if self.width != other.width or self.height != other.height:
            return False
        for row1, row2 in zip(self.board, other.board):
            if row1 != row2:
                return False
        return True

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
            history.append(((piece, direction), self.clone_state()))
        return history

    def board_to_tuple(self):
        return tuple(tuple(row) for row in self.board)

    def bfs(self, filename):
        start_time = time.time()
        self.load_board(filename)

        queue = deque([(self, [])])
        visited = {self.board_to_tuple()}
        nodes_explored = 1

        while queue:
            current_state, moves = queue.popleft()
            nodes_explored += 1

            if current_state.is_done():
                nodes_explored += 1
                self.print_solution(moves, current_state, nodes_explored, start_time)
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
        start_time = time.time()
        self.load_board(filename)

        stack = [(self, [])]
        visited = set()
        nodes_explored = 0

        while stack:
            current_state, moves = stack.pop()
            current_tuple = current_state.board_to_tuple()


            if current_tuple in visited:
                continue

            visited.add(current_tuple)
            nodes_explored += 1

            if current_state.is_done():
                self.print_solution(moves, current_state, nodes_explored, start_time)
                return

            for piece, direction in reversed(current_state.available_moves()):
                new_state = current_state.clone_state()
                new_state.apply_move(piece, direction)
                # new_state.normalize()
                new_board_tuple = new_state.board_to_tuple()

                if new_board_tuple not in visited:
                    stack.append((new_state, moves + [(piece, direction)]))

        print("No solution found")
        return






    def ids(self, filename):
        start_time = time.time()
        nodes_explored = 0
        for depth_limit in range(1, 50):
            visited = {self.board_to_tuple()}
            def dls(state, moves, depth):
                nonlocal nodes_explored

                nodes_explored += 1
                if state.is_done():
                    nodes_explored += 1
                    self.print_solution(moves, state, nodes_explored, start_time)
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
                        if dls(new_state, moves + [(piece, direction)], depth + 1):
                            return True
                        visited.remove(new_board_tuple)
                return False
            self.load_board(filename)
            if dls(self, [], 0):
                return
        print("No solution found within reasonable depth")

    def manhattan_distance(self):

        # Find the goal location (-1)
        goal_x, goal_y = None, None
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == -1:
                    break
            if goal_x is not None:
                break

        if goal_x is None:
            return 0

        master_cells = self.get_piece_cells(2)
        if not master_cells:
            return float('inf')

        centroid_x = sum(x for x, _ in master_cells) / len(master_cells)
        centroid_y = sum(y for _, y in master_cells) / len(master_cells)

        distance = abs(centroid_x - goal_x) + abs(centroid_y - goal_y)

        return distance

    def astar(self, filename):
        start_time = time.time()
        self.load_board(filename)
        initial_state = self.clone_state()

        g_score = {initial_state.board_to_tuple(): 0}

        counter = 0
        pq = [(initial_state.manhattan_distance(), counter, initial_state, [])]
        counter += 1

        visited = set()
        nodes_explored = 0

        while pq:
            min_idx = 0
            for i in range(1, len(pq)):
                if pq[i][0] < pq[min_idx][0]:  # Compare f_scores
                    min_idx = i
                elif pq[i][0] == pq[min_idx][0] and pq[i][1] < pq[min_idx][1]:  # Tiebreaker using counter
                    min_idx = i

            _, _, current_state, moves = pq.pop(min_idx)
            current_tuple = current_state.board_to_tuple()

            if current_tuple in visited:
                continue

            visited.add(current_tuple)
            nodes_explored += 1

            if current_state.is_done():
                self.print_solution(moves, current_state, nodes_explored, start_time)
                return

            current_g = g_score[current_tuple]

            for piece, direction in current_state.available_moves():
                new_state = current_state.clone_state()
                new_state.apply_move(piece, direction)
                new_state.normalize()
                new_tuple = new_state.board_to_tuple()

                new_g = current_g + 1

                if new_tuple not in g_score or new_g < g_score[new_tuple]:
                    g_score[new_tuple] = new_g

                    f_score = new_g + new_state.manhattan_distance()

                    pq.append((f_score, counter, new_state, moves + [(piece, direction)]))
                    counter += 1

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
        puzzle.normalize()


    elif command == "ids":
        puzzle.ids(filename)

    elif command == "astar":
        puzzle.astar(filename)



    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
