import os

import pytest

import archive_loader

testdata_path = os.path.join(os.path.dirname(__file__), "data")


@pytest.mark.files
def test_open(fname):
    pass
