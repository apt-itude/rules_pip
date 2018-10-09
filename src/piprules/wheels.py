import glob
import os
import pkg_resources

from pip._internal import main as pip_main
from wheel import wheelfile

from piprules import util


class Error(Exception):

    """Base exception for the wheels module"""


def download(dest_directory, requirements_file_path):
    pip_main(args=["wheel", "-w", dest_directory, "-r", requirements_file_path])


def find_all(directory):
    for matching_path in glob.glob("{}/*.whl".format(directory)):
        yield matching_path


def unpack(wheel_path, dest_directory):
    # TODO(): don't use unsupported wheel library
    with wheelfile.WheelFile(wheel_path) as wheel_file:
        distribution_name = wheel_file.parsed_filename.group("name")
        library_name = util.normalize_distribution_name(distribution_name)
        package_directory = os.path.join(dest_directory, library_name)
        wheel_file.extractall(package_directory)

    try:
        return next(pkg_resources.find_distributions(package_directory))
    except StopIteration:
        raise DistributionNotFoundError(package_directory)


class DistributionNotFoundError(Error):

    def __init__(self, package_directory):
        super(DistributionNotFoundError, self).__init__()
        self.package_directory = package_directory

    def __str__(self):
        return "Could not find in Python distribution in directory {}".format(
            self.package_directory
        )
