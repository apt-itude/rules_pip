import copy
import logging

from piprules import pipcompat, util


LOG = logging.getLogger(__name__)


def condense_requirements(requirements):
    condensed_set = pipcompat.RequirementSet()
    for requirement in _generate_condensed_requirements(requirements):
        condensed_set.add_requirement(
            requirement,
            # This is required for indirect requirements, but isn't really used
            parent_req_name=(None if requirement.is_direct else "dummy"),
        )
    return condensed_set


def _generate_condensed_requirements(requirements):
    for name, group in util.full_groupby(requirements, key=_get_requirement_key):
        LOG.debug("Condensing requirements for '{}'".format(name))

        condensed_requirement = copy.deepcopy(next(group))

        for requirement in group:
            condensed_requirement.req.specifier &= requirement.req.specifier
            condensed_requirement.constraint &= requirement.constraint
            # Return a sorted, de-duped tuple of extras
            condensed_requirement.extras = tuple(sorted(set(
                tuple(condensed_requirement.extras) + tuple(requirement.extras)
            )))

        LOG.debug("Condensed requirement = {}".format(condensed_requirement))
        yield condensed_requirement


def _get_requirement_key(requirement):
    return pipcompat.canonicalize_name(requirement.name)
