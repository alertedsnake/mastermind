import mastermind


def test_good():
    assert mastermind.check_input('rgby', 'rgby') == ['X', 'X', 'X', 'X']
    assert mastermind.check_input('rgby', 'rgbw') == ['X', 'X', 'X', '-']
    assert mastermind.check_input('kgby', 'rgbw') == ['-', 'X', 'X', '-']
    assert mastermind.check_input('rgby', 'rgyb') == ['X', 'X', 'O', 'O']
    assert mastermind.check_input('rgry', 'rgry') == ['X', 'X', 'X', 'X']
    assert mastermind.check_input('rgry', 'rgrb') == ['X', 'X', 'X', '-']
    assert mastermind.check_input('rgry', 'rgbr') == ['X', 'X', '-', 'O']
    assert mastermind.check_input('rgry', 'rrww') == ['X', 'O', '-', '-']
    assert mastermind.check_input('rryy', 'rrww') == ['X', 'X', '-', '-']
    assert mastermind.check_input('ryyr', 'rryy') == ['X', 'O', 'X', 'O']


def test_should_be_right():
    assert mastermind.check_input('ryyr', 'ryyy') == ['X', 'X', 'X', '-']
    assert mastermind.check_input('rrwk', 'rwwr') == ['X', '-', 'X', 'O']
    assert mastermind.check_input('yrwr', 'rwrk') == ['O', 'O', 'O', '-']
    assert mastermind.check_input('rrwr', 'kwrw') == ['-', 'O', 'O', '-']
