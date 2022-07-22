import os
import json
import pytest
import importlib

from tests import INPUT_FILES, here, outdir

@pytest.mark.parametrize("filepath", INPUT_FILES)
def test_all_formats(filepath):
    name = filepath.name.split('.')[0]
    with open(filepath) as f_in:
        json_data = json.load(f_in)
        class_name = getattr(importlib.import_module("gadal.gadal_types.data_types"),name)
        class_name(**json_data)


