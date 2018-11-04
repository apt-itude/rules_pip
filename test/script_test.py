import textwrap

import pytest


@pytest.mark.parametrize("python_version", [2, 3])
def test_output(python_version):
    path = "test/test-{}.yin".format(python_version)

    with open(path) as yin_file:
        contents = yin_file.read()

    assert contents == textwrap.dedent("""
        <?xml version="1.0" encoding="UTF-8"?>
        <module name="test"
                xmlns="urn:ietf:params:xml:ns:yang:yin:1"
                xmlns:test="urn:xml:ns:test">
          <yang-version value="1"/>
          <namespace uri="urn:xml:ns:test"/>
          <prefix value="test"/>
          <container name="test-container">
            <leaf name="test-leaf">
              <type name="string"/>
            </leaf>
          </container>
        </module>
    """).lstrip()
