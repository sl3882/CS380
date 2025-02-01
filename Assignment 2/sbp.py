import sys
import random
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
            print(f"Error loading game state : {e}")
            sys.exit(1)

    def clone_state(self):
        return [row[:] for row in self.board]
    def is_done(self):
        # Puzzle is solved if no -1 cells remain
        return not any(-1 in row for row in self.board)
    def get_piece_cells(self, piece):
        """Return all cells occupied by a piece"""
        cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == piece:
                    cells.append((x, y))
        return cells

    def can_move(self, piece, direction):
        """Check if a piece can move in given direction"""
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        for x, y in cells:
            new_x, new_y = x + dx, y + dy
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                return False
            if self.board[new_y][new_x] not in [0, -1] and (new_x, new_y) not in cells:
                return False
        return True

    def get_available_moves(self):
        """Get all possible moves for all pieces"""
        moves = []
        pieces = set(val for row in self.board for val in row if val >= 2)
        directions = ["up", "down", "left", "right"]

        for piece in pieces:
            for direction in directions:
                if self.can_move(piece, direction):
                    moves.append((piece, direction))
        return moves

    def apply_move(self, piece, direction):
        """Apply a move to the board"""
        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        # Clear current positions
        for x, y in cells:
            self.board[y][x] = 0 if self.board[y][x] != -1 else -1

        # Set new positions
        for x, y in cells:
            self.board[y + dy][x + dx] = piece

    def compare_board(self, other_board):
        """Compare this board with another board"""
        if len(self.board) != len(other_board) or len(self.board[0]) != len(other_board[0]):
            return False
        return all(self.board[i][j] == other_board[i][j]
                   for i in range(len(self.board))
                   for j in range(len(self.board[0])))

    def normalize(self):
        """Normalize the board state"""
        next_idx = 3
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == next_idx:
                    next_idx += 1
                elif self.board[y][x] > next_idx:
                    # Swap indices
                    old_idx = self.board[y][x]
                    for i in range(self.height):
                        for j in range(self.width):
                            if self.board[i][j] == next_idx:
                                self.board[i][j] = old_idx
                            elif self.board[i][j] == old_idx:
                                self.board[i][j] = next_idx
                    next_idx += 1

    def random_walk(self, N):
        """Perform N random moves"""
        history = []
        for _ in range(N):
            moves = self.get_available_moves()
            if not moves or self.is_done():
                break
            piece, direction = random.choice(moves)
            self.apply_move(piece, direction)
            self.normalize()
            history.append(((piece, direction), self.clone_state()))
        return history
    def print_board(self):
        print(f"{self.width},{self.height},")
        for row in self.board:
            print(",".join(map(str, row)))

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
        for move in puzzle.get_available_moves():
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

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
