"""Reproduce the accuracy and throughput results reported in the SylBI paper.

    pip install -r requirements-dev.txt
    python scripts/evaluate.py [--data evaluation/random10000.csv]

The data file holds a random sample of 10,000 words from the bundled dictionary
(kbbi_words.txt). Columns:
    word           the word
    type           root or derived
    expected       segmentation checked by a linguist (SylBI convention)
    kbbi_official  KBBI's own syllabification (empty for words KBBI does not list)
    sylbi_live     output recorded from SylBI with the online KBBI lookup active

All engines run offline. The live SylBI row is scored from the recorded outputs,
since the online lookup depends on KBBI at the time of the run.
"""

import argparse
import contextlib
import csv
import io
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

with contextlib.redirect_stdout(io.StringIO()):
    from EYDSplitter import EYDSplitter
    from HybridSyllableSplitter import HybridSyllableSplitter
    from KBBISyllableSplitter import KBBISyllableSplitter

try:
    import pyphen
except ImportError:
    pyphen = None


def boundaries(segmented):
    cuts, pos = set(), 0
    for part in segmented.split('-')[:-1]:
        pos += len(part)
        cuts.add(pos)
    return cuts


def score(pairs):
    """Exact-match accuracy and syllable-boundary F1 over (predicted, expected) pairs."""
    correct = tp = fp = fn = 0
    for predicted, expected in pairs:
        correct += predicted == expected
        if predicted.replace('-', '') == expected.replace('-', ''):
            p, e = boundaries(predicted), boundaries(expected)
            tp += len(p & e)
            fp += len(p - e)
            fn += len(e - p)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return len(pairs), 100.0 * correct / len(pairs), f1


def quiet(fn, word):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(word)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--data', default=os.path.join(ROOT, 'evaluation', 'random10000.csv'))
    parser.add_argument('--runs', type=int, default=3, help='timed passes per engine (median is reported)')
    args = parser.parse_args()

    with open(args.data, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    words = [r['word'] for r in rows]

    with contextlib.redirect_stdout(io.StringIO()):
        eyd, kbbi, hybrid = EYDSplitter(), KBBISyllableSplitter(), HybridSyllableSplitter()
    engines = {
        'EYD': lambda w: '-'.join(eyd.split_syllables(w)).lower(),
        'KBBI': lambda w: '-'.join(kbbi.split_syllables(w)).lower(),
        'Hybrid (SylBI)': lambda w: '-'.join(hybrid.split_syllables(w)).lower(),
    }
    if pyphen:
        hyphenator = pyphen.Pyphen(lang='id_ID', left=1, right=1)
        engines['Pyphen'] = lambda w: hyphenator.inserted(w).lower()

    # Warm up on dictionary words outside the sample, so timing excludes first-call setup.
    sample = set(words)
    with open(os.path.join(ROOT, 'kbbi_words.txt'), encoding='utf-8') as f:
        warmup = [w.strip() for w in f if w.strip() and w.strip() not in sample][::30][:2000]
    for split in engines.values():
        for w in warmup:
            quiet(split, w)

    outputs, timings = {}, {}
    for name, split in engines.items():
        passes, times = [], []
        for _ in range(args.runs):
            start = time.perf_counter()
            passes.append([quiet(split, w) for w in words])
            times.append(time.perf_counter() - start)
        outputs[name] = passes[0]
        timings[name] = (statistics.median(times), all(p == passes[0] for p in passes))

    roots = [i for i, r in enumerate(rows) if r['type'] == 'root']
    listed = [i for i, r in enumerate(rows) if r['kbbi_official']]
    n_root = len(roots)
    print(f"Sample: {len(rows)} words ({n_root} root, {len(rows) - n_root} derived); "
          f"{len(listed)} listed in KBBI\n")

    print(f"{'Engine':26s} {'Reference':18s} {'Words':>6s} {'Acc (%)':>8s} {'F1':>6s}")
    print('(a) Root words: one shared convention')
    table_a = [(name, [(outputs[name][i], rows[i]['expected']) for i in roots]) for name in engines]
    table_a.append(('Hybrid (SylBI), live', [(rows[i]['sylbi_live'], rows[i]['expected']) for i in roots]))
    for name, pairs in table_a:
        n, acc, f1 = score(pairs)
        print(f"  {name:24s} {'validated answers':18s} {n:6d} {acc:8.2f} {f1:6.3f}")
    print('(b) Root and derived words: each engine against its own convention')
    for name in engines:
        if name == 'Hybrid (SylBI)':
            continue
        n, acc, f1 = score([(outputs[name][i], rows[i]['kbbi_official']) for i in listed])
        print(f"  {name:24s} {'KBBI official':18s} {n:6d} {acc:8.2f} {f1:6.3f}")
    for name, column in (('Hybrid (SylBI), offline', None), ('Hybrid (SylBI), live', 'sylbi_live')):
        pairs = [((r[column] if column else outputs['Hybrid (SylBI)'][i]), r['expected'])
                 for i, r in enumerate(rows)]
        n, acc, f1 = score(pairs)
        print(f"  {name:24s} {'validated answers':18s} {n:6d} {acc:8.2f} {f1:6.3f}")

    print(f"\nOffline throughput (single process, median of {args.runs} passes over the sample)")
    print(f"{'Engine':26s} {'words/s':>10s} {'us/word':>9s}  deterministic")
    for name, (seconds, same) in timings.items():
        print(f"  {name:24s} {len(words) / seconds:10,.0f} {1e6 * seconds / len(words):9.1f}  {same}")

    agree = sum(outputs['EYD'][i] == outputs['KBBI'][i] for i in roots)
    affixed = 0
    for w in words:
        with contextlib.redirect_stdout(io.StringIO()):
            prefix, _, suffix, _, infix = hybrid.morphology.analyze_with_lemmatizer(
                w, root_hint=hybrid.morphology.kbbi_root(w))
        affixed += bool(prefix or suffix or infix)
    print(f"\nEYD/KBBI agreement on root words: {agree}/{n_root} = {100.0 * agree / n_root:.1f}%")
    print(f"Affix detected by the hybrid analysis: {affixed}/{len(words)} = {100.0 * affixed / len(words):.1f}%")


if __name__ == '__main__':
    main()
