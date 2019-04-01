import logging

from piprules import pipcompat


LOG = logging.getLogger(__name__)


class Locker(object):

    def __init__(self, session, lock_file, requirements_files=None):
        self._session = session
        self._lock_file = lock_file
        self._requirements_files = requirements_files or []

    def lock(self, resolver):
        requirement_set = self._build_requirement_set()

        resolver.resolve(requirement_set)
        self._update_lock_file(requirement_set)

        return self._lock_file

    def _build_requirement_set(self):
        requirement_set = pipcompat.RequirementSet()

        for install_requirement in self._generate_locked_requirements():
            requirement_set.add_requirement(install_requirement)

        for install_requirement in self._generate_direct_requirements():
            install_requirement.is_direct = True
            requirement_set.add_requirement(install_requirement)

        return requirement_set

    def _generate_locked_requirements(self):
        for name, details in self._lock_file.requirements:
            constraint = "{}=={}".format(name, details.version)
            yield _create_requirement_from_string(constraint)

    def _generate_direct_requirements(self):
        for path in self._requirements_files:
            for requirement in self._parse_requirements_file(path):
                requirement.is_direct = True
                yield requirement

    def _parse_requirements_file(self, path):
        for requirement in pipcompat.parse_requirements(path, session=self._session):
            yield requirement

    def _update_lock_file(self, requirement_set):
        for requirement in requirement_set.requirements.values():
            LOG.debug("Updating entry in lock file for {}".format(requirement.name))

            abstract_dist = pipcompat.make_abstract_dist(requirement)
            dist = abstract_dist.dist()

            locked_requirement = self._lock_file.get_requirement(dist.project_name)
            locked_requirement.version = dist.version
            locked_requirement.is_direct = requirement.is_direct

            for dep in dist.requires():
                locked_dep = locked_requirement.get_dependency(dep.name)

            link = requirement.link
            source = locked_requirement.get_source(link.url_without_fragment)
            source.is_local = link.comes_from == "local"

            if link.hash:
                # TODO this assumes the hash is sha256
                source.sha256 = link.hash


def _create_requirement_from_string(string, comes_from=None):
    requirement = pipcompat.Requirement(string)
    return pipcompat.InstallRequirement(requirement, comes_from)
