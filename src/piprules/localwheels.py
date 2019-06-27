import logging
import os


LOG = logging.getLogger(__name__)


class Package(object):

    _VALID_BUILD_FILE_NAMES = {"BUILD", "BUILD.bazel"}
    _STUB_BUILD_FILE_COMMENT = (
        "# This is a generated file which may be overwritten with a custom BUILD file"
    )

    def __init__(self, directory):
        self.directory = directory

    @property
    def _default_build_file_path(self):
        return os.path.join(self.directory, "BUILD")

    def ensure_build_file_exists(self):
        if not self._does_build_file_exist():
            self._generate_stub_build_file()

    def _does_build_file_exist(self):
        return any(
            filename in self._VALID_BUILD_FILE_NAMES
            for filename in self._list_files()
        )

    def _list_files(self):
        return os.listdir(self.directory)

    def _generate_stub_build_file(self):
        LOG.info("Generating stub BUILD file for local wheels package")
        with open(self._default_build_file_path, mode="w") as build_file:
            build_file.write(self._STUB_BUILD_FILE_COMMENT)

    def purge_wheels(self, keep=None):
        if keep is None:
            keep = set()

        for filename in self._iterate_wheels():
            if filename not in keep:
                LOG.info("Removing unused local wheel %s", filename)
                os.remove(os.path.join(self.directory, filename))

    def _iterate_wheels(self):
        for filename in self._list_files():
            if filename.endswith(".whl"):
                yield filename
