# compassheadinglib/__init__.py
# Importing submodules to make them accessible at the package level
from .common import _Headings
from importlib.resources import files as import_files
from json import load as __json_load
import sys as __sys
import types as __types

with import_files('compassheadinglib').joinpath('compass_data.json').open('r', encoding='utf-8') as json_file:
    __raw_compass = __json_load(json_file)

#get all langs
__langs = list(__raw_compass[0]['Lang'].keys())

for __lang in __langs:
    __compass = [i['Lang'][__lang] | i for i in __raw_compass]
    __Compass = _Headings(__compass)

    __lang_ll=__lang.lower()
    
    # Create virtual submodule
    __module = __types.ModuleType(f'compassheadinglib.{__lang_ll}')
    __module.Compass = __Compass
    __sys.modules[f'compassheadinglib.{__lang_ll}'] = __module
    
    # Make English the default at package level
    if __lang == 'EN':
        Compass=__Compass