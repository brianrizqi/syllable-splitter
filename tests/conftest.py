import contextlib
import io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _quiet(factory):
    # The splitters print dictionary-loading messages on construction.
    with contextlib.redirect_stdout(io.StringIO()):
        return factory()


@pytest.fixture(scope='session')
def puebi():
    from PUEBIOfficialSplitter import PUEBIOfficialSplitter
    return _quiet(PUEBIOfficialSplitter)


@pytest.fixture(scope='session')
def kbbi():
    from KBBISyllableSplitter import KBBISyllableSplitter
    return _quiet(KBBISyllableSplitter)


@pytest.fixture(scope='session')
def sylbi():
    from HybridSyllableSplitter import HybridSyllableSplitter
    return _quiet(HybridSyllableSplitter)


def joined(splitter, word, **kwargs):
    return '-'.join(splitter.split_syllables(word, **kwargs))
