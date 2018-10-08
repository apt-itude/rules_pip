import attr
from pip._internal import pep425tags


class Error(Exception):

    """Base exception for the pep425 module"""


@attr.s
class TagSet(object):

    tags = attr.ib(factory=set)

    @classmethod
    def from_system_supported(cls):
        return cls(set(pep425tags.get_supported()))

    @classmethod
    def from_system_exact(cls):
        return cls({(
            pep425tags.get_impl_tag(),
            pep425tags.get_abi_tag(),
            pep425tags.get_platform(),
        )})

    def intersects_with(self, other_tag_set):
        return bool(self.tags.intersection(other_tag_set.tags))

    def compress(self):
        python_tags = set()
        abi_tags = set()
        platform_tags = set()

        for python_tag, abi_tag, platform_tag in self.tags:
            python_tags.add(python_tag)
            abi_tags.add(abi_tag)
            platform_tags.add(platform_tag)

        return CompressedTagSet(
            python=python_tags,
            abi=abi_tags,
            platform=platform_tags,
        )


@attr.s
class CompressedTagSet(object):

    python = attr.ib(default=set)
    abi = attr.ib(default=set)
    platform = attr.ib(default=set)

    @classmethod
    def from_string(cls, string):
        try:
            python_tags, abi_tags, platform_tags = string.split("-")
        except ValueError:
            raise InvalidTagString(string)

        return cls(
            python=set(python_tags.split(".")),
            abi=set(abi_tags.split(".")),
            platform=set(platform_tags.split(".")),
        )

    def expand(self):
        return TagSet({
            (python_tag, abi_tag, platform_tag)
            for python_tag in self.python
            for abi_tag in self.abi
            for platform_tag in self.platform
        })

    def __str__(self):
        return "-".join([
            ".".join(sorted(self.python)),
            ".".join(sorted(self.abi)),
            ".".join(sorted(self.platform)),
        ])


class InvalidTagString(Exception):

    """The given tag string does not comply with PEP 425"""

    def __init__(self, string):
        super(InvalidTagString, self).__init__()
        self.string = string

    def __str__(self):
        return "Invalid compatibility tags: '{}'".format(self.string)
