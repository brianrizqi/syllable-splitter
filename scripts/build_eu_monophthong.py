#!/usr/bin/env python3
"""Build eu_monophthong.json: words whose "eu" KBBI keeps inside one syllable.

EYD V (Keputusan Kepala Badan Bahasa No. 0424/I/BS.00.01/2022, Bab II C.1b):
"Monoftong eu tidak dipenggal" -- ci-leun-cang, seu-da-ti, seu-lu-mat. It only
applies when "eu" is pronounced [ə] (Bab I D.1), which spelling cannot predict:
KBBI keeps geu.lis and seu.da.ti together but splits e.u.fe.mis.me, de.u.te.ri.um
and ke.u.ang.an. So the rule is driven by KBBI's own syllabification: every entry
whose KBBI form keeps an "eu" within one syllable is stored with that form.

The CSV is not kept in the repo; recover it from history with:
    git show 7e20190^:kbbi_v.csv > /tmp/kbbi_v.csv

Usage:
    python3 scripts/build_eu_monophthong.py /tmp/kbbi_v.csv
"""

import argparse
import csv
import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(PROJECT_ROOT, 'eu_monophthong.json')

SYLLABIFIED_RE = re.compile(r'[a-z]+(?:\.[a-z]+)+')


def build(csv_path):
    words = {}
    with open(csv_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            word = row['key'].strip().lower()
            form = row['nama'].strip().lower()
            if 'eu' not in word or not SYLLABIFIED_RE.fullmatch(form):
                continue
            if form.replace('.', '') != word:
                continue
            syllables = form.split('.')
            if any('eu' in s for s in syllables):
                words[word] = syllables
    return words


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('csv_path', help='path to kbbi_v.csv')
    args = parser.parse_args()

    words = build(args.csv_path)
    with open(OUT_PATH, mode='w', encoding='utf-8') as f:
        json.dump(dict(sorted(words.items())), f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f"Wrote {len(words)} entries to {OUT_PATH}")


if __name__ == '__main__':
    main()
