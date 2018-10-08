import os
import subprocess
import sys


def execute_python_module(module_name, *args):
    subprocess.check_call([sys.executable, "-m", module_name] + list(args))


def normalize_distribution_name(name):
    return name.lower().replace("-", "_")


def get_path_stem(path):
    return os.path.splitext(os.path.basename(path))[0]
