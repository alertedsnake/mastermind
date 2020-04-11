"""
The game of Mastermind.
"""

import argparse
import random
import logging
import pkg_resources
import sys
from collections import Counter

__version__ = '0.1.0-dev'
try:
    __version__ = pkg_resources.get_distribution('mastermind').version.rstrip('-')
except pkg_resources.DistributionNotFound:
    pass

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# our colors
RED     = 'r'
GREEN   = 'g'
BLUE    = 'b'
YELLOW  = 'y'
BLACK   = 'k'
WHITE   = 'w'
PURPLE  = 'p'
CYAN    = 'c'

# defaults
NUM_COLORS = 6
NUM_CHOICES = 4
ALLOWED_DUPES = 2
ATTEMPTS = 10

# all possible colors, for shufflin'
COLORS = (RED, GREEN, BLUE, YELLOW, BLACK, WHITE, PURPLE, CYAN)

# results array values
RES_MISS  = '-'  # color is not present
RES_WHITE = 'O'  # right color, wrong position
RES_BLACK = 'X'  # right color, right position
RES_WIN = RES_BLACK * NUM_CHOICES


def colorize(input):
    """Colorize output in a quick and dirty way"""

    output = ""
    for c in input:
        if c == RED:
            output += "\033[91m" + c
        elif c == GREEN:
            output += "\033[92m" + c
        elif c == BLUE:
            output += "\033[94m" + c
        elif c == WHITE or c == RES_WHITE:
            output += "\033[97m" + c
        elif c == YELLOW:
            output += "\033[93m" + c
        elif c == BLACK or c == RES_BLACK:
            output += "\033[90m" + c
        elif c == CYAN:
            output += "\033[96m" + c
        elif c == PURPLE:
            output += "\033[95m" + c
        else:
            output += "\033[95m" + c

    return output + "\033[0m"


class Mastermind:
    def __init__(self, args):
        self.args = args


    @property
    def colors(self):
        return COLORS[0:self.args.colors]


    def check_dupe(self, code, choice):
        """
        Returns true if 'choice' is in 'code' ALLOWED_DUPES times
        """
        c = Counter(code)
        return c[choice] >= self.args.duplicates


    def generate_code(self):
        """
        Generate a new code
        """

        available = list(self.colors)

        code = []
        for slot in range(0, self.args.length):
            choice = random.choice(available)

            # we have enough items to start checking dupes
            if len(code) >= self.args.duplicates:

                # remove this choice, it's already in the list too many times
                if self.check_dupe(code, choice):
                    available.remove(choice)
                    choice = random.choice(available)

            code.append(choice)

            if self.check_dupe(code, choice):
                available.remove(choice)

        return code


    def check_input(self, code, guess):
        """
        Check the user's input for matches.
        Our results array starts with all misses.  Example:
            ['-', '-', '-', '-']
        """

        result = RES_MISS * self.args.length
        result = list(result)

        # make a local copy that we can alter
        tmpcode = list(code)
        tmpguess = list(guess)

        # first pass: find right position matches
        for index, pin in enumerate(guess):

            # if this color is in the right position
            if pin == code[index]:
                result[index] = RES_BLACK
                tmpcode[index] = '-'
                tmpguess[index] = '-'

        # second pass: find wrong position matches
        for index, pin in enumerate(tmpguess):
            if pin == '-':
                continue

            # if this color is in the code anywhere else
            for i, p in enumerate(tmpcode):
                if pin == p:
                    result[index] = RES_WHITE
                    tmpcode[i] = '-'
                    break

        return result


    def validate_input(self, guess):
        """
        Validate user input
        """

        # bail out if requested
        if guess in ('quit', 'exit'):
            sys.exit()

        # check length
        if len(guess) != self.args.length:
            return f"Please enter only {self.args.length} colors."

        # check valid colors
        for letter in guess:
            if letter not in self.colors:
                return f"Invalid color: {letter}."

        # check input dupes
        for letter, count in Counter(guess).items():
            if count > self.args.duplicates:
                return f"Only {self.args.duplicates} of each color are allowed in the code."


    def game_loop(self, code):
        """
        The main game loop
        """

        attempt = 1
        while True:
            # check number of attempts
            if attempt > self.args.attempts:
                print("You lose, the code was {}.".format(colorize(''.join(code))))
                return

            guess = input(f'{attempt}: Enter {self.args.length} colors: ')
            msg = self.validate_input(guess)
            if msg:
                print(msg)
                continue

            guess = guess.lower()
            result = self.check_input(code, guess)
            log.debug(f'check result: {result}')
            random.shuffle(result)
            result = ''.join(result)

            print(f"{colorize(result)}\t{colorize(guess)}")

            # did we win?
            if result == RES_WIN:
                print(f"You won in {attempt} attempts!")
                return

            attempt += 1


    def run(self):
        """
        Run the game
        """

        print(f"""\033[H\033[J
Welcome to Mastermind!

The CodeMaker has chosen a {self.args.length} color code.
Try to break it in {self.args.attempts} guesses or less.
{self.args.duplicates} duplicates are allowed.

Available colors are: {colorize(self.colors)}
""")

        code = self.generate_code()
        log.debug(f'code: {code}')

        try:
            self.game_loop(code)
        except KeyboardInterrupt:
            return


def cli():
    parser = argparse.ArgumentParser("mastermind")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument('--duplicates', type=int, default=ALLOWED_DUPES,
                        help="Number of duplicates")
    parser.add_argument('--colors', type=int, default=NUM_COLORS,
                        help="Number of colors")
    parser.add_argument('--length', type=int, default=NUM_CHOICES,
                        help="Code length")
    parser.add_argument('--attempts', '--guesses', type=int, default=ATTEMPTS,
                        help="Number of attempts")

    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    # check arguments
    if args.colors < 3 or args.colors > len(COLORS):
        print(f"Error: --colors must be 3-{len(COLORS)}")

    Mastermind(args).run()


if __name__ == '__main__':
    cli()
