import contextlib
import logging
import os
import shutil
import tempfile

from piprules import pipcompat, util


LOG = logging.getLogger(__name__)


class ResolverFactory(object):

    def __init__(self, index_urls, wheel_dir):
        self.index_urls = index_urls
        self.wheel_dir = wheel_dir

    @contextlib.contextmanager
    def make_resolver(self, session):
        with pipcompat.RequirementTracker() as requirement_tracker:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dirs = _TempDirs(temp_dir)
                finder = self._make_finder(session)
                preparer = self._make_preparer(requirement_tracker, temp_dirs)
                pip_resolver = self._make_pip_resolver(preparer, finder, session)
                wheel_builder = self._make_wheel_builder(finder, preparer)
                yield Resolver(
                    session,
                    pip_resolver,
                    wheel_builder,
                    temp_dirs,
                    self.wheel_dir,
                )

    def _make_finder(self, session):
        return pipcompat.PackageFinder(
            find_links=[],
            index_urls=self.index_urls,
            session=session,
            prefer_binary=True,
        )

    def _make_preparer(self, requirement_tracker, temp_dirs):
        return pipcompat.RequirementPreparer(
            build_dir=temp_dirs.build,
            src_dir=temp_dirs.src,
            download_dir=None,
            wheel_download_dir=temp_dirs.wheel,
            req_tracker=requirement_tracker,
            progress_bar="off",
            build_isolation=True,
        )

    def _make_pip_resolver(self, preparer, finder, session):
        return pipcompat.Resolver(
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

    def _make_wheel_builder(self, finder, preparer):
        return pipcompat.WheelBuilder(
            finder,
            preparer,
            None,
            build_options=[],
            global_options=[],
            no_clean=True,
        )


class _TempDirs(object):

    def __init__(self, directory):
        self.directory = directory

    @property
    def build(self):
        return os.path.join(self.directory, "build")

    @property
    def src(self):
        return os.path.join(self.directory, "src")

    @property
    def wheel(self):
        return os.path.join(self.directory, "wheel")


class Resolver(object):

    def __init__(self, session, pip_resolver, wheel_builder, temp_dirs, wheel_dir):
        self._session = session
        self._pip_resolver = pip_resolver
        self._wheel_builder = wheel_builder
        self._temp_dirs = temp_dirs
        self._wheel_dir = wheel_dir

    def resolve(self, requirement_set):
        self._pip_resolver.resolve(requirement_set)

        build_failures = self._wheel_builder.build(
            requirement_set.requirements.values(),
            session=self._session,
        )
        if build_failures:
            # TODO better error
            raise RuntimeError('Failed to build one or more wheels')

        for requirement in requirement_set.requirements.values():
            if not requirement.link.is_wheel:
                temp_wheel_path = _find_wheel(self._temp_dirs.wheel, requirement.name)
                wheel_path = _copy_file(temp_wheel_path, self._wheel_dir)
                url = pipcompat.path_to_url(wheel_path)

                LOG.debug("Setting source of {} to {}".format(
                    requirement.name,
                    url,
                ))
                requirement.link = pipcompat.Link(url, comes_from="local")

                # This is necessary for the make_abstract_dist step when updating the
                # lock file
                requirement.ensure_has_source_dir(self._temp_dirs.build)
                pipcompat.unpack_url(
                    requirement.link,
                    requirement.source_dir,
                    None,
                    False,
                    session=self._session,
                )

        return requirement_set


def _find_wheel(directory, name):
    canon_name = pipcompat.canonicalize_name(name)
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            try:
                wheel = pipcompat.Wheel(filename)
            except pipcompat.InvalidWheelFilename:
                continue
            if pipcompat.canonicalize_name(wheel.name) == canon_name:
                return path

    raise RuntimeError('Could not find wheel matching name "{}"'.format(name))


def _copy_file(source_path, directory):
    util.ensure_directory_exists(directory)
    base_name = os.path.basename(source_path)
    dest_path = os.path.join(directory, base_name)
    shutil.copy(source_path, dest_path)
    return dest_path