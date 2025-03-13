import random
import sys


DEFAULT_STATE = '       | ###  -| # #  +| # ####|       '


class Action:

    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy


ACTIONS = [
    Action('UP', 0, -1),
    Action('RIGHT', +1, 0),
    Action('DOWN', 0, +1),
    Action('LEFT', -1, 0)
]


class State:

    def __init__(self, env, x, y):
        self.env = env
        self.x = x
        self.y = y

    def clone(self):
        return State(self.env, self.x, self.y)

    def is_legal(self, action):
        cell = self.env.get(self.x + action.dx, self.y + action.dy)
        return cell is not None and cell in ' +-'
    
    def legal_actions(self, actions):
        legal = []
        for action in actions:
            if self.is_legal(action):
                legal.append(action)
        return legal
    
    def reward(self):
        cell = self.env.get(self.x, self.y)
        if cell is None:
            return None
        elif cell == '+':
            return +10
        elif cell == '-':
            return -10
        else:
            return 0

    def at_end(self):
        return self.reward() != 0

    def execute(self, action):
        self.x += action.dx
        self.y += action.dy
        return self

    def __str__(self):
        tmp = self.env.get(self.x, self.y)
        self.env.put(self.x, self.y, 'A')
        s = ' ' + ('-' * self.env.x_size) + '\n'
        for y in range(self.env.y_size):
            s += '|' + ''.join(self.env.row(y)) + '|\n'
        s += ' ' + ('-' * self.env.x_size)
        self.env.put(self.x, self.y, tmp)
        return s


class Env:

    def __init__(self, string):
        self.grid = [list(line) for line in string.split('|')]
        self.x_size = len(self.grid[0])
        self.y_size = len(self.grid)

    def get(self, x, y):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            return self.grid[y][x]
        else:
            return None

    def put(self, x, y, val):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            self.grid[y][x] = val

    def row(self, y):
        return self.grid[y]

    def random_state(self):
        x = random.randrange(0, self.x_size)
        y = random.randrange(0, self.y_size)
        while self.get(x, y) != ' ':
            x = random.randrange(0, self.x_size)
            y = random.randrange(0, self.y_size)
        return State(self, x, y)


class QTable:

    def __init__(self, env, actions):
        self.env = env
        self.actions = actions
        self.q_table = {}
        # Initialize Q-values to 0 for all state-action pairs
        for y in range(env.y_size):
            for x in range(env.x_size):
                if env.get(x, y) in ' +-':  # Only for valid states
                    for action in actions:
                        self.set_q(State(env, x, y), action, 0.0)

    def get_q(self, state, action):

        key = (state.x, state.y, action.name)
        return self.q_table.get(key, 0.0)
    def get_q_row(self, state):
        return [self.get_q(state, action) for action in self.actions]

    def set_q(self, state, action, val):
        key = (state.x, state.y, action.name)
        self.q_table[key] = val

    def learn_episode(self, alpha=.10, gamma=.90):
        # with the given alpha and gamma values,
        # from a random initial state,
        # consider a random legal action, execute that action,
        # compute the reward, and update the q table for (state, action).
        # repeat until an end state is reached (thus completing the episode)
        # also print the state after each action

        # 𝑄(𝑆, 𝐴) ← (1 − 𝛼)𝑄(𝑆, 𝐴) + 𝛼[𝑅 + 𝛾max𝐴′𝑄(𝑆′, 𝐴′)]
        # 𝑅      is the        reward        after        performing        the        action        𝐴 in state        𝑆 — in other
        # words, the        reward        for the agent in state 𝑆′.The default values of 𝛼 and 𝛾 are provided in the code and can be left as is.To compute the final max part of the equation, note that it is essentially the maximum of the row of the Q-table (which can be gotten with get_q_row()) for state 𝑆′.
        #
        state = self.env.random_state()
        while not state.at_end():
            print(state)
            legal_actions = state.legal_actions(self.actions)
            action = random.choice(legal_actions)
            prev_state = state.clone()
            state.execute(action)
            reward = state.reward()
            max_next_q = max(self.get_q_row(state)) if not state.at_end() else 0
            current_q = self.get_q(prev_state, action)
            # Q(S,A) = (1-α)Q(S,A) + α[R + γ*max_a'Q(S',a')]
            new_q = (1 - alpha) * current_q + alpha * (reward + gamma * max_next_q)

            # Update the Q-table
            self.set_q(prev_state, action, new_q)

            # Print the final state
        print(state)




    def learn(self, episodes, alpha=.10, gamma=.90):
        for i in range(episodes):
            self.learn_episode(alpha, gamma)

def __str__(self):
    result = ""

    # For each action type (UP, RIGHT, DOWN, LEFT)
    for action_idx, action in enumerate(self.actions):
        # Print the action name
        result += action.name + "\n"

        # Create a grid of Q-values for this action
        action_grid = []
        for y in range(self.env.y_size):
            row = []
            for x in range(self.env.x_size):
                cell = self.env.get(x, y)
                if cell in ' +-':  # Only valid locations
                    state = State(self.env, x, y)
                    q_val = self.get_q(state, action)
                    # Display '----' if Q-value is zero, otherwise format to two decimal places
                    row.append("----" if q_val == 0.0 else f"{q_val:.2f}")
                else:
                    row.append("----")  # Invalid locations
            action_grid.append(row)

        # Print the grid
        for row in action_grid:
            result += " ".join(row) + "\n"

    return result
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        env = Env(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STATE)
        if cmd == 'learn':
            qt = QTable(env, ACTIONS)
            qt.learn(100)
            print(qt)
