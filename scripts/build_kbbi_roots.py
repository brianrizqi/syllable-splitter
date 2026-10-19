#!/usr/bin/env python3
"""Build kbbi_roots.tsv (derived word -> KBBI base word) from the KBBI CSV export.

The offline analyzer must know the base word ("kata dasar") of a derived form to
split it the way the live KBBI path does (menguati -> kuat -> meng-ku-at-i).
kbbi_words.txt cannot tell base and derived entries apart, so this map is built
from the `kata_dasar` column of the full KBBI export (kbbi_v.csv).

The CSV itself is not kept in the repo (146k rows); recover it from history with:
    git show 7e20190^:kbbi_v.csv > /tmp/kbbi_v.csv

Usage:
    python3 scripts/build_kbbi_roots.py /tmp/kbbi_v.csv

Output format, one entry per line:  word<TAB>root1|root2|...
Roots keep KBBI's entry order (the live path also uses the first entry). A word
that is also a base headword in KBBI (mereka "they" vs me- + reka) is omitted, so
the analyzer keeps its existing handling instead of always splitting it.
"""

import argparse
import csv
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(PROJECT_ROOT, 'kbbi_roots.tsv')

WORD_RE = re.compile(r'[a-z]+(?:-[a-z]+)*')
HOMONYM_RE = re.compile(r'\s*\(\d+\)')


def build(csv_path):
    roots = {}
    is_base = set()
    with open(csv_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            word = row['key'].strip().lower()
            if not WORD_RE.fullmatch(word):
                continue
            kata_dasar = row['kata_dasar'].strip()
            if not kata_dasar:
                is_base.add(word)
                continue
            entry = roots.setdefault(word, [])
            for part in kata_dasar.split(','):
                root = HOMONYM_RE.sub('', part).strip().lower()
                if root and root != word and root not in entry:
                    entry.append(root)
    return {w: r for w, r in roots.items() if r and w not in is_base}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('csv_path', help='path to kbbi_v.csv')
    args = parser.parse_args()

    roots = build(args.csv_path)
    with open(OUT_PATH, mode='w', encoding='utf-8') as f:
        for word in sorted(roots):
            f.write(f"{word}\t{'|'.join(roots[word])}\n")
    print(f"Wrote {len(roots)} entries to {OUT_PATH}")


if __name__ == '__main__':
    main()
