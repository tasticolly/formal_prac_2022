#!/usr/bin/python3
from collections import defaultdict
import src.parse_input


class Automaton:
    def __init__(self, path: str):
        with open(path) as f:
            src.parse_input.parse_doa(f)
            self.start = src.parse_input.parse_start(f)
            self.terminal = src.parse_input.parse_terminal(f)
            self.transitions, self.states, self.alphabet, self.eps_reachable = src.parse_input.parse_body(f)
            self.reachable = defaultdict(str)




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
