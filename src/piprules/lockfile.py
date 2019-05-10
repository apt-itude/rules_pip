import errno
import json
import logging
import os
import sys

import schematics

from piprules import util


LOG = logging.getLogger(__name__)


class Requirement(schematics.models.Model):

    version = schematics.types.StringType(required=True)
    is_direct = schematics.types.BooleanType(
        required=True,
        serialized_name="is-direct",
        deserialize_from=["is-direct"],
    )
    source = schematics.types.StringType(required=True)
    dependencies = schematics.types.ListType(
        schematics.types.StringType,
        default=[],
    )


class Environment(schematics.models.Model):

    sys_platform = schematics.types.StringType()
    python_version = schematics.types.IntType(choices=[2, 3])
    requirements = schematics.types.DictType(
        schematics.types.ModelType(Requirement),
        default={},
    )

    @classmethod
    def from_current(cls):
        environment = cls()
        environment.set_to_current()
        return environment

    @property
    def name(self):
        return "{sys_platform}_py{python_version}".format(**self.to_primitive())

    def set_to_current(self):
        self.sys_platform = sys.platform
        self.python_version = sys.version_info.major

    def matches_current(self):
        return self == _CURRENT_ENVIRONMENT

    def __eq__(self, other):
        return (
            self.sys_platform == other.sys_platform and
            self.python_version == other.python_version
        )

    def __hash__(self):
        return hash((
            self.sys_platform,
            self.python_version,
        ))


_CURRENT_ENVIRONMENT = Environment.from_current()


class Source(schematics.models.Model):

    # TODO validate that at least one of these two is set
    url = schematics.types.URLType(serialize_when_none=False)
    file = schematics.types.StringType(serialize_when_none=False)
    sha256 = schematics.types.StringType(serialize_when_none=False)


class LockFile(schematics.models.Model):

    environments = schematics.types.DictType(
        schematics.types.ModelType(Environment),
        default={},
    )
    sources = schematics.types.DictType(
        schematics.types.ModelType(Source),
        default={},
    )
    local_wheels_package = schematics.types.StringType()

    @classmethod
    def load(cls, path):
        LOG.debug('Reading requirements lock file %s', path)

        with open(path) as lock_file:
            json_string = lock_file.read()

        return cls.from_json(json_string)

    @classmethod
    def from_json(cls, json_string):
        return cls(json.loads(json_string))

    def dump(self, path):
        LOG.debug('Writing requirements lock file to %s', path)

        util.ensure_directory_exists(os.path.dirname(path))

        json_string = self.to_json()

        with open(path, mode='w') as lock_file:
            lock_file.write(json_string)

    def to_json(self):
        return json.dumps(self.to_primitive(), indent=2, sort_keys=True)

    def update_requirements_for_current_environment(self, resolved_requirements):
        new_requirements = {}

        for resolved_requirement in resolved_requirements:
            resolved_source = resolved_requirement.source
            source_name = resolved_source.get_name()

            # TODO raise error if source exists and is different
            if resolved_source.is_local():
                self.sources[source_name] = Source(dict(
                    file=resolved_source.get_file_name(),
                ))
            else:
                self.sources[source_name] = Source(dict(
                    url=resolved_source.url,
                    sha256=resolved_source.sha256,
                ))

            new_requirements[resolved_requirement.name] = Requirement(dict(
                version=resolved_requirement.version,
                is_direct=resolved_requirement.is_direct,
                source=source_name,
                dependencies=resolved_requirement.dependencies,
            ))

        self._get_or_create_current_environment().requirements = new_requirements

    def _get_or_create_current_environment(self):
        return self.environments.setdefault(
            _CURRENT_ENVIRONMENT.name,
            _CURRENT_ENVIRONMENT
        )

    def get_requirements_for_current_environment(self):
        return self._get_or_create_current_environment().requirements


def load(path, create_if_missing=True):
    try:
        return LockFile.load(path)
    except IOError as err:
        if create_if_missing and err.errno == errno.ENOENT:
            return LockFile()
        raise err
