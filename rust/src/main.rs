extern crate ansi_term;
extern crate promptly;
extern crate rand;
extern crate random_choice;

use ansi_term::Colour;
use ansi_term::Style;
use ansi_term::{ANSIString, ANSIStrings};
use promptly::prompt;
use random_choice::random_choice;
use std::collections::HashMap;
use std::process;

// available colors
const RED: char = 'r';
const GREEN: char = 'g';
const BLUE: char = 'b';
const YELLOW: char = 'y';
const BLACK: char = 'k';
const WHITE: char = 'w';
const PURPLE: char = 'p';
const CYAN: char = 'c';

// settings we could allow overriding
const ALLOWED_DUPES: usize = 2;
const NUM_CHOICES: usize = 4;
const NUM_COLORS: usize = 6;
const ATTEMPTS: usize = 10;

// results output characters
const RES_MISS: char = '-'; // color is not present
const RES_WHITE: char = 'O'; // right color, wrong position
const RES_BLACK: char = 'X'; // right color, right position

static COLORS: &'static [char] = &[RED, GREEN, BLUE, YELLOW, BLACK, WHITE, PURPLE, CYAN];
static RES_WIN: &'static [char] = &['X', 'X', 'X', 'X'];

// we'll need to compare char arrays to strings, so we'll need a to_string()
trait MyToString {
    fn to_string(&self) -> String;
}

impl MyToString for [char] {
    fn to_string(&self) -> String {
        let mut s = String::with_capacity(self.len());
        for c in self {
            s.push(c.clone());
        }
        s
    }
}

// hacky way to colorize a string of our colors
fn colorize(s: String) -> String {
    let mut out: Vec<ANSIString> = Vec::new();

    for c in s.chars() {
        let cstr = format!("{}", c);
        let addstr = match c {
            RED => Colour::Fixed(9).paint(cstr),
            GREEN => Colour::Green.paint(cstr),
            BLUE => Colour::Fixed(12).paint(cstr),
            YELLOW => Colour::Yellow.paint(cstr),
            BLACK | RES_BLACK => Colour::Fixed(242).paint(cstr),
            WHITE | RES_WHITE => Colour::White.paint(cstr),
            CYAN => Colour::Fixed(14).paint(cstr),
            PURPLE | RES_MISS => Colour::Fixed(13).paint(cstr),
            _ => Style::default().paint(cstr),
        };
        out.push(addstr);
    }
    ANSIStrings(&out).to_string()
}

// pick a random character
fn pick_char() -> char {
    let weights: Vec<f64> = vec![1.0, 1.0, 1.0, 1.0, 1.0, 1.0];
    let choices = random_choice().random_choice_f64(&COLORS[0..NUM_COLORS], &weights, 1);
    *choices[0]
}

// check for duplicates
fn check_dupes(choices: Vec<char>, pick: char) -> bool {
    let mut count = 0;
    for c in choices.iter() {
        if *c == pick {
            count += 1
        }
    }
    return count >= ALLOWED_DUPES;
}

// generate our code
fn generate_code() -> Vec<char> {
    let mut out: Vec<char> = Vec::new();
    for _ in 0..NUM_CHOICES {
        let mut pin = pick_char();
        if out.len() > ALLOWED_DUPES as usize {
            while check_dupes(out.clone(), pin) {
                pin = pick_char();
            }
        }

        out.push(pin);
    }
    out
}

// calculate the frequency of the characters in the string
fn frequency(input: String) -> HashMap<char, i32> {
    let mut m: HashMap<char, i32> = HashMap::new();
    for letter in input.chars() {
        let counter = m.entry(letter).or_insert(0);
        *counter += 1;
    }
    return m;
}

// validate user input
fn validate_input(guess: String) -> String {
    if guess == "exit" || guess == "quit" {
        process::exit(0x0100);
    }

    if guess.len() != NUM_CHOICES {
        return format!("Please enter exactly {} choices", NUM_CHOICES);
    }

    // check valid colors
    let mut colors: Vec<char> = Vec::new();
    colors.extend(&COLORS[0..NUM_COLORS]);

    for letter in guess.chars() {
        if !colors.contains(&letter) {
            return format!("Invalid color: {}.", letter);
        }
    }

    // check input dupes
    for (_, count) in frequency(guess.clone()) {
        if count > ALLOWED_DUPES as i32 {
            return format!(
                "Only {} of each color are allowed in the code.",
                ALLOWED_DUPES
            );
        }
    }

    return "".to_string();
}

// check user's guess against the code
fn check_input(code: Vec<char>, guess: String) -> String {
    let mut result: Vec<char> = Vec::new();
    for _ in 0..NUM_CHOICES {
        result.push(RES_MISS);
    }

    // make a local copy that we can alter so we can
    // mark used pins as we check
    let mut tmpcode = code.clone();
    let mut tmpguess: Vec<char> = Vec::new();
    tmpguess.extend(guess.chars());

    // first pass: find right position matches
    for (index, pin) in guess.chars().enumerate() {
        // see if this color is in the right position
        if pin == code[index] {
            result[index] = RES_BLACK;
            tmpcode[index] = '-';
            tmpguess[index] = '-';
        }
    }

    // second pass: find wrong position matches
    for (index, pin) in tmpguess.iter().enumerate() {
        // skip these
        if pin == &'-' {
            continue;
        }

        // if this color is in the code anywhere else
        for (i, p) in tmpcode.iter().enumerate() {
            if pin == p {
                result[index] = RES_WHITE;
                tmpcode[i] = '-';
                break;
            }
        }
    }

    return result.into_iter().collect();
}

fn rungame() {
    // generate code
    let code = generate_code();

    // uncomment if you want to cheat
    //println!("code: {:?}", code);

    let mut attempt: usize = 1;

    while attempt <= ATTEMPTS {
        let cue = format!("{}: Enter {} colors", attempt, NUM_CHOICES);
        let mut guess: String = match prompt(cue) {
            Ok(s) => s,
            Err(_) => continue,
        };
        guess = guess.to_lowercase();

        // validate the input - a message returned here is an error
        let msg = validate_input(guess.clone());
        if msg.len() > 0 {
            println!("{}", &msg);
            continue;
        }

        // check this guess
        let result = check_input(code.clone(), guess.clone());

        // print the results together
        println!("{}\t{}", colorize(result.clone()), colorize(guess.clone()));

        // did we win?
        if result == RES_WIN.to_string() {
            println!("You won in {} attempts!", attempt);
            return;
        }

        attempt += 1;
    }

    let codestr: String = code.into_iter().collect();
    println!("You lose, the code was {}", colorize(codestr));
}

fn main() {
    let mut colorvec: Vec<char> = Vec::new();
    colorvec.extend(&COLORS[0..NUM_COLORS]);
    let colorstr: String = colorvec.into_iter().collect();

    println!(
        "\x1B[H\x1B[J
Welcome to Mastermind!

The CodeMaker has chosen a {} color code.
Try to break it in {} guesses or less.
{} duplicates are allowed.

Available colors are: {}
",
        NUM_CHOICES,
        ATTEMPTS,
        ALLOWED_DUPES,
        colorize(colorstr)
    );

    rungame();
}
