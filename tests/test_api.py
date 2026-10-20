"""HTTP API, with the live KBBI lookup stubbed out so tests run offline."""

import contextlib
import io

import pytest


@pytest.fixture(scope='module')
def client():
    with contextlib.redirect_stdout(io.StringIO()):
        import app as app_module
    app_module.app.config['TESTING'] = True
    original = app_module.kbbi_scraper.get_word_info
    app_module.kbbi_scraper.get_word_info = lambda word: []
    try:
        yield app_module.app.test_client()
    finally:
        app_module.kbbi_scraper.get_word_info = original


def _split(client, text, method):
    response = client.post('/split', json={'text': text, 'method': method, 'bypass_db': True})
    assert response.status_code == 200
    return {r['word']: '-'.join(r['syllables']) for r in response.get_json()['results']}


def test_health(client):
    body = client.get('/health').get_json()
    assert body['status'] == 'ok'
    assert body['kbbi_dict_size'] >= 71000


def test_split_sylbi_offline(client):
    assert _split(client, 'menguatkan membaca', 'sylbi') == {
        'menguatkan': 'meng-ku-at-kan',
        'membaca': 'meng-ba-ca',
    }


def test_split_puebi(client):
    assert _split(client, 'membaca saudara', 'puebi') == {
        'membaca': 'mem-ba-ca',
        'saudara': 'sau-da-ra',
    }


def test_split_keeps_reduplication_as_one_token(client):
    result = _split(client, 'anak-anak', 'sylbi')
    assert list(result) == ['anak-anak']


def test_split_rejects_empty_text(client):
    response = client.post('/split', json={'text': '', 'method': 'sylbi'})
    assert response.status_code == 400
