import parse_input as parse_input


class Rule:
    def __init__(self, not_terminal: str, right_part):
        self.not_terminal_symbol = not_terminal
        self.right_part = right_part


class EarleyState:
    def __init__(self, rule, dot_position, left):
        self.rule = rule
        self.dot_position = dot_position
        self.left = left

    def get_right_part_of_rule(self):
        return self.rule.right_part

    def __eq__(self, other):
        return (self.dot_position == other.dot_position and self.left == other.left and self.rule.not_terminal_symbol
                == other.rule.not_terminal_symbol and self.rule.right_part == other.rule.right_part)

    def __hash__(self):
        return hash(self.rule) * hash(self.dot_position + self.left)


class CFG:
    def __init__(self, path: str):
        with open(path) as f:
            parse_input.parse_cfg(f)
            self.start = parse_input.parse_start(f)
            self.words = parse_input.parse_input_words(f)
            self.transitions, self.not_terminals_alphabet = parse_input.parse_body(f)
            self.make_new_start()

    def get_rule(self, not_terminal):
        return self.transitions[not_terminal]

    def make_new_start(self):
        self.transitions["S'"].append(Rule("S'", "S"))
        self.start = "S'"
        self.not_terminals_alphabet.add("S'")

    def initialization(self, word: str):
        list_of_states = [set() for _ in range(len(word) + 1)]
        list_of_states[0].add(EarleyState(self.get_rule(self.start)[0], 0, 0))
        return list_of_states

    def scan(self, list_of_states, num_of_state, word):
        if num_of_state == 0:
            return
        for early_item in list_of_states[num_of_state - 1]:
            if early_item.dot_position < len(early_item.get_right_part_of_rule()):
                next_symb = early_item.get_right_part_of_rule()[early_item.dot_position]
                if (not (next_symb in self.not_terminals_alphabet)) and next_symb == word[num_of_state - 1]:
                    list_of_states[num_of_state].add(
                        EarleyState(early_item.rule, early_item.dot_position + 1, early_item.left))

    def predict(self, list_of_states, num_of_state):
        old_size = len(list_of_states[num_of_state])
        for early_item in list_of_states[num_of_state].copy():
            if early_item.dot_position < len(early_item.get_right_part_of_rule()):
                next_symb = early_item.get_right_part_of_rule()[early_item.dot_position]
                if next_symb in self.not_terminals_alphabet:
                    for rule in self.get_rule(next_symb):
                        list_of_states[num_of_state].add(EarleyState(rule, 0, num_of_state))

        return old_size != len(list_of_states[num_of_state])

    def complete(self, list_of_states, num_of_state):
        old_size = len(list_of_states[num_of_state])
        for early_item in list_of_states[num_of_state].copy():
            if early_item.dot_position == len(early_item.get_right_part_of_rule()):
                for predictable_early_item in list_of_states[early_item.left]:
                    if predictable_early_item.dot_position < len(predictable_early_item.get_right_part_of_rule()) \
                            and predictable_early_item.get_right_part_of_rule()[predictable_early_item.dot_position] \
                            == early_item.rule.not_terminal_symbol:
                        list_of_states[num_of_state].add(
                            EarleyState(predictable_early_item.rule, predictable_early_item.dot_position + 1,
                                        predictable_early_item.left))
        return old_size != len(list_of_states[num_of_state])

    def is_word_in_CFG(self, word: str):
        list_of_states = self.initialization(word)
        for num_of_state in range(0, len(word) + 1):
            self.scan(list_of_states, num_of_state, word)
            first_result = True
            second_result = True
            while first_result or second_result:
                first_result = self.complete(list_of_states, num_of_state)
                second_result = self.predict(list_of_states, num_of_state)
        return EarleyState(self.get_rule(self.start)[0], 1, 0) in list_of_states[len(word)]


    def get_ans(self):
        ans = list()
        for word in self.words:
            if self.is_word_in_CFG(word):
                ans.append("YES\n")
            else:
                ans.append("NO\n")
        return ans
