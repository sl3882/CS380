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
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()