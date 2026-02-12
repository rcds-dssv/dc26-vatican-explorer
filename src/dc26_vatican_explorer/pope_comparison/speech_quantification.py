"""
Something or other here
"""

# imports
from dataclasses import dataclass

# classes

# Define classes we'll be working with

# TODO:
# - individual BibleRef (per verse) vs span (multiple verses)?


@dataclass
class BibleRef:
    book: str
    chapter: int
    verse: int
    bible_translation: str
    text: str


@dataclass
class PopeSpeech:
    text: str
    bible_references: list[BibleRef]


# functions


def main():
    return


if __name__ == "__main__":
    main()
