import json
import logging
import os

import schematics

from piprules import util


LOG = logging.getLogger(__name__)


class Dependency(schematics.models.Model):

    pass


class Source(schematics.models.Model):

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


class LockFile(schematics.models.Model):

    requirements = schematics.types.DictType(
        schematics.types.ModelType(Requirement),
        default={},
    )

    @classmethod
    def load(cls, path):
        LOG.debug('Reading requirements lock file %s', path)

        with open(path) as lock_file:
            data = json.load(lock_file)

        return cls(data)

    @classmethod
    def from_json(cls, json_string):
        return cls(json.loads(json_string))

    def dump(self, path):
        LOG.debug('Writing requirements lock file to %s', path)

        util.ensure_directory_exists(os.path.dirname(path))

        with open(path, mode='w') as lock_file:
            json.dump(self.to_primitive(), lock_file, indent=2)

    def to_json(self):
        return json.dumps(self.to_primitive(), indent=2)

    def get_requirement(self, name):
        return self.requirements.setdefault(name, Requirement())
