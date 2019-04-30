import errno
import json
import logging
import os
import sys

import schematics

from piprules import util


LOG = logging.getLogger(__name__)


class Environment(schematics.models.Model):

    python_versions = schematics.types.ListType(
        schematics.types.IntType,
        default=[],
        max_size=2,
    )

    def update(self, new_environment):
        self.python_versions = _merge_lists(
            self.python_versions,
            new_environment.python_versions,
        )

    def add_current(self):
        if sys.version_info.major not in self.python_versions:
            self.python_versions.append(sys.version_info.major)


def _merge_lists(first, second):
    return list(set(first) | set(second))


class Dependency(schematics.models.Model):

    environment = schematics.types.ModelType(Environment, default=Environment)

    def update(self, new_dependency):
        self.environment.update(new_dependency.environment)


class Source(schematics.models.Model):

    is_local = schematics.types.BooleanType(
        default=False,
        serialized_name="is-local",
        deserialize_from=["is-local"],
    )
    sha256 = schematics.types.StringType(serialize_when_none=False)
    environment = schematics.types.ModelType(Environment, default=Environment)

    def update(self, new_source):
        if new_source.is_local != self.is_local:
            # TODO raise better error
            raise RuntimeError(
                "A source cannot change from remote to local or vice-versa"
            )

        # TODO warn about hash changing?
        self.sha256 = new_source.sha256
        self.environment.update(new_source.environment)


class Requirement(schematics.models.Model):

    version = schematics.types.StringType(required=True)
    is_direct = schematics.types.BooleanType(
        required=True,
        serialized_name="is-direct",
        deserialize_from=["is-direct"],
    )
    dependencies = schematics.types.DictType(
        schematics.types.ModelType(Dependency),
        default={},
    )
    sources = schematics.types.DictType(
        schematics.types.ModelType(Source),
        default={},
    )

    def get_dependency(self, name):
        return self.dependencies.setdefault(name, Dependency())

    def get_source(self, url):
        return self.sources.setdefault(url, Source())

    def update(self, new_requirement):
        version_is_changing = new_requirement.version != self.version

        self.version = new_requirement.version
        self.is_direct = new_requirement.is_direct

        if version_is_changing:
            self.dependencies = new_requirement.dependencies
            self.sources = new_requirement.sources
        else:
            _update_dict_type_recursively(
                self.dependencies,
                new_requirement.dependencies,
            )
            _update_dict_type_recursively(
                self.sources,
                new_requirement.sources,
            )


class LockFile(schematics.models.Model):

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

    def get_requirement(self, name):
        return self.requirements.setdefault(name, Requirement())

    def update(self, new_requirements):
        _update_dict_type_recursively(self.requirements, new_requirements)


def _update_dict_type_recursively(existing, new):
    for key, new_value in new.items():
        try:
            existing_value = existing[key]
        except KeyError:
            existing[key] = new_value
        else:
            existing_value.update(new_value)


def load(path, create_if_missing=True):
    try:
        return LockFile.load(path)
    except IOError as err:
        if create_if_missing and err.errno == errno.ENOENT:
            return LockFile()
        raise err
