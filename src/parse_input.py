from collections import defaultdict

def parse_doa(f):
    line = f.readline().strip()
    if not line.startswith('DOA:'):
        raise Exception(f"{line} should start with 'DOA:'")


def parse_start(f):
    line = f.readline().strip()
    if not line.startswith('Start:'):
        raise Exception(f"{line} should start with 'Start:'")
    return line.split()[1]


def parse_terminal(f):
    line = f.readline().strip()
    if not line.startswith('Acceptance:'):
        raise Exception(f"{line} should start with 'Acceptance:'")

    line = line[len('Acceptance:'):]
    terminal = [state.strip() for state in line.split('&')]
    return terminal


def parse_body(f):

    lines = [line.strip() for line in f.readlines()]
    if not lines[0] == '--BEGIN--':
        raise Exception(f"Body should start with '--BEGIN--' instead of '{lines[0]}'")
    if not lines[-1] == '--END--':
        raise Exception(f"Body should end with '--END--' instead of '{lines[-1]}'")

    transitions = defaultdict(set)
    states = set()
    eps_reachable = defaultdict(set)
    alphabet = set()

    lines = lines[1:]
    count_of_new_states = 1
    while lines:
        line = lines.pop(0)
        if line == "--END--":
            break
        elif not line.startswith('State:'):
            raise Exception(f"{line} should start with 'State:'")
        state = line.split()[1].strip()
        states.add(state)
        for i, line in enumerate(lines):
            if line.startswith('State:'):
                break
            else:
                if line == "--END--":
                    break
                elif not line.startswith('->'):
                    raise Exception(f"{line}: transition should start with '->'")
                word, to = [s.strip() for s in line.split()][1:]
                states.add(to)
                if word == "EPS":
                    eps_reachable[f"{state}"].add(to)
                else:
                    alphabet = set.union(alphabet, set(word))
                if len(word) == 1 or word == 'EPS':
                    transitions[f"{state}"].add(f"{to},{word}")
                else:
                    transitions[f"{state}"].add(f"{-count_of_new_states},{word[0]}")
                    for index in range(count_of_new_states, count_of_new_states + len(word) - 2):
                        transitions[f"{-index}"].add(f"{- index - 1},{word[index - count_of_new_states + 1]}")
                    transitions[f"{-(count_of_new_states + len(word) - 2)}"].add(f"{to},{word[-1:]}")
                    count_of_new_states += len(word) - 1
        lines = lines[i:]
    return transitions,states,alphabet,eps_reachable