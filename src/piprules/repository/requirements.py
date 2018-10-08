import logging
import re

from piprules.common import pep425
from piprules.common.compat import pathlib


LOG = logging.getLogger(__name__)

FILENAME_REGEX = re.compile(r"requirements-(?P<tags>.+)")


class Error(Exception):

    """Base exception for the requirements module"""


def generate_filename():
    system_tag_set = pep425.TagSet.from_system_exact()
    return "requirements-{}".format(system_tag_set.compress())


def choose_file(paths):
    # TODO(): this should really pick the most appropriate file using the
    # algorithm described here: https://www.python.org/dev/peps/pep-0425/#id1
    # For now, just pick the first file that matches the current environment
    system_tag_set = pep425.TagSet.from_system_supported()

    for path in paths:
        name = pathlib.Path(path).stem
        if name == "requirements":
            # Automatically choose a file that has no tags
            return path

        filename_match = FILENAME_REGEX.match(name)
        if filename_match is None:
            LOG.error("Invalid requirements file name '{}'".format(name))
            continue

        tags = filename_match.group("tags")

        try:
            file_tag_set = pep425.CompressedTagSet.from_string(tags).expand()
        except pep425.InvalidTagString as err:
            LOG.error(err)
            continue

        if file_tag_set.intersects_with(system_tag_set):
            return path

    raise NoMatchingRequirementsError


class NoMatchingRequirementsError(Error):

    def __init__(self):
        super(NoMatchingRequirementsError, self).__init__(
            "None of the given requirements files match the current "
            "environment"
        )
