from collections import defaultdict


def parse_doa(f):
    line = f.readline().strip()
    if not line.startswith('CFG:'):
        raise Exception(f"{line} should start with 'CFG:'")


def parse_start(f):
    line = f.readline().strip()
    if not line.startswith('Start:'):
        raise Exception(f"{line} should start with 'Start:'")
    return line.split()[1]


def parse_input_words(f):
    line = f.readline().strip()
    if not line.startswith('Words:'):
        raise Exception(f"{line} should start with 'Words:'")
    line = line[len('Words:'):]
    words = [word.strip() for word in line.split('&')]
    return words


def parse_body(f):
    lines = [line.strip() for line in f.readlines()]
    if not lines[0] == '--BEGIN--':
        raise Exception(f"Body should start with '--BEGIN--' instead of '{lines[0]}'")
    if not lines[-1] == '--END--':
        raise Exception(f"Body should end with '--END--' instead of '{lines[-1]}'")

    transitions = defaultdict(list)
    alphabet_not_terminal = set()
    is_empty_word = False
    lines = lines[1:]
    for line in lines:
        if line == '--END--':
            break
        elif not line.startswith('->'):
            raise Exception(f"{line}: transition should start with '->'")
        not_term, to = [s.strip() for s in line.split()][1:]
        alphabet_not_terminal.add(not_term)
        if to == "ε":
            is_empty_word = True
        else:
            for symbol in to:
                transitions[not_term].append(to)

    return transitions, alphabet_not_terminal, is_empty_word
