"""Behaviour of the hybrid (SylBI) method: canonical prefixes, peluluhan
restoration, stacked affixes, infixes and reported regressions."""

import pytest

from conftest import joined


def test_listing_examples(sylbi):
    # The examples shown in the paper's Listing 1.
    assert sylbi.split_syllables('menguatkan') == ['meng', 'ku', 'at', 'kan']
    assert sylbi.split_syllables('membantu') == ['meng', 'ban', 'tu']
    assert sylbi.split_syllables('memontang-mantingkan', root_hint='pontang-panting') == \
        ['meng', 'pon', 'tang', 'pan', 'ting', 'kan']


@pytest.mark.parametrize('word,eyd_expected,sylbi_expected', [
    # The examples shown in the paper's table of representative outputs.
    ('membaca', 'mem-ba-ca', 'meng-ba-ca'),
    ('menguatkan', 'me-ngu-at-kan', 'meng-ku-at-kan'),
    ('memodifikasi', 'me-mo-di-fi-ka-si', 'meng-mo-di-fi-ka-si'),
    ('pembelajaran', 'pem-be-la-ja-ran', 'peng-ber-a-jar-an'),
    ('penyu', 'pe-nyu', 'pe-nyu'),
    ('terteror', 'ter-te-ror', 'ter-te-ror'),
    ('berkehidupan', 'ber-ke-hi-du-pan', 'ber-ke-hi-dup-an'),
])
def test_paper_table_examples(eyd, sylbi, word, eyd_expected, sylbi_expected):
    assert joined(eyd, word) == eyd_expected
    assert joined(sylbi, word) == sylbi_expected


# Derived words reported by the tester (2026-10-14), split around their KBBI base word.
REPORTED_DERIVED = {
    'menguati': 'meng-ku-at-i',
    'mentraktor': 'meng-trak-tor',
    'mengonstatasi': 'meng-kon-sta-ta-si',
    'menyeni': 'meng-se-ni',
    'menyerepi': 'meng-se-rep-i',
    'menyokom': 'meng-so-kom',
    'menengkurapkan': 'meng-teng-ku-rap-kan',
    'mengudung': 'meng-ku-dung',
    'mengamuskan': 'meng-ka-mus-kan',
    'menepung': 'meng-te-pung',
    'memurukkan': 'meng-pu-ruk-kan',
    'memidana': 'meng-pi-da-na',
    'menarifkan': 'meng-ta-rif-kan',
    'memotori': 'meng-mo-tor-i',
    'menyelenggara': 'meng-se-leng-ga-ra',
    'memakankan': 'meng-ma-kan-kan',
    'meramping': 'meng-ram-ping',
    'menyampuk': 'meng-sam-puk',
    'menyetem': 'meng-se-tem',
    'menyertifikatkan': 'meng-ser-ti-fi-kat-kan',
    'menengoki': 'meng-te-ngok-i',
    'merecup': 'meng-re-cup',
    'menganvaskan': 'meng-kan-vas-kan',
    'menyigi': 'meng-si-gi',
    'mengerakali': 'meng-ke-ra-kal-i',
    'menyulangkan': 'meng-su-lang-kan',
    'menatih': 'meng-ta-tih',
    'menguahi': 'meng-ku-ah-i',
    'menekik': 'meng-te-kik',
    'menimbunkan': 'meng-tim-bun-kan',
    'menyetup': 'meng-se-tup',
    'menyauh': 'meng-sa-uh',
    'mengebut': 'meng-ke-but',
    'memeka': 'meng-pe-ka',
    'mengepalakan': 'meng-ke-pa-la-kan',
    'mengejikan': 'meng-ke-ji-kan',
    'memeruk': 'meng-pe-ruk',
    'merumuk': 'meng-ru-muk',
    'mengubrakan': 'meng-kub-ra-kan',
    'mengejawantahkan': 'meng-e-ja-wan-tah-kan',
    'mengempit': 'meng-kem-pit',
    'menyubsider': 'meng-sub-si-der',
    'mengalihwahanakan': 'meng-a-lih-wa-ha-na-kan',
    'menasikhkan': 'meng-na-sikh-kan',
    'menyerasikan': 'meng-se-ra-si-kan',
}


@pytest.mark.parametrize('word,expected', sorted(REPORTED_DERIVED.items()))
def test_reported_derived_words(sylbi, word, expected):
    assert joined(sylbi, word) == expected


@pytest.mark.parametrize('word,expected', [
    # Base words that only look affixed stay whole.
    ('mengerawan', 'me-nge-ra-wan'),
    ('mereka', 'me-re-ka'),
    ('meurah', 'meu-rah'),
    ('meander', 'me-an-der'),
    ('pencet', 'pen-cet'),
    ('meja', 'me-ja'),
    # Stacked affixes keep every morpheme.
    ('memberdayakan', 'meng-ber-da-ya-kan'),
    ('memerhatikan', 'meng-per-ha-ti-kan'),
    ('ketidakadilan', 'ke-ti-da-ka-dil-an'),
    # Dwipurwa reduplication is not the ter-/ber-/peng- prefix.
    ('tetua', 'te-tu-a'),
    ('beberapa', 'be-be-ra-pa'),
    ('pepatah', 'pe-pa-tah'),
])
def test_regressions(sylbi, word, expected):
    assert joined(sylbi, word) == expected


@pytest.mark.parametrize('word,expected', [
    # Infixes are shown (research convention); telunjuk is split as a base word.
    ('kelupas', 'ku-el-pas'),
    ('temurun', 'tu-em-run'),
    ('kinerja', 'ker-in-ja'),
    ('telunjuk', 'te-lun-juk'),
])
def test_infix_display(sylbi, word, expected):
    assert joined(sylbi, word) == expected


def test_output_is_deterministic(sylbi):
    words = list(REPORTED_DERIVED) + ['pembelajaran', 'berkehidupan', 'membaca']
    first = [sylbi.split_syllables(w) for w in words]
    assert [sylbi.split_syllables(w) for w in words] == first
