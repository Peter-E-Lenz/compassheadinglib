from .common import _Headings

import importlib.resources
from json import load

with importlib.resources.open_text('compassheadinglib', 'compass_data.json') as json_file:
    raw_compass=load(json_file)

_lang='FR'

_compass=[i['Lang'][_lang] | i for i in raw_compass]

Compass = _Headings(_compass)