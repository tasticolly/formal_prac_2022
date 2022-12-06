import src.parse_input as parse_input

class CFG:
    def __init__(self, path: str):
        with open(path) as f:
            parse_input.parse_cfg(f)
            self.start = parse_input.parse_start(f)
            self.words = parse_input.parse_input_words(f)
            self.transitions, self.not_terminals_alphabet, self.is_consist_empty_word = parse_input.parse_body(f)

    def is_word_in_CFG(self, word: str):
        if word == "ε":
            return self.is_consist_empty_word

        dp = dict()
        for not_terminal in self.not_terminals_alphabet:
            mas = [[False] * len(word) for i in range(len(word))]
            dp[not_terminal] = mas
            for elem in self.transitions[not_terminal]:
                for index in range(0, len(word)):
                    if elem == word[index]:
                        dp[not_terminal][index][index] = True

        for lenght in range(1, len(word)):  # len
            for j in range(0, len(word) - lenght):
                for not_terminal, list_of_symbols in self.transitions.items():
                    for elem in list_of_symbols:
                        for split in range(0, lenght):
                            if (len(elem) == 2 and dp[elem[0]][j][j + split] and
                                    dp[elem[1]][j + 1 + split][j + lenght]):
                                dp[not_terminal][j][j + lenght] = True
                                break
        return dp[self.start][0][len(word) - 1]

    def get_ans(self):
        ans = list()
        for word in self.words:
            if (self.is_word_in_CFG(word)):
                ans.append("YES\n")
            else:
                ans.append("NO\n")
        return ans
