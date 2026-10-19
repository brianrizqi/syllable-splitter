# Monoftong eu (EYD V, Bab II C.1b): "eu" pronounced [ə] is not split
# (ci-leun-cang, seu-da-ti). Whether a given "eu" is that monophthong cannot be
# read from spelling (KBBI: geu.lis but e.u.fe.mis.me, ke.u.ang.an), so the rule
# follows KBBI's syllabification, stored in eu_monophthong.json
# (built by scripts/build_eu_monophthong.py).

import json
import os


def _load():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eu_monophthong.json')
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        print("⚠ Warning: Could not load eu_monophthong.json; eu monophthong rule disabled.")
        return {}


EU_MONOPHTHONG = _load()


def eu_syllables(word):
    """Return the syllables of `word` with its eu monophthong kept whole, or None
    when the word is not listed. The original casing of `word` is preserved."""
    if not word:
        return None
    syllables = EU_MONOPHTHONG.get(word.lower())
    if not syllables:
        return None
    result, pos = [], 0
    for s in syllables:
        result.append(word[pos:pos + len(s)])
        pos += len(s)
    return result
