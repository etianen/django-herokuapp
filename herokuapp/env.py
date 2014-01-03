import os, os.path


def parse_env(line_iter):
    return dict(
        line.split("=", 1)
        for line
        in line_iter
    )


def load_env(cwd):
    env_path = os.path.join(cwd, ".env")
    if os.path.exists(env_path):
        with open(env_path, "rb") as env_handle:
            os.environ.update(parse_env(env_handle))
