Implementations of the old Master Mind board game.

See https://en.wikipedia.org/wiki/Mastermind_(board_game)

Installation
============

Python
------

You should be able to just `pip install .` this one, it'll get you an executable
named `mastermind`.

Requires Python 3.6+, but then, so does the rest of the world these days, right?

Rust
----

Type `cargo run` in the `rust` directory.

Usage
=====

You should certainly read the rules to the game first.

Output is as follows:

| char | meaning                           |
| ---- | --------------------------------- |
| X    | right color in the right position |
| O    | right color in the wrong position |
| -    | wrong color                       |

Note that the order of the output is randomized, otherwise it'd be too easy!
