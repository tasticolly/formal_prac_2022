#!/usr/bin/python3
from collections import defaultdict
import parse_input

class CFG:
    def __init__(self, path: str):
        with open(path) as f:
            parse_input.parse_doa(f)
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
                index = word.find(elem)
                if index != -1:
                    dp[not_terminal][index][index] = True

        for lenght in range(1, len(word)):  # len
            for j in range(0, len(word) - lenght):
                for not_terminal, list_of_symbols in self.transitions.items():
                    for split in range(0, lenght):
                        if (len(list_of_symbols) == 2 and dp[list_of_symbols[0]][j][j + split] and
                                dp[list_of_symbols[1]][j + 1 + split][j + lenght]):
                            dp[not_terminal][j][j + lenght] = True
                            break
        return dp[self.start][0][len(word) - 1]


    def get_ans(self):
        for word in self.words:
            if (self.is_word_in_CFG(word)):
                print("YES")
            else:
                print("NO")