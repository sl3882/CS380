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
    def is_solved(self):
        for row in self.board:
            if -1 in row:
                return False
        return True

def main(command, filename=None):
    if command == "print" and filename:
        puzzle = SlidingBrickPuzzle()
        puzzle.load_state(filename)
        puzzle.display_state()
    elif command == "done" and filename:
        puzzle = SlidingBrickPuzzle()
        puzzle.load_state(filename)
        print(puzzle.is_solved())

if __name__ == "__main__":
    args = sys.argv[1:]
    main(*args)
