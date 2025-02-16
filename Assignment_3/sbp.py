import sys
import random
from collections import deque
import time

class Sbp:

    def __init__(self):  # Constructor method for initializing the Sbp object
        self.width = 0  # Initialize the width of the board
        self.height = 0  # Initialize the height of the board
        self.board = []  # Initialize the board as an empty list

    def load_board(self, filename):  # Method to load the board from a file
        try:  # Start a try block to handle potential exceptions
            with open(filename, 'r') as file:  # Open the file in read mode
                content = file.read().strip()  # Read the file content and remove leading/trailing whitespace
            parts = content.split(",")  # Split the content by commas
            self.width = int(parts[0])  # Set the width from the first part
            self.height = int(parts[1])  # Set the height from the second part
            self.board = [  # Construct the board as a 2D list
                list(map(int, parts[i * self.width + 2:(i + 1) * self.width + 2]))
                for i in range(self.height)
            ]
        except FileNotFoundError:  # Handle file not found exception
            print(f"Error: File not found: {filename}")
            sys.exit(1)  # Exit the program with status code 1
        except ValueError:  # Handle invalid data exception
            print(f"Error: Invalid data in file: {filename}")
            sys.exit(1)  # Exit the program with status code 1
        except Exception as e:  # Handle any other exceptions
            print(f"Error loading game state: {e}")
            sys.exit(1)  # Exit the program with status code 1

    def clone_state(self):  # Method to create a deep copy of the current state
        new_sbp = Sbp()  # Create a new Sbp object
        new_sbp.width = self.width  # Copy the width
        new_sbp.height = self.height  # Copy the height
        new_sbp.board = [row[:] for row in self.board]  # Deep copy the board
        return new_sbp  # Return the cloned object

    def is_done(self):  # Method to check if the puzzle is solved
        return not any(-1 in row for row in self.board)  # Return True if no -1 (goal) is left on the board

    def get_piece_cells(self, piece):  # Method to get the positions of a specific piece
        cells = []  # Initialize an empty list for cell positions
        for y in range(self.height):  # Iterate over each row
            for x in range(self.width):  # Iterate over each column
                if self.board[y][x] == piece:  # Check if the cell contains the specified piece
                    cells.append((x, y))  # Add the cell position to the list
        return cells  # Return the list of cell positions

    def can_move(self, piece, direction):  # Method to check if a piece can move in a given direction
        cells = self.get_piece_cells(piece)  # Get the positions of the piece
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]  # Get the direction vector

        for x, y in cells:  # Iterate over each cell of the piece
            new_x, new_y = x + dx, y + dy  # Calculate the new position

            if not (0 <= new_x < self.width and 0 <= new_y < self.height):  # Check if the new position is within bounds
                return False  # Return False if out of bounds

            target_cell = self.board[new_y][new_x]  # Get the value of the target cell

            if target_cell == 1 or (target_cell == -1 and piece != 2):  # Check if the target cell is a wall or goal (for non-master pieces)
                return False  # Return False if movement is blocked

            if target_cell == 0:  # Check if the target cell is empty
                continue  # Continue to the next cell

            if target_cell > 1 and (new_x, new_y) not in cells:  # Check if the target cell is another piece
                return False  # Return False if movement is blocked by another piece

        return True  # Return True if the piece can move in the given direction

    def available_moves(self):  # Method to get all available moves for all pieces
        moves = []  # Initialize an empty list for moves
        pieces = sorted(set(val for row in self.board for val in row if val >= 2))  # Get all pieces on the board
        directions = ["up", "down", "left", "right"]  # Define possible directions

        for piece in pieces:  # Iterate over each piece
            for direction in directions:  # Iterate over each direction
                if self.can_move(piece, direction):  # Check if the piece can move in the direction
                    moves.append((piece, direction))  # Add the move to the list
        return moves  # Return the list of available moves

    def apply_move(self, piece, direction):  # Method to apply a move to the board
        if not self.can_move(piece, direction):  # Check if the move is valid
            return  # Return if the move is not valid

        cells = self.get_piece_cells(piece)  # Get the positions of the piece
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]  # Get the direction vector

        old_positions = {(x, y): self.board[y][x] for x, y in cells}  # Store the old positions of the piece

        for x, y in cells:  # Iterate over each cell of the piece
            if old_positions[(x, y)] == -1:  # Skip if the cell is a goal
                continue
            self.board[y][x] = 0  # Clear the current cell

        for x, y in cells:  # Iterate over each cell of the piece
            self.board[y + dy][x + dx] = piece  # Move the piece to the new position

        # self.normalize()

    def print_board(self):  # Method to print the board
        print(f"{self.width},{self.height},")  # Print the dimensions of the board
        for row in self.board:  # Iterate over each row
            print(", ".join(map(str, row)) + ",")  # Print the row as a comma-separated string

    def print_solution(self, moves, state, nodes_explored, start_time):  # Method to print the solution
        end_time = time.time()  # Get the current time
        elapsed_time = end_time - start_time  # Calculate the elapsed time

        for piece, direction in moves:  # Iterate over each move in the solution
            print(f"({piece},{direction})")  # Print the move
        print()  # Print a newline

        state.print_board()  # Print the final state of the board
        print()  # Print a newline

        print(nodes_explored)  # Print the number of nodes explored
        print(f"{elapsed_time:.2f}")  # Print the elapsed time
        print(len(moves))  # Print the number of moves

    def compare_states(self, other):  # Method to compare two states
        if self.width != other.width or self.height != other.height:  # Check if dimensions match
            return False  # Return False if dimensions do not match
        for row1, row2 in zip(self.board, other.board):  # Iterate over each row
            if row1 != row2:  # Check if rows are different
                return False  # Return False if rows are different
        return True  # Return True if states are identical

    def normalize(self):  # Method to normalize the board (reassign piece IDs)
        next_idx = 3  # Start assigning new IDs from 3
        for y in range(self.height):  # Iterate over each row
            for x in range(self.width):  # Iterate over each column
                if self.board[y][x] == next_idx:  # Check if the cell matches the next expected ID
                    next_idx += 1  # Increment the next expected ID
                elif self.board[y][x] > next_idx:  # Check if the cell has a higher ID than expected
                    old_idx = self.board[y][x]  # Store the old ID
                    for i in range(self.height):  # Iterate over each row
                        for j in range(self.width):  # Iterate over each column
                            if self.board[i][j] == next_idx:  # Check if the cell matches the next expected ID
                                self.board[i][j] = old_idx  # Swap the IDs
                            elif self.board[i][j] == old_idx:  # Check if the cell matches the old ID
                                self.board[i][j] = next_idx  # Swap the IDs
                    next_idx += 1  # Increment the next expected ID

    def random_walk(self, N):  # Method to perform a random walk of N moves
        history = []  # Initialize an empty list to store the history of moves
        for _ in range(N):  # Iterate N times
            moves = self.available_moves()  # Get all available moves
            if not moves or self.is_done():  # Check if no moves are available or the puzzle is solved
                break  # Exit the loop
            piece, direction = random.choice(moves)  # Choose a random move
            self.apply_move(piece, direction)  # Apply the move
            history.append(((piece, direction), self.clone_state()))  # Store the move and the new state
        return history  # Return the history of moves

    def board_to_tuple(self):  # Method to convert the board to a tuple (for hashing)
        return tuple(tuple(row) for row in self.board)  # Return the board as a tuple of tuples

    def bfs(self, filename):  # Method to perform Breadth-First Search (BFS)
        start_time = time.time()  # Record the start time
        self.load_board(filename)  # Load the board from the file

        queue = deque([(self, [])])  # Initialize the queue with the initial state and an empty move list
        visited = {self.board_to_tuple()}  # Initialize the visited set with the initial state
        nodes_explored = 1  # Initialize the node counter

        while queue:  # While the queue is not empty
            current_state, moves = queue.popleft()  # Dequeue the current state and its move list
            nodes_explored += 1  # Increment the node counter

            if current_state.is_done():  # Check if the current state is the goal state
                nodes_explored += 1  # Increment the node counter
                self.print_solution(moves, current_state, nodes_explored, start_time)  # Print the solution
                return  # Exit the method

            for piece, direction in current_state.available_moves():  # Iterate over all available moves
                new_state = current_state.clone_state()  # Clone the current state
                new_state.apply_move(piece, direction)  # Apply the move
                new_state.normalize()  # Normalize the new state
                new_board_tuple = new_state.board_to_tuple()  # Convert the new state to a tuple

                if new_board_tuple not in visited:  # Check if the new state has not been visited
                    visited.add(new_board_tuple)  # Mark the new state as visited
                    queue.append((new_state, moves + [(piece, direction)]))  # Enqueue the new state and updated move list

        print("No solution found")  # Print a message if no solution is found
        return  # Exit the method

    def dfs(self, filename):  # Method to perform Depth-First Search (DFS)
        start_time = time.time()  # Record the start time
        self.load_board(filename)  # Load the board from the file

        stack = [(self, [])]  # Initialize the stack with the initial state and an empty move list
        visited = set()  # Initialize the visited set
        nodes_explored = 0  # Initialize the node counter

        while stack:  # While the stack is not empty
            current_state, moves = stack.pop()  # Pop the current state and its move list
            current_tuple = current_state.board_to_tuple()  # Convert the current state to a tuple

            if current_tuple in visited:  # Check if the current state has been visited
                continue  # Skip this state

            visited.add(current_tuple)  # Mark the current state as visited
            nodes_explored += 1  # Increment the node counter

            if current_state.is_done():  # Check if the current state is the goal state
                self.print_solution(moves, current_state, nodes_explored, start_time)  # Print the solution
                return  # Exit the method

            for piece, direction in reversed(current_state.available_moves()):  # Iterate over all available moves in reverse order
                new_state = current_state.clone_state()  # Clone the current state
                new_state.apply_move(piece, direction)  # Apply the move
                new_board_tuple = new_state.board_to_tuple()  # Convert the new state to a tuple

                if new_board_tuple not in visited:  # Check if the new state has not been visited
                    stack.append((new_state, moves + [(piece, direction)]))  # Push the new state and updated move list onto the stack

        print("No solution found")  # Print a message if no solution is found
        return  # Exit the method

    def ids(self, filename):  # Method to perform Iterative Deepening Search (IDS)
        start_time = time.time()  # Record the start time
        nodes_explored = 0  # Initialize the node counter
        for depth_limit in range(1, 50):  # Iterate over depth limits from 1 to 49
            visited = {self.board_to_tuple()}  # Initialize the visited set with the initial state
            def dls(state, moves, depth):  # Define the Depth-Limited Search (DLS) function
                nonlocal nodes_explored  # Use the nonlocal keyword to modify the outer scope variable

                nodes_explored += 1  # Increment the node counter
                if state.is_done():  # Check if the current state is the goal state
                    nodes_explored += 1  # Increment the node counter
                    self.print_solution(moves, state, nodes_explored, start_time)  # Print the solution
                    return True  # Return True to indicate a solution was found

                if depth >= depth_limit:  # Check if the depth limit has been reached
                    return False  # Return False to indicate no solution was found at this depth

                for piece, direction in state.available_moves():  # Iterate over all available moves
                    new_state = state.clone_state()  # Clone the current state
                    new_state.apply_move(piece, direction)  # Apply the move
                    new_state.normalize()  # Normalize the new state
                    new_board_tuple = new_state.board_to_tuple()  # Convert the new state to a tuple

                    if new_board_tuple not in visited:  # Check if the new state has not been visited
                        visited.add(new_board_tuple)  # Mark the new state as visited
                        if dls(new_state, moves + [(piece, direction)], depth + 1):  # Recursively call DLS with increased depth
                            return True  # Return True if a solution is found
                        visited.remove(new_board_tuple)  # Remove the new state from the visited set
                return False  # Return False if no solution is found at this depth

            self.load_board(filename)  # Load the board from the file
            if dls(self, [], 0):  # Call DLS with the initial state, empty move list, and depth 0
                return  # Exit the method if a solution is found

        print("No solution found within reasonable depth")  # Print a message if no solution is found within the depth limit

    def manhattan_distance(self):  # Method to calculate the Manhattan distance heuristic
        goal_x, goal_y = None, None  # Initialize variables to store the goal position
        for y in range(self.height):  # Iterate over each row
            for x in range(self.width):  # Iterate over each column
                if self.board[y][x] == -1:  # Check if the cell is the goal
                    goal_x, goal_y = x, y  # Store the goal position
                    break  # Exit the inner loop
            if goal_x is not None:  # Check if the goal position has been found
                break  # Exit the outer loop

        if goal_x is None:  # Check if no goal position was found
            return 0  # Return 0 if no goal is present

        master_cells = self.get_piece_cells(2)  # Get the positions of the master piece
        if not master_cells:  # Check if the master piece is not found
            return float('inf')  # Return infinity if the master piece is missing

        centroid_x = sum(x for x, _ in master_cells) / len(master_cells)  # Calculate the centroid x-coordinate
        centroid_y = sum(y for _, y in master_cells) / len(master_cells)  # Calculate the centroid y-coordinate

        distance = abs(centroid_x - goal_x) + abs(centroid_y - goal_y)  # Calculate the Manhattan distance
        return distance  # Return the Manhattan distance

    def astar(self, filename):  # Method to perform A* search
        start_time = time.time()  # Record the start time
        self.load_board(filename)  # Load the board from the file
        initial_state = self.clone_state()  # Clone the initial state

        g_score = {initial_state.board_to_tuple(): 0}  # Initialize the g_score dictionary with the initial state

        counter = 0  # Initialize a counter for tie-breaking
        pq = [(initial_state.manhattan_distance(), counter, initial_state, [])]  # Initialize the priority queue with the initial state
        counter += 1  # Increment the counter

        visited = set()  # Initialize the visited set
        nodes_explored = 0  # Initialize the node counter

        while pq:  # While the priority queue is not empty
            min_idx = 0  # Initialize the index of the minimum element
            for i in range(1, len(pq)):  # Iterate over the priority queue to find the minimum element
                if pq[i][0] < pq[min_idx][0]:  # Compare f_scores
                    min_idx = i  # Update the index of the minimum element
                elif pq[i][0] == pq[min_idx][0] and pq[i][1] < pq[min_idx][1]:  # Tiebreaker using counter
                    min_idx = i  # Update the index of the minimum element

            _, _, current_state, moves = pq.pop(min_idx)  # Pop the minimum element from the priority queue
            current_tuple = current_state.board_to_tuple()  # Convert the current state to a tuple

            if current_tuple in visited:  # Check if the current state has been visited
                continue  # Skip this state

            visited.add(current_tuple)  # Mark the current state as visited
            nodes_explored += 1  # Increment the node counter

            if current_state.is_done():  # Check if the current state is the goal state
                self.print_solution(moves, current_state, nodes_explored, start_time)  # Print the solution
                return  # Exit the method

            current_g = g_score[current_tuple]  # Get the g_score of the current state

            for piece, direction in current_state.available_moves():  # Iterate over all available moves
                new_state = current_state.clone_state()  # Clone the current state
                new_state.apply_move(piece, direction)  # Apply the move
                new_state.normalize()  # Normalize the new state
                new_tuple = new_state.board_to_tuple()  # Convert the new state to a tuple

                new_g = current_g + 1  # Calculate the new g_score

                if new_tuple not in g_score or new_g < g_score[new_tuple]:  # Check if the new state has a better g_score
                    g_score[new_tuple] = new_g  # Update the g_score of the new state

                    f_score = new_g + new_state.manhattan_distance()  # Calculate the f_score

                    pq.append((f_score, counter, new_state, moves + [(piece, direction)]))  # Add the new state to the priority queue
                    counter += 1  # Increment the counter

        print("No solution found")  # Print a message if no solution is found
        return  # Exit the method

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
