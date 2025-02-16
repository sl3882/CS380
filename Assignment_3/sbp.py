import sys
import random
from collections import deque
import time

class Sbp:
    # ... (load_board, clone_state, is_done, get_piece_cells, print_board,
    #      compare_states, normalize, random_walk, board_to_tuple remain the same)

    def can_move(self, piece, direction):
        """Checks if a piece can move in a given direction."""
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

            if target_cell > 1 and (new_x, new_y) not in cells:  # Optimized
                return False

        return True

    def available_moves(self):
        """Gets all available moves."""
        moves = []
        pieces = sorted(set(val for row in self.board for val in row if val >= 2))
        directions = ["up", "down", "left", "right"]

        for piece in pieces:
            for direction in directions:
                if self.can_move(piece, direction):
                    moves.append((piece, direction))
        return moves

    def apply_move(self, piece, direction):
        """Applies a move to the board."""
        if not self.can_move(piece, direction):  # Check BEFORE applying
            return  # Or raise an exception

        cells = self.get_piece_cells(piece)
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]

        old_positions = {(x, y): self.board[y][x] for x, y in cells}

        for x, y in cells:
            if old_positions[(x, y)] == -1:
                continue
            self.board[y][x] = 0

        for x, y in cells:
            self.board[y + dy][x + dx] = piece

        self.normalize()

    # ... (bfs remains the same)

    def dfs(self, filename):
        """Performs a depth-first search to solve the puzzle."""
        start_time = time.time()
        self.load_board(filename)
        initial_state = self.clone_state()
        stack = [(self, [])]  # Stack of (state, moves)
        visited = {self.board_to_tuple()}  # Set of visited states
        nodes_explored = 0

        while stack:
            current_state, moves = stack.pop()
            nodes_explored += 1

            if current_state.is_done():
                end_time = time.time()
                elapsed_time = end_time - start_time

                for piece, direction in moves:
                    print(f"({piece},{direction})")
                print()

                current_state.print_board()
                print()

                print(nodes_explored)
                print(f"{elapsed_time:.2f}")
                print(len(moves))
                return

            available_moves = current_state.available_moves()

            # Prioritize (2, left) if available
            if (2, "left") in available_moves:
                available_moves.remove((2, "left"))
                available_moves.insert(0, (2, "left"))

            for piece, direction in available_moves:  # Now uses prioritized list
                new_state = current_state.clone_state()
                new_state.apply_move(piece, direction)  # apply_move now has the check
                new_state.normalize()
                new_board_tuple = new_state.board_to_tuple()

                if new_board_tuple not in visited:
                    visited.add(new_board_tuple)
                    stack.append((new_state, moves + [(piece, direction)]))

        print("No solution found")
        return

# ... (main function remains the same)

if __name__ == "__main__":
    main()