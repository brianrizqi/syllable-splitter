"""Integrity of the bundled offline data derived from KBBI."""

import json
import os

from conftest import ROOT


def _lines(name):
    with open(os.path.join(ROOT, name), encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


def test_word_list_is_clean():
    words = _lines('kbbi_words.txt')
    assert len(words) >= 71000
    assert len(set(words)) == len(words), 'duplicate entries'
    assert all(w and w == w.lower() and w == w.strip() and ' ' not in w for w in words)


def test_root_map_entries_are_well_formed():
    rows = [line.split('\t') for line in _lines('kbbi_roots.tsv')]
    assert len(rows) > 25000
    words = set(_lines('kbbi_words.txt'))
    roots_known = 0
    for row in rows:
        assert len(row) == 2
        word, roots = row
        roots = roots.split('|')
        assert all(roots) and word not in roots
        roots_known += roots[0] in words
    # Nearly every base word in the map is itself a known dictionary word.
    assert roots_known / len(rows) > 0.95


def test_eu_monophthong_list_matches_its_words():
    with open(os.path.join(ROOT, 'eu_monophthong.json'), encoding='utf-8') as f:
        entries = json.load(f)
    assert entries
    for word, syllables in entries.items():
        assert ''.join(syllables) == word
        assert any('eu' in s for s in syllables)


def test_analyzer_loads_bundled_data(sylbi):
    morphology = sylbi.morphology
    assert len(morphology.kbbi_words) >= 71000
    assert morphology.kbbi_root('menguati') == 'kuat'
    # Words with a manual override do not take a dictionary root hint.
    assert morphology.kbbi_root('mengaum') is None
