import argparse
import json
import logging
import tempfile

import pip._internal

from piprules import lockfile


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)

    session = pip._internal.download.PipSession()
    finder = pip._internal.index.PackageFinder(
        find_links=[],
        index_urls=[args.index_url],
        session=session,
        prefer_binary=True,
    )

    requirement_set = pip._internal.req.RequirementSet()

    for requirement in _parse_requirements(args.requirements_files, session):
        print("parsed requirement: {}".format(requirement))
        requirement.is_direct = True
        requirement_set.add_requirement(requirement)

    print(repr(requirement_set))

    lock_file = lockfile.LockFile()
    locked_requirements = lock_file.requirements

    with pip._internal.req.req_tracker.RequirementTracker() as requirement_tracker:
        with tempfile.TemporaryDirectory() as temp_dir:
            preparer = pip._internal.operations.prepare.RequirementPreparer(
                build_dir=temp_dir,
                src_dir=temp_dir,
                download_dir=None,
                wheel_download_dir=args.wheel_dir,
                req_tracker=requirement_tracker,
                progress_bar="off",
                build_isolation=True,
            )
            resolver = pip._internal.resolve.Resolver(
                preparer=preparer,
                finder=finder,
                session=session,
                ignore_installed=True,
                wheel_cache=None,
                use_user_site=False,
                ignore_dependencies=False,
                ignore_requires_python=True,
                force_reinstall=False,
                isolated=True,
                upgrade_strategy="to-satisfy-only",
            )
            resolver.resolve(requirement_set)

            print(repr(requirement_set))

            for requirement in requirement_set.requirements.values():
                print(requirement.name)
                print(requirement.link)
                print(requirement.link.hash_name)
                print(requirement.link.hash)
                print(requirement.specifier)
                abstract_dist = pip._internal.operations.prepare.make_abstract_dist(
                    requirement
                )
                dist = abstract_dist.dist()
                print('\n')

                locked_requirement = lock_file.get_requirement(dist.project_name)
                locked_requirement.version = dist.version
                locked_requirement.is_direct = requirement.is_direct

                for dep in dist.requires():
                    locked_dep = locked_requirement.get_dependency(dep.name)

                link = requirement.link
                source = locked_requirement.get_source(link.url_without_fragment)
                # TODO this assumes the hash is sha256
                source.sha256 = link.hash

    print(lock_file.to_json())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--python-version",
        type=int,
        choices=[2, 3],
        action="append",
    )
    parser.add_argument(
        "-P", "--platform",
        action="append",
    )
    parser.add_argument(
        "-l", "--lock-file",
    )
    parser.add_argument(
        "-i", "--index-url",
        default="https://pypi.org/simple",
    )
    parser.add_argument(
        "-w", "--wheel-dir",
        default="wheels",
    )
    parser.add_argument(
        "requirements_files",
        nargs="*",
    )
    return parser.parse_args()


def _parse_requirements(requirements_files, session):
    for path in requirements_files:
        for requirement in pip._internal.req.parse_requirements(path, session=session):
            yield requirement


if __name__ == "__main__":
    main()
