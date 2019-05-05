import copy
import logging
import sys

from piprules import pipcompat, util


LOG = logging.getLogger(__name__)


def collect_and_condense(
    pip_session,
    lock_file,
    requirements_files,
    update_all=False,
    packages_to_update=None,
):
    collection = Collection()

    if not update_all:
        collection.add_from_lock_file(lock_file, packages_to_update=packages_to_update)

    for path in requirements_files:
        collection.add_from_requirements_file(path, pip_session)

    return collection.condense()


class Collection(object):

    def __init__(self, requirements=None):
        self._requirements = requirements or []

    def add(self, requirement):
        self._requirements.append(requirement)

    def add_from_lock_file(self, lock_file, packages_to_update=None):
        LOG.info("Adding requirements from lock file to collection")

        if packages_to_update is None:
            packages_to_update = []

        update_packages_canon_names = {
            pipcompat.canonicalize_name(name)
            for name in packages_to_update
        }
        if update_packages_canon_names:
            LOG.debug(
                "The following packages are being updated: %s",
                update_packages_canon_names,
            )

        for name, details in lock_file.iterate_requirements_for_current_environment():
            canon_name = pipcompat.canonicalize_name(name)

            if canon_name in update_packages_canon_names:
                LOG.debug("Package %s is being updated; not adding locked requirement")
            else:
                requirement = _create_locked_requirement(
                    name,
                    details.version,
                    details.is_direct,
                )
                LOG.debug("Adding locked requirement %s", requirement)
                self.add(requirement)

    def add_from_requirements_file(self, path, pip_session):
        LOG.info("Adding requirements from file %s to collection", path)

        for requirement in pipcompat.parse_requirements(path, session=pip_session):
            LOG.debug("Adding direct requirement %s", requirement)
            requirement.is_direct = True
            self.add(requirement)

    def condense(self):
        LOG.info("Condensing requirement collection into a set")

        condensed_set = pipcompat.RequirementSet()

        for requirement in self._generate_condensed_requirements():
            condensed_set.add_requirement(
                requirement,
                # This is required for indirect requirements, but isn't really used
                parent_req_name=(None if requirement.is_direct else "dummy"),
            )

        return condensed_set

    def _generate_condensed_requirements(self):
        for name, group in self._iterate_grouped_requirements():
            LOG.debug("Condensing requirements for '{}'".format(name))

            condensed_requirement = copy.deepcopy(next(group))

            for requirement in group:
                condensed_requirement.req.specifier &= requirement.req.specifier
                condensed_requirement.constraint &= requirement.constraint
                # Return a sorted, de-duped tuple of extras
                condensed_requirement.extras = tuple(sorted(set(
                    tuple(condensed_requirement.extras) + tuple(requirement.extras)
                )))

            LOG.debug("Condensed requirement: %s", condensed_requirement)
            yield condensed_requirement

    def _iterate_grouped_requirements(self):
        return util.full_groupby(self._requirements, key=_get_key)


def _create_locked_requirement(name, version, is_direct):
    constraint = "{}=={}".format(name, version)
    requirement = pipcompat.create_requirement_from_string(
        constraint,
        comes_from="lock file",
    )
    requirement.is_direct = is_direct
    return requirement


def _get_key(requirement):
    return pipcompat.canonicalize_name(requirement.name)
