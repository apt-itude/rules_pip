import logging

from piprules import pipcompat


LOG = logging.getLogger(__name__)


class Updater(object):

    def __init__(self, session, lock_file, requirements_files=None):
        self._session = session
        self._lock_file = lock_file
        self._requirements_files = requirements_files or []

    def update(self, resolver, all_=False, packages=None):
        if packages is None:
            packages = []

        requirements = list(self._generate_requirements(all_, packages))

        requirement_set = resolver.resolve(requirements)

        self._update_lock_file(requirement_set)

        return self._lock_file

    def _generate_requirements(self, update_all, update_packages):
        if not update_all:
            for requirement in self._generate_locked_requirements(update_packages):
                yield requirement

        for requirement in self._generate_direct_requirements():
            yield requirement

    def _generate_locked_requirements(self, update_packages):
        update_packages_canon_names = {
            pipcompat.canonicalize_name(name) for name in update_packages
        }
        for name, details in self._lock_file.requirements.items():
            canon_name = pipcompat.canonicalize_name(name)
            if canon_name not in update_packages_canon_names:
                yield _create_locked_requirement(
                    name,
                    details.version,
                    details.is_direct,
                )

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


def _create_locked_requirement(name, version, is_direct):
    constraint = "{}=={}".format(name, version)
    requirement = pipcompat.create_requirement_from_string(constraint)
    requirement.is_direct = is_direct
    return requirement
