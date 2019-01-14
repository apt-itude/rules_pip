import argparse

from piprules import bazel, wheels


def main():
    args, extra_args = parse_args()
    wheels.download(args.repository_directory, args.requirements, *extra_args)
    unpack_wheels_into_bazel_packages(args.repository_directory)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("repository_directory")
    parser.add_argument("requirements")

    return parser.parse_known_args()


def unpack_wheels_into_bazel_packages(repository_directory):
    for wheel_path in wheels.find_all(repository_directory):
        distribution = wheels.unpack(wheel_path, repository_directory)
        bazel.generate_package_for_python_distribution(distribution)


if __name__ == "__main__":
    main()
