import errno
import json
import logging
import os
import sys

import schematics

from piprules import urlcompat, util


LOG = logging.getLogger(__name__)


class Environment(schematics.models.Model):

    sys_platform = schematics.types.StringType()
    python_version = schematics.types.IntType(choices=[2, 3])

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

    url = schematics.types.URLType()
    # TODO remove this and just use file:// URL scheme to indicate local
    is_local = schematics.types.BooleanType(
        default=False,
        serialized_name="is-local",
        deserialize_from=["is-local"],
    )
    sha256 = schematics.types.StringType(serialize_when_none=False)


class Requirement(schematics.models.Model):

    version = schematics.types.StringType(required=True)
    is_direct = schematics.types.BooleanType(
        required=True,
        serialized_name="is-direct",
        deserialize_from=["is-direct"],
    )
    source = schematics.types.DictType(
        schematics.types.StringType,
        default={},
    )
    dependencies = schematics.types.DictType(
        schematics.types.ListType(schematics.types.StringType),
        default={},
    )

    def update(self, version, is_direct, source, dependencies):
        version_is_different = version != self.version

        self.version = version
        self.is_direct = is_direct

        if version_is_different:
            # If the version is changing, remove existing sources and dependencies for
            # other environments since they no longer apply
            self.source = {
                _CURRENT_ENVIRONMENT.name: source
            }
            self.dependencies = {
                _CURRENT_ENVIRONMENT.name: dependencies
            }
        else:
            self.source[_CURRENT_ENVIRONMENT.name] = source
            self.dependencies[_CURRENT_ENVIRONMENT.name] = dependencies


class LockFile(schematics.models.Model):

    environments = schematics.types.DictType(
        schematics.types.ModelType(Environment),
        default={},
    )
    sources = schematics.types.DictType(
        schematics.types.ModelType(Source),
        default={},
    )
    requirements = schematics.types.DictType(
        schematics.types.ModelType(Requirement),
        default={},
    )

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

    def update(self, resolved_requirements):
        self.environments.setdefault(_CURRENT_ENVIRONMENT.name, _CURRENT_ENVIRONMENT)

        for resolved_requirement in resolved_requirements:
            source_name = _get_source_name(resolved_requirement.source.url)

            self.sources[source_name] = Source(dict(
                url=resolved_requirement.source.url,
                is_local=resolved_requirement.source.is_local,
                sha256=resolved_requirement.source.sha256,
            ))

            requirement = self.requirements.setdefault(
                resolved_requirement.name,
                Requirement()
            )
            requirement.update(
                version=resolved_requirement.version,
                is_direct=resolved_requirement.is_direct,
                source=source_name,
                dependencies=resolved_requirement.dependencies,
            )

    def requirement_matches_current_environment(self, requirement):
        return any(
            self.environments[environment_name].matches_current()
            for environment_name in requirement.source.keys()
        )


def _get_source_name(url):
    path_part = urlcompat.urlparse(url).path
    stem = util.get_path_stem(path_part)
    return stem.replace("-", "_").replace(".", "_")


def load(path, create_if_missing=True):
    try:
        return LockFile.load(path)
    except IOError as err:
        if create_if_missing and err.errno == errno.ENOENT:
            return LockFile()
        raise err
