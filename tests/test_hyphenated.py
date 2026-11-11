"""Hyphenated words (reduplications, Arabic article forms) reported by the tester
on 2026-11-11: the hyphen separates words and must not end up inside a syllable."""

import pytest

from conftest import joined
from KBBIScraper import parse_header_syllables

HYPHENATED = [
    ('alok-alok', 'a-lok-a-lok'),
    ('alon-alon', 'a-lon-a-lon'),
    ('anak-anak', 'a-nak-a-nak'),
    ('al-isra', 'al-is-ra'),
    ('an-nahl', 'an-nahl'),
]


@pytest.mark.parametrize('word,expected', HYPHENATED)
def test_all_engines_split_hyphenated_words(eyd, kbbi, sylbi, word, expected):
    assert joined(eyd, word).lower() == expected
    assert joined(kbbi, word) == expected
    assert joined(sylbi, word) == expected


@pytest.mark.parametrize('header,word,expected', [
    # KBBI headers seen for the reported words.
    ('a.lok-a.lok 1', 'alok-alok', ['a', 'lok', 'a', 'lok']),
    ('alon 1 » a.lon-a.lon', 'alon-alon', ['a', 'lon', 'a', 'lon']),
    ('Al-Is.ra', 'al-isra', ['al', 'is', 'ra']),
    ('Al-Is.ra', 'Al-Isra', ['Al', 'Is', 'ra']),
    # Ordinary headers are unchanged.
    ('ajar (1) » pem.bel.a.jar.an', 'pembelajaran', ['pem', 'bel', 'a', 'jar', 'an']),
    ('kuat » meng.u.at.kan', 'menguatkan', ['meng', 'u', 'at', 'kan']),
    ('ba.ca', 'baca', ['ba', 'ca']),
    ('teh', 'teh', []),
])
def test_kbbi_header_syllables(header, word, expected):
    assert parse_header_syllables(header, word) == expected
