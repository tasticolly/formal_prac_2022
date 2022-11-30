from src.automaton import Automaton
from src.action_with_automaton import are_automation_equal
from src.action_with_automaton import make_min_pdka

def read_test(number_of_test):
    first = Automaton(f"test_{number_of_test}.txt")
    make_min_pdka(first)
    second = Automaton(f"ans_test_{number_of_test}")
    return first, second


def test_with_eps_1():
    assert are_automation_equal(*read_test(1))


def test_with_eps_2():
    assert are_automation_equal(*read_test(2))


def test_word_transitions():
    assert are_automation_equal(*read_test(3))


def test_small():
    assert are_automation_equal(*read_test(4))


def test_with_wrong_ans():
    assert not are_automation_equal(*read_test(5))

def test_differnt_lenght():
    assert not are_automation_equal(*read_test(6))
