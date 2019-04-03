import logging

from piprules import pipcompat


LOG = logging.getLogger(__name__)


def update_lock_file(lock_file, requirements):
    for requirement in requirements:
        canon_requirement_name = pipcompat.canonicalize_name(requirement.name)
        LOG.debug("Updating entry in lock file for %s", canon_requirement_name)

        abstract_dist = pipcompat.make_abstract_dist(requirement)
        dist = abstract_dist.dist()

        locked_requirement = lock_file.get_requirement(canon_requirement_name)
        locked_requirement.version = dist.version
        locked_requirement.is_direct = requirement.is_direct

        for dep in dist.requires():
            canon_dep_name = pipcompat.canonicalize_name(dep.name)
            locked_dep = locked_requirement.get_dependency(canon_dep_name)

        link = requirement.link
        source = locked_requirement.get_source(link.url_without_fragment)
        source.is_local = link.comes_from == "local"

        if link.hash:
            # TODO this assumes the hash is sha256
            source.sha256 = link.hash
