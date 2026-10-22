"""Base-word splitting rules of EYD Edisi V (Keputusan Kepala Badan Bahasa
No. 0424/I/BS.00.01/2022, Bab II C), checked with the standard's own examples."""

import pytest

from conftest import joined

# Bab II C.1: pemenggalan kata pada kata dasar.
BASE_WORD_RULES = {
    '1a vowel sequence': ['bu-ah', 'ma-in', 'ni-at', 'sa-at'],
    '1b monophthong eu': ['ci-leun-cang', 'seu-da-ti', 'seu-lu-mat'],
    '1c diphthong': ['pan-dai', 'sau-da-ra', 'sur-vei', 'am-boi'],
    '1d one consonant': ['ba-pak', 'de-ngan', 'ke-nyang', 'la-wan', 'mu-ta-khir', 'mu-sya-wa-rah'],
    '1e two consonants': ['ap-ril', 'ban-tu', 'man-di', 'som-bong', 'swas-ta'],
    '1f three consonants': ['am-bruk', 'ben-trok', 'in-fra', 'ul-tra', 'in-stru-men'],
    '1g digraphs': ['ba-nyak', 'kong-res', 'makh-luk', 'masy-hur'],
}
BASE_CASES = [(rule, expected) for rule, words in BASE_WORD_RULES.items() for expected in words]

# Bab II C.2c: words with an infix are split like base words.
INFIX_WORDS = ['ge-lem-bung', 'ge-mu-ruh', 'ge-ri-gi', 'si-nam-bung', 'te-lun-juk']


@pytest.mark.parametrize('rule,expected', BASE_CASES)
def test_eyd_base_word_rules(eyd, rule, expected):
    assert joined(eyd, expected.replace('-', '')) == expected


@pytest.mark.parametrize('rule,expected', BASE_CASES)
def test_kbbi_base_word_rules(kbbi, rule, expected):
    assert joined(kbbi, expected.replace('-', '')) == expected


@pytest.mark.parametrize('expected', INFIX_WORDS)
def test_infix_words_split_like_base_words(eyd, sylbi, expected):
    word = expected.replace('-', '')
    assert joined(eyd, word) == expected
    assert joined(sylbi, word) == expected


@pytest.mark.parametrize('word,expected', [
    ('geulis', 'geu-lis'),
    ('eurih', 'eu-rih'),
    ('sadeu', 'sa-deu'),
    ('teuku', 'teu-ku'),
])
def test_eu_monophthong_kept_whole(kbbi, sylbi, word, expected):
    assert joined(kbbi, word) == expected
    assert joined(sylbi, word) == expected


@pytest.mark.parametrize('word,expected', [
    # "eu" that is not the monophthong [ə] is still split, as in KBBI.
    ('eufemisme', 'e-u-fe-mis-me'),
    ('neuron', 'ne-u-ron'),
    ('deuterium', 'de-u-te-ri-um'),
    # Prefix + u-initial root.
    ('seumur', 'se-u-mur'),
    ('keuangan', 'ke-u-ang-an'),
])
def test_non_monophthong_eu_is_split(sylbi, word, expected):
    assert joined(sylbi, word) == expected


def test_eu_monophthong_keeps_original_case(eyd):
    assert eyd.split_syllables('Teuku') == ['Teu', 'ku']


@pytest.mark.parametrize('word,expected', [
    # A diphthong before a final consonant is two vowels (EYD V 1a).
    ('laut', 'la-ut'),
    ('main', 'ma-in'),
    ('baik', 'ba-ik'),
    # Before one consonant + vowel it is kept whole (EYD V 1c).
    ('kaidah', 'kai-dah'),
    ('audit', 'au-dit'),
])
def test_diphthong_position(kbbi, word, expected):
    assert joined(kbbi, word) == expected
