# Aseprite INI

[![Python](https://img.shields.io/badge/python-3.10-brightgreen)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/aseprite-ini)](https://pypi.org/project/aseprite-ini/)

A tool to parse [Aseprite](https://github.com/aseprite/aseprite) `.ini` format file.

This format is being used for [language translation strings](https://github.com/aseprite/aseprite/blob/main/data/strings/en.ini).

## Installation

```shell
pip install aseprite-ini
```

## Usage

```python
import os

from aseprite_ini import Aseini
from examples import assets_dir, build_dir


def main():
    strings_en = Aseini.pull_strings('main')
    strings_en.fallback(Aseini.pull_strings('v1.3.2'))
    strings_en.fallback(Aseini.pull_strings('v1.2.40'))
    strings_en.save(os.path.join(build_dir, 'en.ini'))

    strings_my = Aseini.load(os.path.join(assets_dir, 'my.ini'))
    translated, total = strings_my.coverage(strings_en)
    print(f'progress: {translated} / {total}')
    strings_my.save(os.path.join(build_dir, 'my.ini'), strings_en)
    strings_my.save_alphabet(os.path.join(build_dir, 'my.txt'))


if __name__ == '__main__':
    main()
```

## Dependencies

- [Requests](https://github.com/psf/requests)

## License

Under the [MIT license](LICENSE).
