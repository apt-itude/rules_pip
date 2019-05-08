import argparse
import logging
import os
import sys

from piprules import lockfile, pipcompat, requirements, resolve


LOG = logging.getLogger()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG)
    pipcompat.LOG.setLevel(logging.INFO)

    workspace_directory = get_workspace_directory()
    lock_file_path = os.path.join(workspace_directory, args.lock_file_path)
    wheel_directory = os.path.join(workspace_directory, args.wheel_dir)

    LOG.info("Locking pip requirements for Python %s", sys.version_info.major)

    pip_session = pipcompat.PipSession()

    lock_file = lockfile.load(lock_file_path or '')

    requirement_set = requirements.collect_and_condense(
        pip_session,
        lock_file,
        args.requirements_files,
        update_all=args.update_all,
        packages_to_update=args.packages_to_update,
    )

    resolved_requirements = resolve.resolve_requirement_set(
        requirement_set,
        pip_session,
        [args.index_url],
        wheel_directory,
    )

    lock_file.update_requirements_for_current_environment(resolved_requirements)

    # TODO raise error if wheel dir changes?
    # Set this to the wheel dir relative to the WORKSPACE root so it doesn't include any
    # parts of the path custom to the current environment
    lock_file.wheel_directory = args.wheel_dir

    if lock_file_path:
        lock_file.dump(lock_file_path)
    else:
        print(lock_file.to_json())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--lock-file",
        dest="lock_file_path",
    )
    parser.add_argument(
        "-U", "--update",
        action="store_true",
        dest="update_all",
    )
    parser.add_argument(
        "-P", "--update-package",
        action="append",
        dest="packages_to_update",
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


def get_workspace_directory():
    try:
        return os.environ["BUILD_WORKSPACE_DIRECTORY"]
    except KeyError:
        sys.exit("This tool must by executed via 'bazel run'")


if __name__ == "__main__":
    main()
