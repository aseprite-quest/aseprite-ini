import os

from aseprite_ini import Aseini
from tests import assets_dir, outputs_dir


def read_str(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def test_load():
    strings_en = Aseini.load(os.path.join(assets_dir, 'en.ini'))
    assert len(strings_en.headers) == 3
    assert strings_en.headers[0] == 'Header 1'
    assert strings_en.headers[1] == 'Header 2'
    assert strings_en.headers[2] == 'Header 3'
    assert strings_en['game_mode']['title'] == 'Game Mode'
    assert strings_en['game_mode']['message'] == '<<<END\nThis is Game Mode.\nEND'


def test_fallback():
    strings_en = Aseini.load(os.path.join(assets_dir, 'en.ini'))
    strings_en.fallback(Aseini.load(os.path.join(assets_dir, 'en-old.ini')))
    assert len(strings_en.headers) == 3
    assert strings_en.headers[0] == 'Header 1'
    assert strings_en.headers[1] == 'Header 2'
    assert strings_en.headers[2] == 'Header 3'
    assert strings_en['game_mode']['title'] == 'Game Mode'
    assert strings_en['legacy_mode']['title'] == 'Legacy Mode - Old'


def test_coverage():
    strings_en = Aseini.load(os.path.join(assets_dir, 'en.ini'))
    strings_zh = Aseini.load(os.path.join(assets_dir, 'zh.ini'))
    translated, total = strings_zh.coverage(strings_en)
    assert total == 6
    assert translated == 4


def test_encode_1():
    strings_en = Aseini.load(os.path.join(assets_dir, 'en.ini'))
    text = strings_en.encode_str()
    text2 = read_str(os.path.join(assets_dir, 'en-clean.ini'))
    assert text == text2


def test_encode_2():
    strings_en = Aseini.load(os.path.join(assets_dir, 'en.ini'))
    strings_zh = Aseini.load(os.path.join(assets_dir, 'zh.ini'))
    text = strings_zh.encode_str(strings_en)
    text2 = read_str(os.path.join(assets_dir, 'zh-todo.ini'))
    assert text == text2


def test_alphabet_1():
    strings_en = Aseini.load(os.path.join(assets_dir, 'en.ini'))
    alphabet = list(strings_en.alphabet())
    alphabet.sort()
    text = ''.join(alphabet)
    assert text == ' .BGMSTadefhimorsty'


def test_alphabet_2():
    strings_zh = Aseini.load(os.path.join(assets_dir, 'zh.ini'))
    alphabet = list(strings_zh.alphabet())
    alphabet.sort()
    text = ''.join(alphabet)
    assert text == '。式戏是模池游电这'


def test_save():
    strings_en = Aseini.load(os.path.join(assets_dir, 'en.ini'))
    strings_zh = Aseini.load(os.path.join(assets_dir, 'zh.ini'))
    strings_zh.save(os.path.join(outputs_dir, 'zh.ini'), strings_en)
    strings_zh.save_alphabet(os.path.join(outputs_dir, 'zh.txt'))


def test_pull():
    Aseini.pull_strings('main')
    Aseini.pull_strings('v1.3-rc4')
    Aseini.pull_strings('v1.2.40')
