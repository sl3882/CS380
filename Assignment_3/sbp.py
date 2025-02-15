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

    def get_piece_positions(self):
        """Returns a dictionary mapping piece IDs to their positions on the board."""
        pieces = {}
        for r in range(self.height):
            for c in range(self.width):
                piece = self.board[r][c]
                if piece > 0:  # Ignore empty cells and walls
                    if piece not in pieces:
                        pieces[piece] = []
                    pieces[piece].append((r, c))
        return pieces

    def available_moves(self):
        """Returns a list of all available moves as (piece, direction)."""
        moves = []
        piece_positions = self.get_piece_positions()

        for piece, positions in piece_positions.items():
            min_r = min(r for r, _ in positions)
            max_r = max(r for r, _ in positions)
            min_c = min(c for _, c in positions)
            max_c = max(c for _, c in positions)

            # Check movement in all four directions
            if min_r > 0 and self.board[min_r - 1][min_c] == 0:  # Up
                moves.append((piece, "up"))
            if max_r < self.height - 1 and self.board[max_r + 1][min_c] == 0:  # Down
                moves.append((piece, "down"))
            if min_c > 0 and self.board[min_r][min_c - 1] == 0:  # Left
                moves.append((piece, "left"))
            if max_c < self.width - 1 and self.board[min_r][max_c + 1] == 0:  # Right
                moves.append((piece, "right"))

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