#!/usr/bin/python3
from collections import defaultdict
from collections import deque
import sys


def get_state(str):
    return str.split(',')[0]


class automaton:

    def __init__(self, path: str):
        with open(path) as f:
            self.eps_reachable = defaultdict(set)
            self.parse_doa(f)
            self.alphabet = set()
            self.start = self.parse_start(f)
            self.terminal = self.parse_terminal(f)
            self.transitions = self.parse_body(f)
            self.reachable = defaultdict(str)

    def parse_doa(self, f):
        line = f.readline().strip()
        if not line.startswith('DOA:'):
            raise Exception(f"{line} should start with 'DOA:'")

    def parse_start(self, f):
        line = f.readline().strip()
        if not line.startswith('Start:'):
            raise Exception(f"{line} should start with 'Start:'")
        return line.split()[1]

    def parse_terminal(self, f):
        line = f.readline().strip()
        if not line.startswith('Acceptance:'):
            raise Exception(f"{line} should start with 'Acceptance:'")

        line = line[len('Acceptance:'):]
        terminal = [state.strip() for state in line.split('&')]
        return terminal

    def parse_body(self, f):
        lines = [line.strip() for line in f.readlines()]
        if not lines[0] == '--BEGIN--':
            raise Exception(f"Body should start with '--BEGIN--' instead of '{lines[0]}'")
        if not lines[-1] == '--END--':
            raise Exception(f"Body should end with '--END--' instead of '{lines[-1]}'")

        lines = lines[1:]
        transitions = defaultdict(set)
        count_of_new_states = 1
        while lines:
            line = lines.pop(0)
            if line == "--END--":
                break
            elif not line.startswith('State:'):
                raise Exception(f"{line} should start with 'State:'")
            state = line.split()[1].strip()
            for i, line in enumerate(lines):
                if line.startswith('State:'):
                    break
                else:
                    if line == "--END--":
                        break
                    elif not line.startswith('->'):
                        raise Exception(f"{line}: transition should start with '->'")
                    word, to = [s.strip() for s in line.split()][1:]
                    if (word == "EPS"):
                        self.eps_reachable[f"{state}"].add(to)
                    else:
                        self.alphabet = set.union(self.alphabet, set(word))
                    if len(word) == 1 or word == 'EPS':
                        transitions[f"{state}"].add(f"{to},{word}")
                    else:
                        transitions[f"{state}"].add(f"{-count_of_new_states},{word[0]}")
                        for index in range(count_of_new_states, count_of_new_states + len(word) - 2):
                            transitions[f"{-index}"].add(f"{- index - 1},{word[index - count_of_new_states]}")
                        transitions[f"{-(count_of_new_states + len(word) - 2)}"].add(f"{to},{word[-1:]}")
                        count_of_new_states += len(word) - 1
            lines = lines[i:]
        return transitions
    def find_eps_close(self, vertions):
        reachable_vertions = vertions
        for vert in vertions:
            reachable_from_vert = self.eps_reachable[str(vert)]
            reachable_vertions = set.union(reachable_from_vert, reachable_from_vert)
        return reachable_vertions

    def extend_vertions(self, array, symbol):
        ans = set()
        for vert in array:
            for string in self.transitions[vert]:
                if string.split(',')[1] == symbol:
                    ans = set.union(ans, set(string.split(',')[0].split(":")))
        return sorted(ans)

    def to_dka(self):
        new_terminal = set()
        q = deque()
        q.append(self.start)
        new_states = []
        new_transitions = defaultdict(set)
        while len(q) != 0:
            current_array_for_symbol = q.popleft()
            set_current_array_for_symbol = set(current_array_for_symbol.split(':'))
            set_current_array_for_symbol = set.union(set_current_array_for_symbol,
                                                     self.find_eps_close(current_array_for_symbol))
            for vert in current_array_for_symbol:
                if vert in self.terminal or (vert in new_terminal):
                    new_terminal.add(current_array_for_symbol)
                    break
            for symbol in self.alphabet:
                new_curr_states = self.extend_vertions(set_current_array_for_symbol, symbol)
                new_curr_states = self.format(new_curr_states)

                if (not (new_curr_states in new_states)):
                    if new_curr_states != "":
                        q.append(new_curr_states)
                    new_states.append(self.format(set_current_array_for_symbol))
                if (new_curr_states != ""):
                    new_transitions[current_array_for_symbol].add(f"{new_curr_states},{symbol}")
        self.terminal = new_terminal
        self.transitions = new_transitions
        new_states = list(set(new_states))
        self.states = new_states

    def format(self, vert):
        vert = sorted(vert)
        ans = ""
        for elem in vert:
            ans += f"{elem}:"
        return ans[:-1]

    def print_graph(self):
        print("DOA: v1")
        print("Start: ", self.start, sep='')
        print("Acceptance:", end=" ")
        print(*self.terminal, sep=" & ")
        print("--BEGIN--")
        for transition in self.transitions:
            print(f"State: {transition}")
            for elem in self.transitions[transition]:
                other_state, symbol = elem.split(',')
                print(f"-> {symbol} {other_state}")
        print("--END--")

    def dfs(self, state):
        self.reachable[state] = "gray"
        for elem in self.transitions[state]:
            v = elem.split(',')[0]
            if self.reachable[v] == "":
                self.dfs(v)
        self.reachable[state] = "black"

    def to_pdka(self):
        for symb in self.alphabet:
            self.transitions["trash"].add(f"trash,{symb}")
        for key in self.transitions:
            alph = set()
            for mn in self.transitions[key]:
                alph.add(mn.split(',')[1])
            diff = self.alphabet - alph
            for symb in diff:
                self.transitions[key].add(f"trash,{symb}")
        self.states.append("trash")

    def to_min_pdka(self):
        self.dfs(self.start)
        table = defaultdict(dict)
        q = deque()
        reverse_transitions = defaultdict(set)
        for state in self.transitions:
            for to in self.transitions[state]:
                reverse_transitions[to].add(state)

        for state1 in self.states:
            for state2 in self.states:
                table[state1][state2] = False
                table[state2][state1] = False

        for state1 in self.states:
            for state2 in self.states:
                if (not table[state1][state2]) and ((state1 in self.terminal) != (state2 in self.terminal)):
                    table[state1][state2] = True
                    table[state2][state1] = True
                    q.append((state1, state2))

        while (len(q) != 0):
            state1, state2 = q.popleft()
            for symbol in self.alphabet:
                for to1 in reverse_transitions[f"{state1},{symbol}"]:
                    for to2 in reverse_transitions[f"{state2},{symbol}"]:
                        if (not table[to1][to2]):
                            table[to1][to2] = True
                            table[to2][to1] = True
                            q.append((to1, to2))
        count_component = 0
        new_transitions = defaultdict(set)
        new_terminal = set()
        component = defaultdict(int)

        for state1 in sorted(table):
            is_terminal = False
            if (self.reachable[state1] != "black"):
                continue
            if component[state1] == 0:
                count_component += 1
                component[state1] = count_component
            for state2 in sorted(table):
                if not table[state1][state2] and component[state2] == 0:
                    component[state2] = count_component
                    is_terminal = is_terminal or (state2 in self.terminal)

            if is_terminal:
                new_terminal.add(count_component)
        for elem in self.transitions:
            for transition in self.transitions[elem]:
                trans_state, symb = transition.split(',')
                new_transitions[component[elem]].add(f"{component[trans_state]},{symb}")
        self.start = component[self.start]
        self.transitions = new_transitions
        self.terminal = new_terminal


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: doa2graphviz file")
    else:
        a = automaton(sys.argv[1])
        a.to_dka()
        a.to_pdka()
        a.to_min_pdka()
        a.print_graph()
