with open("./test/visibility_test_pytest_six") as f:
    assert f.read().strip() == "@pip//six:six"

with open("./test/visibility_test_lib_six") as f:
    assert not f.read().strip()

