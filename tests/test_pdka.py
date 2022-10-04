from src.automaton import Automaton
from src.automaton import is_automation_equal


def read_test(number_of_test):
    first = Automaton(f"test_{number_of_test}.txt")
    first.make_min_pdka()
    second = Automaton(f"ans_test_{number_of_test}")
    return first, second


def test_with_eps_1():
    assert is_automation_equal(*read_test(1))


def test_with_eps_2():
    assert is_automation_equal(*read_test(2))


def test_word_transitions():
    assert is_automation_equal(*read_test(3))


def test_small():
    assert is_automation_equal(*read_test(4))


def test_with_wrong_ans():
    assert not is_automation_equal(*read_test(5))
