"""
This test ensures that Python distributions not published as wheels, like
pyyaml, will be imported correctly.
"""

import yaml


DATA = {
    "ghosts": [
        "inky",
        "pinky",
        "blinky",
        "sue",
    ]
}


def test_yaml():
    yaml_str = yaml.dump(DATA)
    assert yaml.load(yaml_str) == DATA
