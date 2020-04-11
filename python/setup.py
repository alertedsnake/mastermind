from setuptools import setup, find_packages

setup(
    name                = 'mastermind',
    version             = '1.0.0',
    description         = 'Mastermind Game',
    url                 = 'https://en.wikipedia.org/wiki/Mastermind_(board_game)',
    author              = 'randm',
    entry_points = {
        'console_scripts': ['mastermind=mastermind:cli'],
    },
    packages            = find_packages(exclude=['tests']),
)
