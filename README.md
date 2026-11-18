# Tarot (1983) — Python port

A command-line port of **Tarot**, a 1983 cassette program for the Timex Sinclair 1000 (the US version of the Sinclair ZX81). The title screen credits it as "(C)1983 COMPUTER PHOOD"; the archive's file names list it as a Timex release.

The original cassette was downloaded from the Timex Sinclair archive:
<https://www.timexsinclair.com/product/tarot-2/index.html>

## The original

Side A of the tape holds two separate Sinclair BASIC programs:

| Program   | What it does |
|-----------|--------------|
| `CARDS`   | A reference to the deck. You pick the Major Arcana or one of the four suits (Wands, Cups, Swords, Pentacles) and step through each card's picture and meaning. |
| `READING` | A fortune-telling program. You type in a question, it deals 11 random cards into a Celtic-Cross-style layout, you turn them over one at a time, and then it explains each position (*signifies you*, *in opposition*, *final outcome*, …). |

On the real machine you loaded one program from tape, and each told you to `LOAD` the other when you were done.

### About the files

The original tape files aren't included in this repository. Download them from the archive link above. The download unpacks to a folder named `Tarot (1983)(Timex)(US)(TS1000)(Cassette)/` (ignored by git), which contains:

- `cards.p`, `reading.p`: **ZX81 `.p` files**. Each is a byte-for-byte image of the ZX81's memory from the system variables at `0x4009` through the end of the BASIC program and variables. This is what the machine saved to tape, minus the audio encoding. (The Unix `file` command wrongly reports them as "TTComp archive data".)
- `Tarot.txt`: the archiver's note describing the two tracks on side A.

Both programs are pure BASIC with no machine code, so they could be decoded and ported directly. The card text, block-graphic card pictures and screen layouts in `tarot.py` were pulled straight from the bytes of the `.p` files, not retyped.

## Running it

You need Python 3.7 or newer. There are no other dependencies.

```sh
python3 tarot.py            # menu: browse the cards, get a reading, or quit
python3 tarot.py cards      # the CARDS program
python3 tarot.py reading    # the READING program
python3 tarot.py gallery    # print every card's screen in order, no prompts
```

### Controls

- Press **C** to continue and **T** to turn over a card, as in the original. **Enter** also works for both.
- Menus take a number followed by Enter.
- At the end of a reading, press **N** for a new reading or any other key to finish.
- **Ctrl-C** quits from anywhere.

For the best results use a terminal at least 36 columns × 24 rows, with a font that includes Unicode block characters (`▛ ▜ ▙ ▟ ▀ ▄ ▌ ▐ █ ▒`). Most modern terminal fonts do.

### Gallery

`gallery` prints all 22 Major Arcana screens, then each suit's picture followed by its 14 meanings. You can page through it or save it to a file:

```sh
python3 tarot.py gallery | less -R
python3 tarot.py gallery > cards.txt
```

In a terminal, characters that were inverse video on the ZX81 show in reverse video. Output sent to a file or pipe is plain text. `cards.txt` in this folder is a saved copy.

## How the port works

`tarot.py` emulates the ZX81's 32×22 text screen, including how `PRINT`, `PRINT AT`, `TAB` and 32-column line wrapping behave. Each BASIC screen is redrawn the same way the original drew it. That's why the suit screens update just the card number and meaning in place, and the reading drops each card into its slot on the layout.

Inverse-video characters are marked as `{…}` in the data strings and drawn with the terminal's reverse video.

### Differences from the original

- **Keys:** Enter works wherever the original needed **C** or **T**, and Ctrl-C quits.
- **Exiting:** "End program" and the "LOAD the other tape" messages return you to the menu.
- **New reading:** the original gave you about a second to press **N** for another reading. The port waits for you.
- **Card numbers:** two Major Arcana cards were mislabelled in the original ("3-THE HIGH PRIESTESS", "4-THE EMPRESS"). They're corrected to 2 and 3. Everything else, including spelling like "OF THE SWORD-", is unchanged.
- **Graphics:** the ZX81 has four half-shaded block characters with no exact Unicode equivalent. They're drawn with the nearest matches (`▂ ▔ ▀ ▄`). The fully shaded checkerboard uses `▒`, or `▓` when it's in inverse video.

## Playing the real thing

To run the original programs unchanged, download the tape files from the archive and load `cards.p` or `reading.p` in a ZX81 emulator such as [EightyOne](https://sourceforge.net/projects/eightyone-sinclair-emulator/) (Windows) or sz81 (Linux/macOS, built from source).
