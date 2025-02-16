import copy
import sys

class SlidingBrickPuzzle:
    def __init__(self):
        self.board = []
        self.width = 0
        self.height = 0

    def load_state(self, filename):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                dimensions = lines[0].strip().split(',')
                self.width = int(dimensions[0])
                self.height = int(dimensions[1])
                self.board = []
                for line in lines[1:]:
                    row = list(map(int, line.strip().split(',')))
                    self.board.append(row)
        except Exception as e:
            print(f"Error loading state from file: {e}")

    def display_state(self):
        print(f"{self.width},{self.height},")
        for row in self.board:
            print(','.join(map(str, row)) + ',')
    def clone_state(self):
        cloned_puzzle = SlidingBrickPuzzle()
        cloned_puzzle.width = self.width
        cloned_puzzle.height = self.height
        cloned_puzzle.board = copy.deepcopy(self.board)
        return cloned_puzzle
    def is_done(self):  # Method to check if the puzzle is solved
        return not any(-1 in row for row in self.board)  # Check if any -1 (empty space) remains

def main():  # Main function
    if len(sys.argv) < 3:  # Check if enough command-line arguments are provided
        print("Usage: python3 sbp.py <command> <filename> [args]")  # Print usage instructions
        sys.exit(1)  # Exit with error code 1

    command = sys.argv[1]  # Get command from command-line arguments
    filename = sys.argv[2]  # Get filename from command-line arguments
    puzzle = SlidingBrickPuzzle()  # Create Sbp instance

    if command == "print":  # If command is "print"
        puzzle.load_state(filename)  # Load board from file
        puzzle.display_state()  # Print the board

    elif command == "done":  # If command is "done"
        puzzle.load_state(filename)  # Load board from file
        print(puzzle.is_done())  # Print whether puzzle is solved


if __name__ == "__main__":
    main()
