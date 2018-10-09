import os


def normalize_distribution_name(name):
    return name.lower().replace("-", "_")


def get_path_stem(path):
    return os.path.splitext(os.path.basename(path))[0]
