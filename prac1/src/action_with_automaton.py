from collections import defaultdict
from collections import deque


def bfs_find_terminal(automaton, vert):
    q = deque()
    q.append(vert)
    used = defaultdict(bool)
    while len(q) != 0:
        state = q.popleft()
        used[state] = True
        for to in automaton.eps_reachable[vert]:
            if to in automaton.terminal:
                return True
            if not used[to]:
                q.append(to)


def relax_eps(automaton):
    for vert in automaton.eps_reachable:
        if bfs_find_terminal(automaton, vert):
            automaton.terminal.append(vert)
        for to_EPS in automaton.eps_reachable[vert]:
            for to_state in automaton.transitions[to_EPS]:
                to, symbol = to_state.split(",")
                automaton.transitions[f"{vert}"].add(f"{to},{symbol}")
            automaton.transitions[vert].discard(f"{to_EPS},EPS")
    automaton.terminal = set(automaton.terminal)


def extend_vertions(automaton, array, symbol):
    ans = set()
    for vert in array:
        for string in automaton.transitions[vert]:
            if string.split(',')[1] == symbol:
                ans = set.union(ans, set(string.split(',')[0].split(":")))
    return sorted(ans)


def to_dka(automaton):
    relax_eps(automaton)
    new_terminal = set()
    q = deque()
    q.append(automaton.start)
    new_states = []
    new_transitions = defaultdict(set)
    while len(q) != 0:
        current_array_for_symbol = q.popleft()
        set_current_array_for_symbol = set(current_array_for_symbol.split(':'))
        for symbol in automaton.alphabet:
            new_curr_states = extend_vertions(automaton, set_current_array_for_symbol, symbol)
            new_curr_states = format(new_curr_states)
            if new_curr_states != "" and not (new_curr_states in new_states):
                q.append(new_curr_states)
            if new_curr_states != "":
                new_states.append(current_array_for_symbol)
                new_transitions[current_array_for_symbol].add(f"{new_curr_states},{symbol}")
                for vert in set_current_array_for_symbol:
                    if vert in automaton.terminal or (vert in new_terminal):
                        new_terminal.add(current_array_for_symbol)
                        break
    automaton.terminal = new_terminal
    automaton.transitions = new_transitions
    automaton.states = set(new_states)


def format(vert):
    vert = sorted(vert)
    ans = ""
    for elem in vert:
        ans += f"{elem}:"
    return ans[:-1]

def dfs(automaton, state):
    automaton.reachable[state] = "gray"
    for elem in automaton.transitions[state]:
        v = elem.split(',')[0]
        if automaton.reachable[v] == "":
            dfs(automaton, v)
    automaton.reachable[state] = "black"

def to_pdka(automaton):
    is_exist_trash = True
    for key in automaton.transitions:
        alph = set()
        for mn in automaton.transitions[key]:
            alph.add(mn.split(',')[1])
        diff = automaton.alphabet - alph
        for symb in diff:
            automaton.transitions[key].add(f"trash,{symb}")
            is_exist_trash = False
    if not is_exist_trash:
        for symb in automaton.alphabet:
            automaton.transitions["trash"].add(f"trash,{symb}")
        automaton.states.add("trash")

def expand_transitions(automaton):
    reverse_transitions = defaultdict(set)
    for state in automaton.transitions:
        for to in automaton.transitions[state]:
            reverse_transitions[to].add(state)
    return reverse_transitions

def fill_table(automaton, reverse_transitions):
    q = deque()
    table = defaultdict(dict)
    for state1 in automaton.states:
        for state2 in automaton.states:
            table[state1][state2] = False
            table[state2][state1] = False

    for state1 in automaton.states:
        for state2 in automaton.states:
            if (not table[state1][state2]) and ((state1 in automaton.terminal) != (state2 in automaton.terminal)):
                table[state1][state2] = True
                table[state2][state1] = True
                q.append((state1, state2))

    while len(q) != 0:
        state1, state2 = q.popleft()
        for symbol in automaton.alphabet:
            for to1 in reverse_transitions[f"{state1},{symbol}"]:
                for to2 in reverse_transitions[f"{state2},{symbol}"]:
                    if not table[to1][to2]:
                        table[to1][to2] = True
                        table[to2][to1] = True
                        q.append((to1, to2))

    return table

def minimize_pdka(automaton):
    dfs(automaton, automaton.start)
    reverse_transitions = expand_transitions(automaton)
    table = fill_table(automaton, reverse_transitions)

    count_component = 0
    new_transitions = defaultdict(set)
    new_terminal = set()
    component = defaultdict(int)

    for state1 in sorted(table):
        is_terminal = state1 in automaton.terminal
        if automaton.reachable[state1] != "black":
            continue
        if component[state1] == 0:
            count_component += 1
            component[state1] = count_component

        for state2 in sorted(table):
            if not table[state1][state2] and component[state2] == 0:
                component[state2] = count_component
                is_terminal = is_terminal or (state2 in automaton.terminal)
        if is_terminal:
            new_terminal.add(str(count_component))
    for elem in automaton.transitions:
        for transition in automaton.transitions[elem]:
            trans_state, symb = transition.split(',')
            new_transitions[str(component[elem])].add(f"{component[trans_state]},{symb}")
    automaton.start = str(component[automaton.start])
    automaton.transitions = new_transitions
    automaton.terminal = new_terminal
    automaton.states = set(map(str, component.values()))

def make_min_pdka(automaton):
    to_dka(automaton)
    to_pdka(automaton)
    minimize_pdka(automaton)

def determine_state_by_transition(automaton, symbol, state):
    for transition in automaton.transitions[state]:
        to, current_symbol = transition.split(',')
        if current_symbol == symbol:
            return to


def are_automation_equal(first, second):
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
            to1 = determine_state_by_transition(first, symbol, state1)
            to2 = determine_state_by_transition(second, symbol, state2)
            if not used[to1][to2]:
                q.append((to1, to2))
    return True
