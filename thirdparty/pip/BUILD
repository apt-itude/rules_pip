load("//rules:lock.bzl", "pip_lock")

exports_files([
    "requirements-lock.json",
    "requirements.in",
])

pip_lock(
    name = "lock",
    requirements = [":requirements.in"],
    requirements_lock = "requirements-lock-new.json",
)
