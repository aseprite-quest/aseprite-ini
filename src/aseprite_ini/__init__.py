import os
import re
from collections import UserDict
from collections.abc import Iterable

import requests


class Aseini(UserDict[str, dict[str, str]]):
    @staticmethod
    def decode(lines: Iterable[str]) -> 'Aseini':
        headers = []
        for line in lines:
            line = line.strip()
            if not line.startswith('#'):
                break
            line = line.removeprefix('#').strip()
            headers.append(line)
        ini = Aseini(headers)

        section = None
        lines_iterator = iter(lines)
        line_num = 0
        for line in lines_iterator:
            line_num += 1
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                section_name = line.removeprefix('[').removesuffix(']').strip()
                if section_name in ini:
                    section = ini[section_name]
                else:
                    section = {}
                    ini[section_name] = section
            elif '=' in line:
                if section is None:
                    print(f'[line {line_num}] Ignore: {line}')
                    continue
                tokens = line.split('=', 1)
                key = tokens[0].strip()
                tail = tokens[1].strip()
                if tail.startswith('<<<'):
                    buffer = []
                    tag = tail.removeprefix('<<<')
                    for value_line in lines_iterator:
                        line_num += 1
                        if value_line.strip() == tag:
                            break
                        buffer.append(value_line.rstrip())
                    value = '\\n'.join(buffer)
                else:
                    value = tail
                if key not in section:
                    section[key] = value
            else:
                raise AssertionError(f'[line {line_num}] Token error.')
        return ini

    @staticmethod
    def decode_str(text: str) -> 'Aseini':
        return Aseini.decode(re.split(r'\r\n|\r|\n', text))

    @staticmethod
    def load(file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> 'Aseini':
        with open(file_path, 'r', encoding='utf-8') as file:
            return Aseini.decode_str(file.read())

    @staticmethod
    def pull_strings_by_url(url: str) -> 'Aseini':
        response = requests.get(url)
        assert response.ok, url
        response.encoding = 'utf-8'
        return Aseini.decode_str(response.text)

    @staticmethod
    def pull_strings(tag_name: str, lang: str = 'en') -> 'Aseini':
        url = f'https://raw.githubusercontent.com/aseprite/aseprite/{tag_name}/data/strings/{lang}.ini'
        return Aseini.pull_strings_by_url(url)

    def __init__(self, headers: list[str] = None):
        super().__init__()
        if headers is None:
            headers = []
        self.headers = headers

    def patch(self, other: 'Aseini'):
        for section_name, other_section in other.items():
            if section_name in self:
                section = self[section_name]
            else:
                section = {}
                self[section_name] = section
            section.update(other_section)

    def fallback(self, other: 'Aseini'):
        for section_name, other_section in other.items():
            if section_name in self:
                section = self[section_name]
            else:
                section = {}
                self[section_name] = section
            for key, value in other_section.items():
                if key not in section:
                    section[key] = value

    def coverage(self, source: 'Aseini') -> tuple[int, int]:
        total = 0
        translated = 0
        for section_name, section in source.items():
            for key in section:
                total += 1
                if section_name in self and key in self[section_name]:
                    translated += 1
        return translated, total

    def encode(
            self,
            source: 'Aseini' = None,
            old_format: bool = False,
    ) -> list[str]:
        if source is None:
            source = self

        lines = []
        for header in self.headers:
            lines.append(f'# {header}')
        lines.append('')
        for section_name, source_section in source.items():
            if len(source_section) <= 0:
                continue
            lines.append(f'[{section_name}]')
            for key, source_value in source_section.items():
                if section_name in self and key in self[section_name]:
                    value = self[section_name][key]
                else:
                    key = f'# TODO # {key}'
                    value = source_value
                if '\\n' in value and old_format:
                    value = value.replace('\\n', '\n')
                    value = f'<<<END\n{value}\nEND'
                lines.append(f'{key} = {value}')
            lines.append('')
        return lines

    def encode_str(
            self,
            source: 'Aseini' = None,
            old_format: bool = False,
    ) -> str:
        return '\n'.join(self.encode(source, old_format))

    def save(
            self,
            file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            source: 'Aseini' = None,
            old_format: bool = False,
    ):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(self.encode_str(source, old_format))

    def alphabet(self) -> set[str]:
        alphabet = set()
        for section in self.values():
            for value in section.values():
                value = value.replace('\\n', '')
                alphabet.update(value)
        return alphabet

    def save_alphabet(self, file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        with open(file_path, 'w', encoding='utf-8') as file:
            alphabet = list(self.alphabet())
            alphabet.sort()
            file.write(''.join(alphabet))
