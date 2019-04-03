import argparse
import json
import logging

from piprules import lockfile, pipcompat, resolve, update


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG)
    pipcompat.LOG.setLevel(logging.INFO)

    session = pipcompat.PipSession()

    lock_file = lockfile.load(args.lock_file or '')

    updater = update.Updater(session, lock_file, args.requirements_files)

    resolver_factory = resolve.ResolverFactory([args.index_url], args.wheel_dir)
    with resolver_factory.make_resolver(session) as resolver:
        updater.update(resolver)

    if args.lock_file:
        lock_file.dump(args.lock_file)
    else:
        print(lock_file.to_json())


def parse_args():
    parser = argparse.ArgumentParser()
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


if __name__ == "__main__":
    main()
