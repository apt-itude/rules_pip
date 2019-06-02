with open("test/ietf-yang-metadata-generated.yin") as yin_file:
    contents = yin_file.read()

with open("test/ietf-yang-metadata.yin") as expected_yin_file:
    expected_contents = expected_yin_file.read()

assert contents == expected_contents
