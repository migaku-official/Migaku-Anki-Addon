import atexit
import os
import shutil
import tempfile
from contextlib import contextmanager


temp_dir = tempfile.mkdtemp(prefix="migaku-anki-addon-")


def tmp_path(*path_parts):
    os.makedirs(temp_dir, exist_ok=True)
    return os.path.join(temp_dir, *path_parts)


@contextmanager
def temporary_workspace():
    os.makedirs(temp_dir, exist_ok=True)
    workspace = tempfile.mkdtemp(prefix="operation-", dir=temp_dir)
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def publish_file_atomically(source, destination):
    destination_directory = os.path.dirname(destination) or "."
    file_descriptor, staging_path = tempfile.mkstemp(
        prefix=".migaku-media-", dir=destination_directory
    )
    os.close(file_descriptor)
    try:
        shutil.copyfile(source, staging_path)
        os.replace(staging_path, destination)
    finally:
        try:
            os.remove(staging_path)
        except OSError:
            pass


def cleanup():
    shutil.rmtree(temp_dir, ignore_errors=True)


atexit.register(cleanup)
