import contextlib
import logging
import os
import shutil
import tempfile

from piprules import lockfile, pipcompat, util


LOG = logging.getLogger(__name__)


def resolve_requirement_set(requirement_set, pip_session, index_urls, wheel_dir):
    resolver_factory = ResolverFactory(pip_session, index_urls, wheel_dir)

    with resolver_factory.make_resolver() as resolver:
        return resolver.resolve(requirement_set)


class ResolverFactory(object):

    def __init__(self, pip_session, index_urls, wheel_dir):
        self.pip_session = pip_session
        self.index_urls = index_urls
        self.wheel_dir = wheel_dir

    @contextlib.contextmanager
    def make_resolver(self):
        with pipcompat.RequirementTracker() as requirement_tracker:
            with _WorkDirs(tempfile.mkdtemp()) as work_dirs:
                finder = self._make_finder()
                preparer = self._make_preparer(requirement_tracker, work_dirs)
                pip_resolver = self._make_pip_resolver(finder, preparer)
                wheel_builder = self._make_wheel_builder(finder, preparer)

                yield Resolver(
                    self.pip_session,
                    pip_resolver,
                    wheel_builder,
                    work_dirs,
                    self.wheel_dir,
                )

    def _make_finder(self):
        return pipcompat.PackageFinder(
            find_links=[],
            index_urls=self.index_urls,
            session=self.pip_session,
            prefer_binary=True,
        )

    def _make_preparer(self, requirement_tracker, work_dirs):
        return pipcompat.RequirementPreparer(
            build_dir=work_dirs.build,
            src_dir=work_dirs.src,
            download_dir=None,
            wheel_download_dir=work_dirs.wheel,
            req_tracker=requirement_tracker,
            progress_bar="off",
            build_isolation=True,
        )

    def _make_pip_resolver(self, finder, preparer):
        return pipcompat.Resolver(
            finder=finder,
            preparer=preparer,
            session=self.pip_session,
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


class _WorkDirs(object):

    def __init__(self, base):
        self.base = base

    @property
    def build(self):
        return os.path.join(self.base, "build")

    @property
    def src(self):
        return os.path.join(self.base, "src")

    @property
    def wheel(self):
        return os.path.join(self.base, "wheel")

    def __enter__(self):
        self.create_all()
        return self

    def create_all(self):
        util.ensure_directory_exists(self.build)
        util.ensure_directory_exists(self.src)
        util.ensure_directory_exists(self.wheel)

    def __exit__(self, *args, **kwargs):
        self.delete_all()

    def delete_all(self):
        shutil.rmtree(self.base)


class Resolver(object):

    def __init__(self, session, pip_resolver, wheel_builder, work_dirs, wheel_dir):
        self._session = session
        self._pip_resolver = pip_resolver
        self._wheel_builder = wheel_builder
        self._work_dirs = work_dirs
        self._wheel_dir = wheel_dir

    def resolve(self, requirement_set):
        self._pip_resolver.resolve(requirement_set)

        requirements = requirement_set.requirements.values()

        self._build_wheels_if_necessary(requirements)

        return {
            name: locked_requirement
            for name, locked_requirement
            in self._generate_locked_requirements(requirements)
        }

    def _build_wheels_if_necessary(self, requirements):
        build_failures = self._wheel_builder.build(
            requirements,
            session=self._session,
        )
        if build_failures:
            # TODO raise better error
            raise RuntimeError('Failed to build one or more wheels')

    def _generate_locked_requirements(self, requirements):
        for requirement in requirements:
            name = pipcompat.canonicalize_name(requirement.name)
            locked_requirement = self._create_locked_requirement(requirement)
            yield name, locked_requirement

    def _create_locked_requirement(self, requirement):
        use_local_wheel_source = not requirement.link.is_wheel

        if use_local_wheel_source:
            self._set_link_to_local_wheel(requirement)

        abstract_dist = pipcompat.make_abstract_dist(requirement)
        dist = abstract_dist.dist()

        locked_requirement = lockfile.Requirement()
        locked_requirement.version = dist.version
        locked_requirement.is_direct = requirement.is_direct

        for dep in dist.requires():
            canon_dep_name = pipcompat.canonicalize_name(dep.name)
            locked_dep = locked_requirement.get_dependency(canon_dep_name)
            locked_dep.add_current_environment()

        link = requirement.link
        source = locked_requirement.get_source(link.url_without_fragment)
        source.is_local = use_local_wheel_source
        source.add_current_environment()

        if link.hash:
            # TODO this assumes the hash is sha256
            source.sha256 = link.hash

        return locked_requirement

    def _set_link_to_local_wheel(self, requirement):
        temp_wheel_path = _find_wheel(self._work_dirs.wheel, requirement.name)
        wheel_path = _copy_file(temp_wheel_path, self._wheel_dir)
        url = pipcompat.path_to_url(wheel_path)

        LOG.debug("Setting source of %s to %s", requirement.name, url)
        requirement.link = pipcompat.Link(url, comes_from=wheel_path)

        # This is necessary for the make_abstract_dist step, which relies on an
        # unpacked wheel that looks like an installed distribution
        requirement.ensure_has_source_dir(self._work_dirs.build)
        pipcompat.unpack_url(
            requirement.link,
            requirement.source_dir,
            None,
            False,
            session=self._session,
        )


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

    # TODO raise better error
    raise RuntimeError('Could not find wheel matching name "{}"'.format(name))


def _copy_file(source_path, directory):
    util.ensure_directory_exists(directory)
    base_name = os.path.basename(source_path)
    dest_path = os.path.join(directory, base_name)
    shutil.copy(source_path, dest_path)
    return dest_path
