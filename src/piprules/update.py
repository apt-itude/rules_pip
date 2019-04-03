import logging

from piprules import pipcompat


LOG = logging.getLogger(__name__)


def update_lock_file(lock_file, requirements):
    for requirement in requirements:
        LOG.debug("Updating entry in lock file for %s", requirement.name)

        abstract_dist = pipcompat.make_abstract_dist(requirement)
        dist = abstract_dist.dist()

        locked_requirement = lock_file.get_requirement(dist.project_name)
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
