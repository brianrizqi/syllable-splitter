#!/usr/bin/env python3
"""Refresh the offline KBBI disambiguation dictionary (kbbi_words.txt).

The morphological analyzer needs a fast local set of known words to decide whether a
word is a base word or an affixed form. The live KBBI website stays the source of
truth for *new* words (it is queried first at request time), but the offline analyzer
also needs that vocabulary so its fallback stays correct without one HTTP call per
candidate root.

This script keeps the local list fresh by MERGING in words gathered from cheap,
already-available sources -- no full 70k+ re-scrape required:

  * the self-learning cache (words confirmed via live KBBI lookups at runtime)
  * the human validation database (words people have validated in the app)
  * an optional plain-text seed file passed with --seed (one word per line); with
    --verify each seed word is checked against live KBBI before being added.

Usage:
    python3 scripts/refresh_kbbi_words.py                 # merge cache + validation DB
    python3 scripts/refresh_kbbi_words.py --seed new.txt  # also merge a word list
    python3 scripts/refresh_kbbi_words.py --seed new.txt --verify   # verify seeds vs KBBI
    python3 scripts/refresh_kbbi_words.py --dry-run       # show what would change only
"""

import argparse
import os
import sys
import time

# Allow running from anywhere: make the project root importable.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

WORDS_PATH = os.path.join(PROJECT_ROOT, 'kbbi_words.txt')


def _norm(word):
    """Normalise a word for the dictionary: lowercase, trimmed, letters only."""
    if not word:
        return None
    w = word.strip().lower()
    return w if w and w.isalpha() else None


def load_existing():
    words = set()
    if os.path.exists(WORDS_PATH):
        with open(WORDS_PATH, mode='r', encoding='utf-8') as f:
            for line in f:
                w = _norm(line)
                if w:
                    words.add(w)
    return words


def from_learned_cache():
    try:
        from MorphologicalAnalyzer import load_learned_words
        return {w for w in (_norm(x) for x in load_learned_words()) if w}
    except Exception as e:
        print(f"  (skip learned cache: {e})")
        return set()


def from_validation_db():
    try:
        from SyllableValidationDB import SyllableValidationDB
        db = SyllableValidationDB()
        records = db.export_database() or []
        return {w for w in (_norm(r.get('word')) for r in records) if w}
    except Exception as e:
        print(f"  (skip validation DB: {e})")
        return set()


def from_seed(path, verify):
    words = set()
    if not path:
        return words
    with open(path, mode='r', encoding='utf-8') as f:
        seeds = [w for w in (_norm(x) for x in f) if w]
    if not verify:
        return set(seeds)
    # Verify each seed against live KBBI before trusting it.
    from KBBIScraper import KBBIScraper
    scraper = KBBIScraper()
    for w in seeds:
        try:
            if scraper.get_word_info(w):
                words.add(w)
                print(f"  ✓ verified: {w}")
            else:
                print(f"  ✗ not in KBBI: {w}")
            time.sleep(0.15)  # polite rate limiting
        except Exception as e:
            print(f"  ! error verifying {w}: {e}")
    return words


def main():
    parser = argparse.ArgumentParser(description="Refresh offline KBBI word list.")
    parser.add_argument('--seed', help="Optional plain-text word list to merge (one per line).")
    parser.add_argument('--verify', action='store_true',
                        help="Verify --seed words against live KBBI before adding.")
    parser.add_argument('--dry-run', action='store_true',
                        help="Report what would change without writing the file.")
    args = parser.parse_args()

    existing = load_existing()
    print(f"Existing words: {len(existing)}")

    additions = set()
    print("Gathering from self-learning cache...")
    additions |= from_learned_cache()
    print("Gathering from validation database...")
    additions |= from_validation_db()
    if args.seed:
        print(f"Gathering from seed file {args.seed} (verify={args.verify})...")
        additions |= from_seed(args.seed, args.verify)

    new_words = additions - existing
    print(f"\nNew words to add: {len(new_words)}")
    if new_words:
        preview = sorted(new_words)
        print("  " + ", ".join(preview[:30]) + (" ..." if len(preview) > 30 else ""))

    if args.dry_run:
        print("\n(dry run — nothing written)")
        return

    if not new_words:
        print("\nNothing to add; kbbi_words.txt is already up to date.")
        return

    merged = sorted(existing | new_words)
    with open(WORDS_PATH, mode='w', encoding='utf-8') as f:
        f.write("\n".join(merged) + "\n")
    print(f"\nWrote {len(merged)} words to {WORDS_PATH} (+{len(new_words)}).")


if __name__ == '__main__':
    main()
