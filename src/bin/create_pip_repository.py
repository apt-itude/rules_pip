import argparse

from piprules import bazel, requirements, wheels


def main():
    args = parse_args()
    requirements_file_path = requirements.choose_file(args.requirements)
    wheels.download(args.repository_directory, requirements_file_path)
    unpack_wheels_into_bazel_packages(args.repository_directory)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("repository_directory")
    parser.add_argument("requirements", nargs="+")

    return parser.parse_args()


def unpack_wheels_into_bazel_packages(repository_directory):
    for wheel_path in wheels.find_all(repository_directory):
        distribution = wheels.unpack(wheel_path, repository_directory)
        bazel.create_build_file(distribution)


if __name__ == "__main__":
    main()
