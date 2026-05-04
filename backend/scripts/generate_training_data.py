#!/usr/bin/env python3


import csv
import random
from pathlib import Path

from training_data.depression import DEPRESSION
from training_data.anxiety import ANXIETY
from training_data.suicidal import SUICIDAL
from training_data.stress import STRESS
from training_data.bipolar import BIPOLAR
from training_data.personality_disorder import PERSONALITY_DISORDER
from training_data.normal import NORMAL

random.seed(314)

SAMPLES_PER_CLASS = 400


def sample_sentences(sentences: list[str], count: int, label: str) -> list[tuple[str, str]]:
    """Sample `count` unique sentences from the pool, cycling if needed."""
    result = []
    pool = sentences[:]
    random.shuffle(pool)
    while len(result) < count:
        if not pool:
            pool = sentences[:]
            random.shuffle(pool)
        result.append((pool.pop(), label))
    return result


def main():
    print("=" * 70)
    print("SENTI-MIND v4 Training Data Generator")
    print("=" * 70)

    categories = [
        (DEPRESSION, "Depression"),
        (ANXIETY, "Anxiety"),
        (SUICIDAL, "Suicidal"),
        (STRESS, "Stress"),
        (BIPOLAR, "Bipolar"),
        (PERSONALITY_DISORDER, "Personality disorder"),
        (NORMAL, "Normal"),
    ]

    all_data: list[tuple[str, str]] = []

    for sentences, label in categories:
        unique = len(set(sentences))
        samples = sample_sentences(sentences, SAMPLES_PER_CLASS, label)
        all_data.extend(samples)
        print(f"  {label:25s}: {len(samples)} samples (from {unique} unique sentences)")

    random.shuffle(all_data)

    output_path = Path(__file__).parent.parent / "data" / "Combined Data.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["statement", "status"])
        writer.writerows(all_data)

    total = len(all_data)
    print(f"\nTotal samples: {total} ({SAMPLES_PER_CLASS} per class x {len(categories)} classes)")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
