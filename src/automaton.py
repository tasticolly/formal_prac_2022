#!/usr/bin/python3
from collections import defaultdict
from collections import deque
import sys


class Automaton:
    def __init__(self, path: str):
        with open(path) as f:
            self.states = set()
            self.eps_reachable = defaultdict(set)
            self.parse_doa(f)
            self.alphabet = set()
            self.start = self.parse_start(f)
            self.terminal = self.parse_terminal(f)
            self.transitions = self.parse_body(f)
            self.reachable = defaultdict(str)

    @staticmethod
    def parse_doa(f):
        line = f.readline().strip()
        if not line.startswith('DOA:'):
            raise Exception(f"{line} should start with 'DOA:'")

    @staticmethod
    def parse_start(f):
        line = f.readline().strip()
        if not line.startswith('Start:'):
            raise Exception(f"{line} should start with 'Start:'")
        return line.split()[1]

    @staticmethod
    def parse_terminal(f):
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
            self.states.add(state)
            for i, line in enumerate(lines):
                if line.startswith('State:'):
                    break
                else:
                    if line == "--END--":
                        break
                    elif not line.startswith('->'):
                        raise Exception(f"{line}: transition should start with '->'")
                    word, to = [s.strip() for s in line.split()][1:]
                    self.states.add(to)
                    if word == "EPS":
                        self.eps_reachable[f"{state}"].add(to)
                    else:
                        self.alphabet = set.union(self.alphabet, set(word))
                    if len(word) == 1 or word == 'EPS':
                        transitions[f"{state}"].add(f"{to},{word}")
                    else:
                        transitions[f"{state}"].add(f"{-count_of_new_states},{word[0]}")
                        for index in range(count_of_new_states, count_of_new_states + len(word) - 2):
                            transitions[f"{-index}"].add(f"{- index - 1},{word[index - count_of_new_states + 1]}")
                        transitions[f"{-(count_of_new_states + len(word) - 2)}"].add(f"{to},{word[-1:]}")
                        count_of_new_states += len(word) - 1
            lines = lines[i:]
        return transitions

    def bfs_find_terminal(self, vert):
        q = deque()
        q.append(vert)
        used = defaultdict(bool)
        while len(q) != 0:
            state = q.popleft()
            used[state] = True
            for to in self.eps_reachable[vert]:
                if to in self.terminal:
                    return True
                if not used[to]:
                    q.append(to)

    def relax_eps(self):
        for vert in self.eps_reachable:
            if self.bfs_find_terminal(vert):
                self.terminal.append(vert)
            for to_EPS in self.eps_reachable[vert]:
                for to_state in self.transitions[to_EPS]:
                    to, symbol = to_state.split(",")
                    self.transitions[f"{vert}"].add(f"{to},{symbol}")
                self.transitions[vert].discard(f"{to_EPS},EPS")
        self.terminal = set(self.terminal)

    def extend_vertions(self, array, symbol):
        ans = set()
        for vert in array:
            for string in self.transitions[vert]:
                if string.split(',')[1] == symbol:
                    ans = set.union(ans, set(string.split(',')[0].split(":")))
        return sorted(ans)

    def to_dka(self):
        self.relax_eps()
        new_terminal = set()
        q = deque()
        q.append(self.start)
        new_states = []
        new_transitions = defaultdict(set)
        while len(q) != 0:
            current_array_for_symbol = q.popleft()
            set_current_array_for_symbol = set(current_array_for_symbol.split(':'))
            for symbol in self.alphabet:
                new_curr_states = self.extend_vertions(set_current_array_for_symbol, symbol)
                new_curr_states = self.format(new_curr_states)
                if new_curr_states != "" and not (new_curr_states in new_states):
                    q.append(new_curr_states)
                if new_curr_states != "":
                    new_states.append(current_array_for_symbol)
                    new_transitions[current_array_for_symbol].add(f"{new_curr_states},{symbol}")
                    for vert in set_current_array_for_symbol:
                        if vert in self.terminal or (vert in new_terminal):
                            new_terminal.add(current_array_for_symbol)
                            break
        self.terminal = new_terminal
        self.transitions = new_transitions
        self.states = set(new_states)

    @staticmethod
    def format(vert):
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
        is_exist_trash = True
        for key in self.transitions:
            alph = set()
            for mn in self.transitions[key]:
                alph.add(mn.split(',')[1])
            diff = self.alphabet - alph
            for symb in diff:
                self.transitions[key].add(f"trash,{symb}")
                is_exist_trash = False
        if not is_exist_trash:
            for symb in self.alphabet:
                self.transitions["trash"].add(f"trash,{symb}")
            self.states.add("trash")

    def expand_transitions(self):
        reverse_transitions = defaultdict(set)
        for state in self.transitions:
            for to in self.transitions[state]:
                reverse_transitions[to].add(state)
        return reverse_transitions

    def fill_table(self, reverse_transitions):
        q = deque()
        table = defaultdict(dict)
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

        while len(q) != 0:
            state1, state2 = q.popleft()
            for symbol in self.alphabet:
                for to1 in reverse_transitions[f"{state1},{symbol}"]:
                    for to2 in reverse_transitions[f"{state2},{symbol}"]:
                        if not table[to1][to2]:
                            table[to1][to2] = True
                            table[to2][to1] = True
                            q.append((to1, to2))

        return table

    def from_pdka_to_min_pdka(self):
        self.dfs(self.start)
        reverse_transitions = self.expand_transitions()
        table = self.fill_table(reverse_transitions)

        count_component = 0
        new_transitions = defaultdict(set)
        new_terminal = set()
        component = defaultdict(int)

        for state1 in sorted(table):
            is_terminal = state1 in self.terminal
            if self.reachable[state1] != "black":
                continue
            if component[state1] == 0:
                count_component += 1
                component[state1] = count_component

            for state2 in sorted(table):
                if not table[state1][state2] and component[state2] == 0:
                    component[state2] = count_component
                    is_terminal = is_terminal or (state2 in self.terminal)
            if is_terminal:
                new_terminal.add(str(count_component))
        for elem in self.transitions:
            for transition in self.transitions[elem]:
                trans_state, symb = transition.split(',')
                new_transitions[str(component[elem])].add(f"{component[trans_state]},{symb}")
        self.start = str(component[self.start])
        self.transitions = new_transitions
        self.terminal = new_terminal
        self.states = set(map(str, component.values()))

    def make_min_pdka(self):
        self.to_dka()
        self.to_pdka()
        self.from_pdka_to_min_pdka()

    def determine_state_by_transition(self, symbol, state):
        for transition in self.transitions[state]:
            to, current_symbol = transition.split(',')
            if current_symbol == symbol:
                return to


def is_automation_equal(first, second):
    q = deque()
    q.append((first.start, second.start))
    if len(first.states) != len(second.states):
        return False
    used = defaultdict(defaultdict)
    for state1 in first.states:
        for state2 in second.states:
            used[state1][state2] = False

    while len(q) != 0:
        state1, state2 = q.popleft()
        if (state1 in first.terminal) != (state2 in second.terminal):
            return False
        used[state1][state2] = True
        for symbol in first.alphabet:
            to1 = first.determine_state_by_transition(symbol, state1)
            to2 = second.determine_state_by_transition(symbol, state2)
            if not used[to1][to2]:
                q.append((to1, to2))

    return True

#
# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: doa2graphviz file")
#     else:
#         a = automaton("tests/ans_test_5")
#         a.make_min_pdka()
#         a.print_graph()
#         # b = automaton("ans_test_1")
#         # print(is_automation_equal(a, b))
#
#         # a.print_graph()
