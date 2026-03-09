#!/usr/bin/env python3
"""Generate Anki decks using Claude AI."""

import argparse
import json
import random
import re
import sys

import anthropic
import genanki


def generate_flashcards(topic: str, count: int) -> list[dict]:
    """Use Claude to generate flashcard Q&A pairs for a given topic."""
    client = anthropic.Anthropic()

    prompt = f"""Generate {count} high-quality Anki flashcards for the topic: "{topic}"

Return a JSON array of objects, each with exactly two fields:
- "front": the question or prompt (one side of the card)
- "back": the answer or explanation (other side of the card)

Make questions specific, clear, and educational. Answers should be concise but complete.
Cover a range of difficulty levels and subtopics within "{topic}".

Return ONLY valid JSON — no markdown fences, no extra text."""

    print(f"Asking Claude to generate {count} cards...", flush=True)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=8192,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for block in stream:
            pass  # consume stream events
        response = stream.get_final_message()

    # Extract the text block
    text = next(
        (block.text for block in response.content if block.type == "text"), ""
    ).strip()

    # Strip markdown fences if Claude added them despite the instruction
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    cards = json.loads(text)
    if not isinstance(cards, list):
        raise ValueError(f"Expected a JSON array, got: {type(cards)}")

    return cards


def create_anki_deck(topic: str, cards: list[dict], output_path: str) -> None:
    """Create an Anki .apkg file from a list of {front, back} dicts."""
    model = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        "Claude Generated",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
    )

    deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), topic)

    for card in cards:
        note = genanki.Note(
            model=model,
            fields=[card["front"], card["back"]],
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_path)
    print(f"Saved {len(cards)}-card deck to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an Anki .apkg deck on any topic using Claude AI.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("topic", help="Topic for the Anki deck")
    parser.add_argument(
        "--count", type=int, default=20, help="Number of flashcards to generate"
    )
    parser.add_argument("--output", help="Output .apkg file path")
    args = parser.parse_args()

    output = args.output or f"{args.topic.replace(' ', '_')}.apkg"

    try:
        cards = generate_flashcards(args.topic, args.count)
    except json.JSONDecodeError as e:
        print(f"Error: Claude returned invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Generated {len(cards)} cards.")
    create_anki_deck(args.topic, cards, output)


if __name__ == "__main__":
    main()
