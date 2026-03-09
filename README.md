# Anki Deck Generator

Generate Anki flashcard decks on any topic using Claude AI.

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

```bash
python generate_deck.py "topic" [--count N] [--output file.apkg]
```

### Examples

```bash
# 20-card deck (default) on Python decorators
python generate_deck.py "Python decorators"

# 30-card deck on World War II, saved to a specific file
python generate_deck.py "World War II" --count 30 --output ww2.apkg

# 10-card deck on basic Spanish vocabulary
python generate_deck.py "Spanish vocabulary for beginners" --count 10
```

The output `.apkg` file can be imported directly into [Anki](https://apps.ankiweb.net/) via **File → Import**.

## How it works

1. Sends your topic to Claude Opus 4.6 (with adaptive thinking enabled)
2. Claude returns a JSON array of `{ front, back }` flashcard pairs
3. The cards are packaged into a standard Anki `.apkg` file using [genanki](https://github.com/kerrickstaley/genanki)
