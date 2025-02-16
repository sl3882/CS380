import sys

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

    def clone_state(self):
        return [row[:] for row in self.board]

    def is_done(self):
        return not any(-1 in row for row in self.board)

    def print_board(self):
        print(f"{self.width},{self.height},")
        for row in self.board:
            print(",".join(map(str, row)) + ",")
    def available_moves(self):
        moves = []
        directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        pieces = set()
        for row in self.board:
            for cell in row:
                if cell > 2:
                    pieces.add(cell)
        for piece in pieces:
            for direction, (dx, dy) in directions.items():
                for i in range(self.height):
                    for j in range(self.width):
                        if self.board[i][j] == piece:
                            ni, nj = i + dx, j + dy
                            if 0 <= ni < self.height and 0 <= nj < self.width and self.board[ni][nj] == 0:
                                # Check if the entire piece can move in the given direction
                                can_move = True
                                for k in range(self.height):
                                    for l in range(self.width):
                                        if self.board[k][l] == piece:
                                            nk, nl = k + dx, l + dy
                                            if not (0 <= nk < self.height and 0 <= nl < self.width and self.board[nk][nl] == 0):
                                                can_move = False
                                                break
                                    if not can_move:
                                        break
                                if can_move:
                                    moves.append((piece, direction))
        return moves
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





    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()